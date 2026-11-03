"""Evaluation helpers: FID, conditioning accuracy, diversity and a small CNN classifier."""
import warnings

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import linalg


# ----------------------------------------------------------------- classifier
class SimpleCNN(nn.Module):
    """Small CNN for MNIST (inputs in [-1, 1], shape (B, 1, 28, 28))."""

    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),     # 14
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),    # 7
        )
        self.fc1 = nn.Sequential(nn.Flatten(), nn.Dropout(0.3), nn.Linear(64 * 7 * 7, 128), nn.ReLU())
        self.fc2 = nn.Linear(128, num_classes)

    def features(self, x):
        return self.fc1(self.conv(x))

    def forward(self, x):
        return self.fc2(self.features(x))


def train_classifier(images, labels, device, epochs=5, batch_size=128, lr=1e-3, verbose=True):
    """Train a SimpleCNN on in-memory tensors ``images`` (N,1,28,28) in [-1,1] and ``labels`` (N,)."""
    model = SimpleCNN().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    ds = torch.utils.data.TensorDataset(images.float(), labels.long())
    loader = torch.utils.data.DataLoader(ds, batch_size=batch_size, shuffle=True)
    for ep in range(1, epochs + 1):
        model.train()
        total, correct, loss_sum = 0, 0, 0.0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = F.cross_entropy(logits, y)
            opt.zero_grad(); loss.backward(); opt.step()
            loss_sum += loss.item() * len(y); total += len(y); correct += (logits.argmax(1) == y).sum().item()
        if verbose:
            print(f"  classifier epoch {ep}/{epochs} | loss {loss_sum / total:.4f} | train acc {correct / total:.4f}")
    return model


@torch.no_grad()
def evaluate_classifier(model, images, labels, device, batch_size=500) -> float:
    """Accuracy of ``model`` on (images, labels)."""
    model.eval().to(device)
    correct = 0
    for i in range(0, len(images), batch_size):
        x = images[i:i + batch_size].to(device)
        y = labels[i:i + batch_size].to(device)
        correct += (model(x).argmax(1) == y).sum().item()
    return correct / len(images)


def conditioning_accuracy(reference_classifier, gen_images, gen_labels, device) -> float:
    """Fraction of generated images that a (real-data-trained) classifier assigns to the *requested* label."""
    return evaluate_classifier(reference_classifier, gen_images, gen_labels, device)


@torch.no_grad()
def intra_class_diversity(images, labels, num_classes=10, max_per_class=500) -> float:
    """Mean pairwise L2 distance (pixel space) between samples of the same class, averaged over classes.
    Higher = more diverse. Compare against the value obtained on real data."""
    vals = []
    for c in range(num_classes):
        x = images[labels == c][:max_per_class].flatten(1).float()
        if len(x) < 2:
            continue
        d = torch.cdist(x, x)
        vals.append((d.sum() / (len(x) * (len(x) - 1))).item())
    return float(np.mean(vals))


# ----------------------------------------------------------------- FID
def calculate_frechet_distance(mu1, sigma1, mu2, sigma2, eps=1e-6) -> float:
    """Frechet distance between two Gaussians N(mu1, sigma1) and N(mu2, sigma2)."""
    diff = mu1 - mu2
    covmean, _ = linalg.sqrtm(sigma1.dot(sigma2), disp=False)
    if not np.isfinite(covmean).all():
        offset = np.eye(sigma1.shape[0]) * eps
        covmean = linalg.sqrtm((sigma1 + offset).dot(sigma2 + offset))
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    return float(diff.dot(diff) + np.trace(sigma1) + np.trace(sigma2) - 2 * np.trace(covmean))


_INCEPTION = None


def _get_inception(device):
    global _INCEPTION
    if _INCEPTION is None:
        from torchvision.models import inception_v3, Inception_V3_Weights
        net = inception_v3(weights=Inception_V3_Weights.IMAGENET1K_V1)
        net.fc = nn.Identity()          # 2048-d pool3 features
        _INCEPTION = net.eval()
    return _INCEPTION.to(device)


@torch.no_grad()
def inception_features(images, device, batch_size=100) -> np.ndarray:
    """2048-d Inception-v3 pool features of images in [-1, 1], shape (N, 1, 28, 28)."""
    net = _get_inception(device)
    mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)
    feats = []
    for i in range(0, len(images), batch_size):
        x = images[i:i + batch_size].to(device).float()
        x = ((x + 1) / 2).clamp(0, 1).repeat(1, 3, 1, 1)                     # grayscale -> RGB, [0, 1]
        x = F.interpolate(x, size=(299, 299), mode="bilinear", align_corners=False)
        feats.append(net((x - mean) / std).cpu())
    return torch.cat(feats).numpy().astype(np.float64)


@torch.no_grad()
def cnn_features(images, device, cnn, batch_size=500) -> np.ndarray:
    """Penultimate-layer features of a MNIST-trained SimpleCNN (fallback feature space)."""
    cnn.eval().to(device)
    feats = [cnn.features(images[i:i + batch_size].to(device).float()).cpu() for i in range(0, len(images), batch_size)]
    return torch.cat(feats).numpy().astype(np.float64)


def _stats(feats):
    return feats.mean(axis=0), np.cov(feats, rowvar=False)


def compute_fid(real_images, fake_images, device, feature_net=None, backend="inception", batch_size=100):
    """Frechet distance between real and generated image sets (both in [-1, 1]).

    backend="inception": standard FID with ImageNet Inception-v3 pool features (torchvision weights, so values are
        comparable *within* this project but not exactly with TF-Inception FID numbers in papers).
    backend="cnn": FID computed in the feature space of ``feature_net`` (a MNIST-trained SimpleCNN).
    If the Inception weights cannot be downloaded and ``feature_net`` is given, falls back to "cnn" with a warning.
    Returns (fid_value, backend_used).
    """
    if backend == "inception":
        try:
            f_real = inception_features(real_images, device, batch_size)
            f_fake = inception_features(fake_images, device, batch_size)
            used = "inception"
        except Exception as e:  # no internet / weights unavailable
            if feature_net is None:
                raise RuntimeError("Could not load Inception weights and no `feature_net` fallback given.") from e
            warnings.warn(f"Inception unavailable ({type(e).__name__}); falling back to CNN-feature FID.")
            return compute_fid(real_images, fake_images, device, feature_net, backend="cnn")
    elif backend == "cnn":
        f_real = cnn_features(real_images, device, feature_net)
        f_fake = cnn_features(fake_images, device, feature_net)
        used = "cnn"
    else:
        raise ValueError("backend must be 'inception' or 'cnn'")
    mu_r, sig_r = _stats(f_real)
    mu_f, sig_f = _stats(f_fake)
    return calculate_frechet_distance(mu_r, sig_r, mu_f, sig_f), used
