# Synthetic Handwriting for CAPTCHA Training - cGAN vs Conditional Diffusion

SuperCognition Labs' CAPTCHA can be beaten by bots that rely on simple geometric fonts. This project builds two
class-conditional generative models on MNIST (a **Conditional GAN** and a **Conditional Diffusion Model**), uses them
to produce a large, varied dataset of human-like handwritten digits, and compares them on quality, diversity,
conditioning and practical suitability.

## Project structure
```
project/
|-- data_utils/dataloader.py    MNIST loading, [-1,1] normalisation, tensor helpers
|-- model/
|   |-- cgan.py                 Generator (z ++ label embedding -> Tanh 1x28x28), Discriminator (image + label map)
|   `-- diffusion.py            timestep_embedding, ResidualBlock, ConditionalUNet (skip connections)
|-- training/
|   |-- train_cgan.py           BCE minimax training: separate D and G updates, checkpointing
|   `-- train_diffusion.py      linear/cosine schedules, q_sample, MSE noise-prediction training, reverse sampler
|-- utils/
|   |-- checkpoint.py           save/load model + optimizer states
|   |-- metrics.py              FID, CNN classifier, conditioning accuracy, diversity
|   `-- visualize.py            grids, real-vs-generated comparison, interpolation, CAPTCHA composer
|-- 00_data_preparation.ipynb
|-- 01_cGAN_training.ipynb
|-- 02_diffusion_training.ipynb
|-- 03_evaluation.ipynb
`-- README.md
```

## How to run
```bash
pip install torch torchvision scipy matplotlib jupyter
jupyter notebook          # run notebooks in order: 00 -> 01 -> 02 -> 03 (GPU strongly recommended)
```
Notebooks must be started from the project root (they import `data_utils`, `model`, `training`, `utils`).
Checkpoints are written to `checkpoints/`, figures to `outputs/`.
Setting the environment variable `QUICK_RUN=1` runs a tiny smoke-test version of every notebook (1 epoch, few samples).

## Models
| | cGAN | Conditional diffusion (DDPM) |
|---|---|---|
| Conditioning | G: `concat(z, Embedding(y))`; D: label embedded to a 28x28 map and concatenated as 2nd channel | label embedding added to the time embedding and injected in every residual block |
| Output | `Tanh`, 1x28x28 in [-1, 1] | noise prediction, same shape as the noisy input |
| Objective | minimax GAN with `BCELoss` (D: mean of real/fake BCE; G: non-saturating) | MSE(predicted noise, true noise) |
| Architecture | transposed-conv G, conv D | U-Net: 28->14->7 down path, bottleneck, 7->14->28 up path with concatenated skip connections |
| Sampling | 1 forward pass | reverse ancestral DDPM loop T-1 -> 0 (optionally re-spaced to K < T steps) |

Details: linear beta schedule 1e-4 -> 0.02 with T = 1000 (cosine schedule available), EMA of weights for sampling.

## Evaluation (notebook 03)
* Visual comparison Real / cGAN / Diffusion for all 10 digits.
* **FID** between the real MNIST test set and 10,000 synthetic images per model. Uses torchvision's ImageNet Inception-v3
  features; if the weights cannot be downloaded the notebook falls back to CNN-feature FID and prints which backend was used.
* Conditioning accuracy (real-data CNN classifies the requested digit), intra-class diversity, generation time.
* **Downstream utility:** a CNN trained **only on synthetic data** (cGAN, diffusion, both) and tested on the **real** MNIST test set.
* A markdown analysis cell (section 7) comparing fidelity, diversity, conditioning and practicality - review it against your own numbers.

## Stand-out features implemented
* Latent-space walk (notebook 01) - interpolation between two noise vectors.
* Cosine noise schedule trained and compared to linear by FID (notebooks 02/03).
* Multi-digit CAPTCHA generator `utils.visualize.make_captcha` (notebook 03, section 10).
* FID vs number of sampling steps (notebook 03, section 8).

## Results (run submitted with this project)
| Model | FID (Inception) | Conditioning acc | Downstream acc (real test) | s / 1000 imgs |
|---|---|---|---|---|
| cGAN | 9.70 | 0.990 | 95.47% | 0.03 |
| Diffusion (250 steps) | 2.91 | 0.983 | 96.81% | 72.30 |
| cGAN + Diffusion | - | - | 97.59% | - |
| Real data (reference) | 1.76 (real vs real) | 0.992 | 99.18% | - |

Cosine-schedule diffusion: FID 8.09 vs 2.91 for linear (250 sampling steps). FID vs sampling steps (linear): 10 -> 19.13, 25 -> 9.38, 50 -> 6.70, 100 -> 5.69, 250 -> 5.44, 500 -> 5.25, 1000 -> 5.45 (2,000 samples).

Note: the cGAN uses GroupNorm instead of BatchNorm because a BatchNorm version collapsed to near-identical samples in `eval()` mode.
Executed notebooks with outputs are provided separately from this zip when available; the notebooks here are the code only.
