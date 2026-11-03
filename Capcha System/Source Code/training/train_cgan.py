"""Adversarial training loop for the conditional GAN (standard minimax / BCE objective)."""
import os
import time

import torch
import torch.nn as nn

from utils.checkpoint import save_checkpoint


def train_cgan(generator, discriminator, dataloader, epochs, device, latent_dim=100, num_classes=10,
               lr=2e-4, betas=(0.5, 0.999), criterion=None, real_label=1.0,
               checkpoint_dir=None, save_every=10, checkpoint_name="cgan", epoch_callback=None):
    """Train a cGAN.

    Per batch:
      1. Discriminator step: BCE on real (target 1) and fake (target 0) pairs, averaged.
      2. Generator step   : non-saturating loss, i.e. BCE(D(G(z, y), y), 1).

    Returns a history dict with per-epoch ``g_loss``, ``d_loss``, ``d_real`` (mean D(x,y)) and ``d_fake``.
    """
    criterion = criterion if criterion is not None else nn.BCELoss()
    generator.to(device).train()
    discriminator.to(device).train()
    g_opt = torch.optim.Adam(generator.parameters(), lr=lr, betas=betas)
    d_opt = torch.optim.Adam(discriminator.parameters(), lr=lr, betas=betas)
    history = {"g_loss": [], "d_loss": [], "d_real": [], "d_fake": []}
    config = {"latent_dim": latent_dim, "num_classes": num_classes, "lr": lr, "epochs": epochs}

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        sums = {"g": 0.0, "d": 0.0, "dr": 0.0, "df": 0.0}
        n_batches = 0
        for real_imgs, real_labels in dataloader:
            real_imgs, real_labels = real_imgs.to(device), real_labels.to(device)
            bs = real_imgs.size(0)
            real_target = torch.full((bs,), real_label, device=device)
            fake_target = torch.zeros(bs, device=device)

            # ---------------- Discriminator update ----------------
            d_opt.zero_grad()
            z = torch.randn(bs, latent_dim, device=device)
            fake_labels = torch.randint(0, num_classes, (bs,), device=device)
            with torch.no_grad():
                fake_imgs = generator(z, fake_labels)
            d_real = discriminator(real_imgs, real_labels)
            d_fake = discriminator(fake_imgs, fake_labels)
            loss_real = criterion(d_real, real_target)
            loss_fake = criterion(d_fake, fake_target)
            d_loss = (loss_real + loss_fake) / 2          # average of real and fake loss
            d_loss.backward()
            d_opt.step()

            # ---------------- Generator update ----------------
            g_opt.zero_grad()
            z = torch.randn(bs, latent_dim, device=device)
            gen_labels = torch.randint(0, num_classes, (bs,), device=device)
            gen_imgs = generator(z, gen_labels)
            g_loss = criterion(discriminator(gen_imgs, gen_labels), torch.ones(bs, device=device))
            g_loss.backward()
            g_opt.step()

            sums["g"] += g_loss.item(); sums["d"] += d_loss.item()
            sums["dr"] += d_real.mean().item(); sums["df"] += d_fake.mean().item()
            n_batches += 1

        for k, name in [("g", "g_loss"), ("d", "d_loss"), ("dr", "d_real"), ("df", "d_fake")]:
            history[name].append(sums[k] / max(n_batches, 1))
        print(f"[cGAN] epoch {epoch:3d}/{epochs} | D loss {history['d_loss'][-1]:.4f} | G loss {history['g_loss'][-1]:.4f} "
              f"| D(x) {history['d_real'][-1]:.3f} | D(G(z)) {history['d_fake'][-1]:.3f} | {time.time() - t0:.1f}s")

        if checkpoint_dir is not None and (epoch % save_every == 0 or epoch == epochs):
            save_checkpoint(os.path.join(checkpoint_dir, f"{checkpoint_name}_final.pt" if epoch == epochs
                                         else f"{checkpoint_name}_epoch{epoch}.pt"),
                            {"generator": generator, "discriminator": discriminator},
                            {"g_opt": g_opt, "d_opt": d_opt}, epoch=epoch, history=history, config=config)
        if epoch_callback is not None:
            epoch_callback(epoch, generator)
    return history
