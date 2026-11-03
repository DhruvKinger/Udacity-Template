"""Class-conditional U-Net that predicts the noise added in the forward diffusion process."""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


def timestep_embedding(timesteps: torch.Tensor, dim: int, max_period: int = 10000) -> torch.Tensor:
    """Sinusoidal embedding of integer diffusion steps.

    Args:
        timesteps: (B,) tensor of (integer-valued) steps.
        dim: embedding dimension.
    Returns:
        (B, dim) tensor.
    """
    half = dim // 2
    freqs = torch.exp(-math.log(max_period) * torch.arange(half, device=timesteps.device, dtype=torch.float32) / half)
    args = timesteps.float()[:, None] * freqs[None, :]
    emb = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
    if dim % 2 == 1:
        emb = F.pad(emb, (0, 1))
    return emb


class ResidualBlock(nn.Module):
    """Conv residual block conditioned on a (time + label) embedding vector."""

    def __init__(self, in_channels: int, out_channels: int, emb_dim: int, groups: int = 8):
        super().__init__()
        self.norm1 = nn.GroupNorm(groups, in_channels)
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.emb_proj = nn.Linear(emb_dim, out_channels)
        self.norm2 = nn.GroupNorm(groups, out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.skip = nn.Conv2d(in_channels, out_channels, 1) if in_channels != out_channels else nn.Identity()

    def forward(self, x: torch.Tensor, emb: torch.Tensor) -> torch.Tensor:
        h = self.conv1(F.silu(self.norm1(x)))
        h = h + self.emb_proj(F.silu(emb))[:, :, None, None]   # inject time + class information
        h = self.conv2(F.silu(self.norm2(h)))
        return h + self.skip(x)                                 # residual connection


class ConditionalUNet(nn.Module):
    """eps_theta(x_t, t, y): predicts noise with the same shape as x_t.

    Path:  time/label embedding -> down path -> bottleneck -> up path (with skip
    connections) -> output noise prediction.
    """

    def __init__(self, in_channels: int = 1, base_channels: int = 64, emb_dim: int = 128, num_classes: int = 10):
        super().__init__()
        c = base_channels
        self.emb_dim = emb_dim
        self.num_classes = num_classes

        # time + label embeddings
        self.time_mlp = nn.Sequential(nn.Linear(emb_dim, emb_dim), nn.SiLU(), nn.Linear(emb_dim, emb_dim))
        self.label_emb = nn.Embedding(num_classes, emb_dim)

        self.init_conv = nn.Conv2d(in_channels, c, 3, padding=1)

        # contracting path
        self.down1 = ResidualBlock(c, c, emb_dim)             # 28x28
        self.pool1 = nn.Conv2d(c, c, 3, stride=2, padding=1)  # -> 14x14
        self.down2 = ResidualBlock(c, 2 * c, emb_dim)         # 14x14
        self.pool2 = nn.Conv2d(2 * c, 2 * c, 3, stride=2, padding=1)  # -> 7x7

        # bottleneck
        self.mid1 = ResidualBlock(2 * c, 4 * c, emb_dim)
        self.mid2 = ResidualBlock(4 * c, 4 * c, emb_dim)

        # expansive path
        self.up1 = nn.ConvTranspose2d(4 * c, 2 * c, 4, stride=2, padding=1)  # -> 14x14
        self.dec1 = ResidualBlock(4 * c, 2 * c, emb_dim)                     # concat skip (2c + 2c)
        self.up2 = nn.ConvTranspose2d(2 * c, c, 4, stride=2, padding=1)      # -> 28x28
        self.dec2 = ResidualBlock(2 * c, c, emb_dim)                         # concat skip (c + c)

        self.out = nn.Sequential(nn.GroupNorm(8, c), nn.SiLU(), nn.Conv2d(c, in_channels, 3, padding=1))

    def forward(self, x: torch.Tensor, t: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        # 1) embeddings
        emb = self.time_mlp(timestep_embedding(t, self.emb_dim)) + self.label_emb(y)

        # 2) down path (store skips)
        h = self.init_conv(x)
        s1 = self.down1(h, emb)                     # (B, c, 28, 28)
        s2 = self.down2(self.pool1(s1), emb)        # (B, 2c, 14, 14)
        h = self.pool2(s2)                          # (B, 2c, 7, 7)

        # 3) bottleneck
        h = self.mid2(self.mid1(h, emb), emb)       # (B, 4c, 7, 7)

        # 4) up path with skip connections
        h = self.dec1(torch.cat([self.up1(h), s2], dim=1), emb)   # (B, 2c, 14, 14)
        h = self.dec2(torch.cat([self.up2(h), s1], dim=1), emb)   # (B, c, 28, 28)

        # 5) predicted noise, same shape as input
        return self.out(h)
