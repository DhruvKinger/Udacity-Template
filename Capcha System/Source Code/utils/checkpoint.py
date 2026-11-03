"""Save / load model + optimizer states."""
import os
from typing import Dict, Union

import torch
import torch.nn as nn

Models = Union[nn.Module, Dict[str, nn.Module]]
Optims = Union[torch.optim.Optimizer, Dict[str, torch.optim.Optimizer], None]


def _as_dict(obj, default_name: str):
    if obj is None:
        return {}
    return obj if isinstance(obj, dict) else {default_name: obj}


def save_checkpoint(path: str, models: Models, optimizers: Optims = None, epoch: int = 0,
                    history: dict = None, config: dict = None) -> str:
    """Save one or several models (and optimizers) to ``path``."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    ckpt = {
        "epoch": epoch,
        "models": {k: m.state_dict() for k, m in _as_dict(models, "model").items()},
        "optimizers": {k: o.state_dict() for k, o in _as_dict(optimizers, "optimizer").items()},
        "history": history or {},
        "config": config or {},
    }
    torch.save(ckpt, path)
    return path


def load_checkpoint(path: str, models: Models, optimizers: Optims = None, device="cpu") -> dict:
    """Load weights in-place into ``models`` (and ``optimizers``). Returns the full checkpoint dict."""
    ckpt = torch.load(path, map_location=device, weights_only=False)
    for k, m in _as_dict(models, "model").items():
        m.load_state_dict(ckpt["models"][k])
    for k, o in _as_dict(optimizers, "optimizer").items():
        if k in ckpt["optimizers"]:
            o.load_state_dict(ckpt["optimizers"][k])
    return ckpt
