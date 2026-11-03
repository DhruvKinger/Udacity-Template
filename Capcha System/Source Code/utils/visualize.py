"""Plotting helpers for batches of images, class grids, comparisons, interpolations and CAPTCHAs."""
import matplotlib.pyplot as plt
import torch
import torchvision.transforms.functional as TF
from torchvision.utils import make_grid


def denormalize(x: torch.Tensor) -> torch.Tensor:
    """[-1, 1] -> [0, 1]."""
    return ((x.detach().cpu() + 1) / 2).clamp(0, 1)


def _show(grid, title=None, figsize=(8, 8), save_path=None, ax=None):
    own = ax is None
    if own:
        _, ax = plt.subplots(figsize=figsize)
    ax.imshow(grid.permute(1, 2, 0).numpy(), cmap="gray")
    ax.axis("off")
    if title:
        ax.set_title(title)
    if own:
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()


def show_images(images, nrow=8, title=None, save_path=None, figsize=(8, 8)):
    """Plot a batch of images in [-1, 1] as a grid."""
    grid = make_grid(denormalize(images), nrow=nrow, padding=2, pad_value=1.0)
    _show(grid, title, figsize, save_path)


def show_class_grid(images, labels, num_classes=10, per_class=10, title=None, save_path=None):
    """One row per digit class: ``per_class`` samples of each class from (images, labels)."""
    rows = []
    for c in range(num_classes):
        x = images[labels == c][:per_class]
        if len(x) < per_class:  # pad if too few samples
            x = torch.cat([x, -torch.ones(per_class - len(x), *images.shape[1:])])
        rows.append(x)
    grid = make_grid(denormalize(torch.cat(rows)), nrow=per_class, padding=2, pad_value=1.0)
    _show(grid, title, (per_class * 0.9, num_classes * 0.9 + 0.5), save_path)


def compare_real_vs_generated(real, real_labels, cgan, cgan_labels, diffusion, diffusion_labels,
                              digits=range(10), n_per_digit=8, save_path=None):
    """Side-by-side "Real vs cGAN vs Diffusion" figure: one row per digit, three columns."""
    digits = list(digits)
    fig, axes = plt.subplots(len(digits), 3, figsize=(12, 1.15 * len(digits) + 0.8))
    axes = axes.reshape(len(digits), 3)
    for r, d in enumerate(digits):
        for col, (imgs, labs) in enumerate([(real, real_labels), (cgan, cgan_labels), (diffusion, diffusion_labels)]):
            strip = make_grid(denormalize(imgs[labs == d][:n_per_digit]), nrow=n_per_digit, padding=1, pad_value=1.0)
            _show(strip, ax=axes[r, col])
            if r == 0:
                axes[r, col].set_title(["Real MNIST", "cGAN", "Diffusion"][col], fontsize=13, fontweight="bold")
        axes[r, 0].text(-0.02, 0.5, f"digit {d}", transform=axes[r, 0].transAxes, ha="right", va="center", fontsize=11)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_losses(history, title="Training losses", save_path=None):
    """Line plot of every list stored in a history dict (e.g. g_loss / d_loss)."""
    plt.figure(figsize=(7, 4))
    for k, v in history.items():
        plt.plot(range(1, len(v) + 1), v, label=k)
    plt.xlabel("epoch"); plt.title(title); plt.legend(); plt.grid(alpha=0.3)
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def show_interpolation(images, title=None, save_path=None):
    """images: (rows, steps, 1, 28, 28) or (steps, 1, 28, 28) -> grid with one interpolation walk per row."""
    if images.dim() == 4:
        images = images.unsqueeze(0)
    rows, steps = images.shape[:2]
    grid = make_grid(denormalize(images.flatten(0, 1)), nrow=steps, padding=2, pad_value=1.0)
    _show(grid, title, (steps * 0.9, rows * 0.9 + 0.5), save_path)


@torch.no_grad()
def make_captcha(text, sample_fn, height=56, spacing=(-4, 2), max_rotation=15, noise_lines=4, seed=None):
    """Compose a multi-digit CAPTCHA from single-digit samples.

    Args:
        text: string of digits, e.g. "4821".
        sample_fn: callable ``digit(int) -> tensor (1, 28, 28)`` in [-1, 1] (wraps cGAN or diffusion model).
        Random rotation, vertical jitter, spacing and distractor lines make segmentation harder for bots.
    Returns:
        (height, width) float tensor in [0, 1] (1 = white background, dark ink).
    """
    g = torch.Generator().manual_seed(seed) if seed is not None else None
    rnd = lambda lo, hi: lo + (hi - lo) * torch.rand(1, generator=g).item()
    glyphs, widths = [], []
    for ch in text:
        img = denormalize(sample_fn(int(ch))).squeeze(0)                      # (28, 28), ink = bright
        img = 1.0 - img                                                       # dark ink on white
        img = TF.rotate(img.unsqueeze(0), rnd(-max_rotation, max_rotation), fill=[1.0]).squeeze(0)
        glyphs.append(img)
    width = 8 + sum(28 + int(rnd(*spacing)) for _ in glyphs) + 8
    canvas = torch.ones(height, width)
    x = 8
    for img in glyphs:
        y = int(rnd(0, height - 28))
        patch = canvas[y:y + 28, x:x + 28]
        canvas[y:y + 28, x:x + 28] = torch.minimum(patch, img[:patch.shape[0], :patch.shape[1]])
        x += 28 + int(rnd(*spacing))
    for _ in range(noise_lines):                                              # distractor strokes
        y0, y1 = int(rnd(0, height)), int(rnd(0, height))
        for xi in range(width):
            yi = int(y0 + (y1 - y0) * xi / max(width - 1, 1))
            if 0 <= yi < height:
                canvas[yi, xi] = min(canvas[yi, xi].item(), 0.35)
    return canvas


def show_captchas(captchas, titles=None, save_path=None):
    """Display a list of (H, W) captcha tensors stacked vertically."""
    fig, axes = plt.subplots(len(captchas), 1, figsize=(5, 1.6 * len(captchas)))
    axes = [axes] if len(captchas) == 1 else axes
    for i, (ax, c) in enumerate(zip(axes, captchas)):
        ax.imshow(c.numpy(), cmap="gray", vmin=0, vmax=1); ax.axis("off")
        if titles:
            ax.set_title(titles[i], fontsize=9)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


# Alias matching the name used in the starter notebooks
show_batch = show_images
