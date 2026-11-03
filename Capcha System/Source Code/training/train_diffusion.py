"""DDPM-style training and sampling for the conditional U-Net."""
import copy
import math
import os
import time

import torch
import torch.nn.functional as F

from utils.checkpoint import save_checkpoint


# ----------------------------------------------------------------- noise schedules
def linear_beta_schedule(timesteps: int, beta_start: float = 1e-4, beta_end: float = 0.02) -> torch.Tensor:
    """Linear beta schedule (Ho et al., 2020). Returns (T,) tensor."""
    return torch.linspace(beta_start, beta_end, timesteps)


def cosine_beta_schedule(timesteps: int, s: float = 0.008) -> torch.Tensor:
    """Cosine schedule (Nichol & Dhariwal, 2021). Returns (T,) tensor."""
    x = torch.linspace(0, timesteps, timesteps + 1, dtype=torch.float64)
    alphas_cumprod = torch.cos(((x / timesteps) + s) / (1 + s) * math.pi / 2) ** 2
    alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
    betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
    return betas.clamp(1e-4, 0.999).float()


def get_beta_schedule(name: str, timesteps: int) -> torch.Tensor:
    if name == "linear":
        return linear_beta_schedule(timesteps)
    if name == "cosine":
        return cosine_beta_schedule(timesteps)
    raise ValueError(f"Unknown schedule '{name}' (use 'linear' or 'cosine')")


# ----------------------------------------------------------------- forward process
def q_sample(x0: torch.Tensor, t: torch.Tensor, noise: torch.Tensor, alphas_cumprod: torch.Tensor) -> torch.Tensor:
    """Forward diffusion: x_t = sqrt(abar_t) * x_0 + sqrt(1 - abar_t) * eps."""
    abar = alphas_cumprod.to(x0.device)[t].view(-1, 1, 1, 1)
    return abar.sqrt() * x0 + (1.0 - abar).sqrt() * noise


# ----------------------------------------------------------------- training
def train_diffusion(model, dataloader, epochs, device, timesteps=1000, schedule="linear", lr=2e-4,
                    ema_decay=0.999, checkpoint_dir=None, save_every=10, checkpoint_name="diffusion",
                    epoch_callback=None):
    """Train the noise-prediction network with the simple DDPM objective.

    For every batch: sample t ~ U{0..T-1}, eps ~ N(0, I), build x_t with ``q_sample`` and minimise
    MSE(eps_theta(x_t, t, y), eps). An EMA copy of the weights is kept for better samples.

    Returns:
        history (dict with ``loss`` per epoch), ema_model (use this one for sampling).
    """
    model.to(device).train()
    ema_model = copy.deepcopy(model).eval() if ema_decay else None
    betas = get_beta_schedule(schedule, timesteps)
    alphas_cumprod = torch.cumprod(1.0 - betas, dim=0).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    history = {"loss": []}
    config = {"timesteps": timesteps, "schedule": schedule, "lr": lr, "epochs": epochs, "ema_decay": ema_decay}

    for epoch in range(1, epochs + 1):
        t0, total, n = time.time(), 0.0, 0
        for x0, y in dataloader:
            x0, y = x0.to(device), y.to(device)
            t = torch.randint(0, timesteps, (x0.size(0),), device=device)   # random step per image
            noise = torch.randn_like(x0)
            x_t = q_sample(x0, t, noise, alphas_cumprod)                     # forward diffusion (add noise)

            pred_noise = model(x_t, t, y)
            loss = F.mse_loss(pred_noise, noise)                             # MSE noise-prediction loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            if ema_model is not None:
                with torch.no_grad():
                    for p_ema, p in zip(ema_model.parameters(), model.parameters()):
                        p_ema.mul_(ema_decay).add_(p.detach(), alpha=1 - ema_decay)
                    for b_ema, b in zip(ema_model.buffers(), model.buffers()):
                        b_ema.copy_(b)
            total += loss.item(); n += 1

        history["loss"].append(total / max(n, 1))
        print(f"[Diffusion-{schedule}] epoch {epoch:3d}/{epochs} | MSE loss {history['loss'][-1]:.5f} | {time.time() - t0:.1f}s")

        if checkpoint_dir is not None and (epoch % save_every == 0 or epoch == epochs):
            models = {"model": model}
            if ema_model is not None:
                models["ema_model"] = ema_model
            fname = f"{checkpoint_name}_final.pt" if epoch == epochs else f"{checkpoint_name}_epoch{epoch}.pt"
            save_checkpoint(os.path.join(checkpoint_dir, fname), models, {"optimizer": optimizer},
                            epoch=epoch, history=history, config=config)
        if epoch_callback is not None:
            epoch_callback(epoch, ema_model if ema_model is not None else model)
    return history, (ema_model if ema_model is not None else model)


# ----------------------------------------------------------------- reverse process
@torch.no_grad()
def sample_images(model, labels, betas, device, num_inference_steps=None, img_size=28, channels=1):
    """Reverse diffusion (ancestral DDPM sampling) from t = T-1 down to 0.

    Args:
        model: trained ConditionalUNet (ideally the EMA copy).
        labels: (N,) long tensor with the class to generate per image.
        betas: (T,) beta schedule used for training.
        num_inference_steps: number of denoising steps K <= T. ``None`` -> use all T steps. If K < T the
            chain is *re-spaced* (Nichol & Dhariwal, 2021): K evenly spaced timesteps are kept and the
            betas are recomputed from the cumulative alphas, so the same network can sample faster.
    Returns:
        (N, 1, 28, 28) tensor clamped to [-1, 1].
    """
    model.to(device).eval()
    labels = labels.to(device)
    T = len(betas)
    K = T if num_inference_steps is None else int(num_inference_steps)
    alphas_cumprod = torch.cumprod(1.0 - betas.to(device).double(), dim=0)

    # chosen training timesteps, ascending (e.g. K=T -> 0..T-1)
    steps = torch.linspace(0, T - 1, K, device=device).round().long()
    abar = alphas_cumprod[steps]                                          # (K,)
    abar_prev = torch.cat([torch.ones(1, device=device, dtype=abar.dtype), abar[:-1]])
    alpha_k = abar / abar_prev                                            # effective alpha for each kept step
    beta_k = 1.0 - alpha_k
    posterior_var = beta_k * (1.0 - abar_prev) / (1.0 - abar)

    x = torch.randn(len(labels), channels, img_size, img_size, device=device)   # x_T ~ N(0, I)
    for i in reversed(range(K)):                                                # T-1 ... 0
        t = torch.full((len(labels),), int(steps[i]), device=device, dtype=torch.long)
        eps = model(x, t, labels)
        coef = (beta_k[i] / (1.0 - abar[i]).sqrt()).float()
        mean = (x - coef * eps) / alpha_k[i].sqrt().float()
        if i > 0:
            x = mean + posterior_var[i].sqrt().float() * torch.randn_like(x)
        else:
            x = mean                                                            # no noise at the last step
    return x.clamp(-1.0, 1.0)
