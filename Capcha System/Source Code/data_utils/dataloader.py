"""MNIST loading utilities.

All images are normalised to the [-1, 1] range (mean 0.5, std 0.5) so that they
match the Tanh output range of the cGAN generator and the Gaussian-noise
range used by the diffusion model.
"""
from typing import Tuple

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

DEFAULT_ROOT = "./data/mnist"


def get_transform() -> transforms.Compose:
    """Standard MNIST transform: PIL -> tensor in [0, 1] -> [-1, 1]."""
    return transforms.Compose(
        [
            transforms.ToTensor(),                 # (1, 28, 28), values in [0, 1]
            transforms.Normalize((0.5,), (0.5,)),  # values in [-1, 1]
        ]
    )


def get_mnist_dataset(train: bool = True, root: str = DEFAULT_ROOT, download: bool = True):
    """Return the MNIST torchvision dataset (train or test split)."""
    return datasets.MNIST(root=root, train=train, download=download, transform=get_transform())


def get_dataloader(
    batch_size: int = 128,
    train: bool = True,
    shuffle: bool = None,
    num_workers: int = 2,
    root: str = DEFAULT_ROOT,
    download: bool = True,
    drop_last: bool = None,
    subset: int = None,
) -> DataLoader:
    """Return a DataLoader over MNIST. Shuffles / drops last batch only for training by default.
    ``subset`` keeps only the first N samples (debugging)."""
    if shuffle is None:
        shuffle = train
    if drop_last is None:
        drop_last = train
    dataset = get_mnist_dataset(train=train, root=root, download=download)
    if subset is not None:  # handy for quick smoke tests / debugging
        dataset = torch.utils.data.Subset(dataset, range(min(subset, len(dataset))))
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        drop_last=drop_last,
        pin_memory=torch.cuda.is_available(),
    )


def get_mnist_dataloaders(
    batch_size: int = 128, num_workers: int = 2, root: str = DEFAULT_ROOT, download: bool = True
) -> Tuple[DataLoader, DataLoader]:
    """Convenience helper returning (train_loader, test_loader)."""
    train_loader = get_dataloader(batch_size, True, num_workers=num_workers, root=root, download=download)
    test_loader = get_dataloader(batch_size, False, num_workers=num_workers, root=root, download=download)
    return train_loader, test_loader


def dataset_to_tensors(train: bool = False, root: str = DEFAULT_ROOT, download: bool = True):
    """Return the whole split as tensors: images (N, 1, 28, 28) in [-1, 1] and labels (N,) long.

    Used by the evaluation notebook (FID / classifier) where we need all real
    images in memory at once.
    """
    ds = datasets.MNIST(root=root, train=train, download=download)
    images = ds.data.unsqueeze(1).float() / 127.5 - 1.0
    labels = ds.targets.long()
    return images, labels


# Alias matching the name used in the starter notebooks
get_mnist_loaders = get_mnist_dataloaders
