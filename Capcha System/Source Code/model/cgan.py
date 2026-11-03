"""Conditional GAN (cGAN) for 28x28 MNIST digits.

Conditioning strategy
---------------------
* Generator  : concatenate the latent vector ``z`` with a learned class embedding.
* Discriminator: embed the label into a full 1x28x28 "label map" and concatenate it
  with the image along the channel axis (2 x 28 x 28 input).
"""
import torch
import torch.nn as nn

IMG_SIZE = 28


def weights_init(m: nn.Module) -> None:
    """DCGAN-style weight initialisation."""
    name = m.__class__.__name__
    if "Conv" in name or "Linear" in name:
        nn.init.normal_(m.weight, 0.0, 0.02)
        if m.bias is not None:
            nn.init.zeros_(m.bias)
    elif "BatchNorm" in name or "GroupNorm" in name:
        nn.init.normal_(m.weight, 1.0, 0.02)
        nn.init.zeros_(m.bias)


class Generator(nn.Module):
    """G(z, y) -> image of shape (B, 1, 28, 28) with values in [-1, 1] (Tanh)."""

    def __init__(self, latent_dim: int = 100, num_classes: int = 10, embed_dim: int = 50, base_channels: int = 64):
        super().__init__()
        self.latent_dim = latent_dim
        self.num_classes = num_classes
        self.base_channels = base_channels

        # Class label -> dense embedding
        self.label_emb = nn.Embedding(num_classes, embed_dim)

        # (z ++ embedding) -> 2*C x 7 x 7 feature map.
        # GroupNorm (not BatchNorm) is used on purpose: it behaves identically in train() and eval(), so the
        # generator cannot rely on batch statistics (which made samples collapse in eval mode).
        self.project = nn.Linear(latent_dim + embed_dim, base_channels * 2 * 7 * 7, bias=False)
        self.net = nn.Sequential(
            nn.GroupNorm(8, base_channels * 2),
            nn.ReLU(True),
            # 7x7 -> 14x14
            nn.ConvTranspose2d(base_channels * 2, base_channels, 4, 2, 1, bias=False),
            nn.GroupNorm(8, base_channels),
            nn.ReLU(True),
            # 14x14 -> 28x28 ; single channel output
            nn.ConvTranspose2d(base_channels, 1, 4, 2, 1),
            nn.Tanh(),  # output range [-1, 1]
        )
        self.apply(weights_init)

    def forward(self, z: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        # z: (B, latent_dim), labels: (B,) int64
        emb = self.label_emb(labels)                  # (B, embed_dim)
        x = torch.cat([z, emb], dim=1)                # label conditioning (concatenation)
        x = self.project(x)                           # (B, 2C*7*7)
        x = x.view(-1, self.base_channels * 2, 7, 7)  # reshape to a feature map
        img = self.net(x)                             # (B, 1, 28, 28)
        return img


class Discriminator(nn.Module):
    """D(x, y) -> probability in (0, 1) that x is a real image of class y. Output shape (B,)."""

    def __init__(self, num_classes: int = 10, base_channels: int = 64, dropout: float = 0.3):
        super().__init__()
        self.num_classes = num_classes
        # label -> 784-dim vector, reshaped into a 1x28x28 map
        self.label_emb = nn.Embedding(num_classes, IMG_SIZE * IMG_SIZE)

        self.net = nn.Sequential(
            nn.Conv2d(2, base_channels, 4, 2, 1),                       # 28 -> 14
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout2d(dropout),
            nn.Conv2d(base_channels, base_channels * 2, 4, 2, 1, bias=False),  # 14 -> 7
            nn.GroupNorm(8, base_channels * 2),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout2d(dropout),
        )
        self.classifier = nn.Sequential(
            nn.Linear(base_channels * 2 * 7 * 7, 1),
            nn.Sigmoid(),
        )
        self.apply(weights_init)

    def forward(self, img: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        # accept flat (B, 784) or image (B, 1, 28, 28) inputs
        img = img.view(-1, 1, IMG_SIZE, IMG_SIZE)
        label_map = self.label_emb(labels).view(-1, 1, IMG_SIZE, IMG_SIZE)
        x = torch.cat([img, label_map], dim=1)        # label conditioning (channel concat)
        h = self.net(x)
        h = h.flatten(start_dim=1)
        return self.classifier(h).view(-1)            # (B,)
