# Generative Model Architectures — Project Feedback Report

This report provides reusable feedback aligned with the six rubric criteria supplied for the project. Each criterion includes Pass and Fail feedback with further reading. The overall feedback section includes Pass, Fail, and Ungradable — Required Files Missing outcomes.

---

## 1. Implement class-conditional logic in GAN architectures

### Pass feedback
- `model/cgan.py` contains a Generator that concatenates the latent vector `z` with a class embedding.
- The Discriminator integrates the class label with the image input tensor.
- The Generator uses `Tanh` activation and produces `1 × 28 × 28` tensors in the `[-1, 1]` range.
- The class information is incorporated into both networks in a way that supports class-conditional digit generation.

**Further reading:** [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784) · [PyTorch `torch.cat`](https://pytorch.org/docs/stable/generated/torch.cat.html) · [PyTorch `Tanh`](https://pytorch.org/docs/stable/generated/torch.nn.Tanh.html)

### Fail feedback
- The Generator does not correctly concatenate the latent vector with the class embedding, or the Discriminator does not incorporate the class label with the image input.
- The Generator output shape or activation does not meet the required `1 × 28 × 28` shape and `[-1, 1]` range.
- Review the label-embedding and tensor-shape logic in both networks, then verify the output dimensions and value range with a test batch.

**Further reading:** [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784) · [PyTorch `Embedding`](https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html) · [PyTorch `Tanh`](https://pytorch.org/docs/stable/generated/torch.nn.Tanh.html)

---

## 2. Construct a Conditional U-Net for noise prediction

### Pass feedback
- `model/diffusion.py` implements a `ConditionalUNet` that uses both a time-step embedding and a class-label embedding.
- Skip connections link the contracting (down) path to the expansive (up) path.
- The model returns a predicted-noise tensor with the same shape as the input noisy image.
- Time and class conditioning are incorporated into the network's noise-prediction process.

**Further reading:** [U-Net: Convolutional Networks for Biomedical Image Segmentation](https://arxiv.org/abs/1505.04597) · [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) · [PyTorch `Embedding`](https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html)

### Fail feedback
- The `ConditionalUNet` is missing either the time-step embedding or the class-label embedding, or these conditioning signals are not used by the model.
- Skip connections are missing or do not connect the down and up paths as required.
- The predicted-noise tensor does not match the input noisy image's shape.
- Check conditioning integration, skip-connection dimensions, and the final output layer. Test the model with a sample batch and compare input and output shapes.

**Further reading:** [U-Net paper](https://arxiv.org/abs/1505.04597) · [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) · [PyTorch tensor shapes and operations](https://pytorch.org/docs/stable/tensors.html)

---

## 3. Implement adversarial training loops for cGANs

### Pass feedback
- `01_cGAN_training.ipynb` uses binary cross-entropy (BCE) loss for the standard GAN minimax objective.
- The training loop separately updates the Discriminator using real and generated data and updates the Generator to improve its generated samples.
- The notebook displays a grid of generated digits from 0–9, with samples that clearly correspond to their requested class labels.
- The training steps and generated results make the conditional training process verifiable.

**Further reading:** [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784) · [PyTorch `BCELoss`](https://pytorch.org/docs/stable/generated/torch.nn.BCELoss.html) · [PyTorch DCGAN tutorial](https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html)

### Fail feedback
- The notebook does not implement the required BCE-based adversarial objective, or the Discriminator and Generator updates are not handled as separate training steps.
- Real and fake samples are not both used in the Discriminator update, or the Generator update does not optimize the intended objective.
- The notebook does not display a grid of generated digits 0–9, or the images do not visibly match their class labels.
- Review the loss calculations, optimizer steps, gradient handling, and label conditioning. Add a reproducible sample grid to demonstrate class-specific generation.

**Further reading:** [PyTorch `BCELoss`](https://pytorch.org/docs/stable/generated/torch.nn.BCELoss.html) · [PyTorch optimizers](https://pytorch.org/docs/stable/optim.html) · [PyTorch DCGAN tutorial](https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html)

---

## 4. Implement forward and reverse diffusion processes

### Pass feedback
- `02_diffusion_training.ipynb` implements the forward noising process (`q` sampling) using a linear or cosine beta schedule.
- The `sample_images` function performs iterative reverse denoising from timestep `T` down to `0`.
- The training objective calculates mean squared error (MSE) between the predicted noise and the actual noise added to the image.
- The forward process, reverse sampling loop, and noise-prediction loss are implemented consistently with the selected schedule.

**Further reading:** [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) · [Improved Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2102.09672) · [PyTorch `MSELoss`](https://pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)

### Fail feedback
- The forward noising process or beta schedule is missing or incorrectly applied.
- The `sample_images` function does not iteratively denoise from `T` toward `0`.
- The training loss does not compare predicted noise against the actual added noise using MSE.
- Check the timestep indexing, schedule coefficients, noise sampling, reverse-update equations, and loss calculation. Verify that the sampling loop runs through the intended timesteps without shape or indexing errors.

**Further reading:** [DDPM paper](https://arxiv.org/abs/2006.11239) · [Improved DDPM and cosine schedules](https://arxiv.org/abs/2102.09672) · [PyTorch `MSELoss`](https://pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)

---

## 5. Evaluate generative performance via quantitative and visual metrics

### Pass feedback
- `03_evaluation.ipynb` computes and displays an FID score for both the cGAN and Diffusion model outputs.
- The notebook includes a side-by-side comparison of **Real vs. cGAN vs. Diffusion** samples for at least five different digits.
- A Markdown cell briefly analyzes which model produces higher-fidelity samples and which shows greater diversity.
- The reported metrics and visual comparison support a clear, evidence-based comparison between the two models.

**Further reading:** [Fréchet Inception Distance (FID) paper](https://arxiv.org/abs/1706.08500) · [TorchMetrics FID documentation](https://lightning.ai/docs/torchmetrics/stable/image/frechet_inception_distance.html) · [TensorFlow — Evaluating generative models](https://www.tensorflow.org/tgan/tutorial/evaluate)

### Fail feedback
- The notebook does not compute and display FID for both model outputs, or the metric setup is not applied consistently enough to support a comparison.
- The required side-by-side **Real vs. cGAN vs. Diffusion** samples for at least five digits are missing.
- The Markdown analysis does not discuss fidelity and diversity, or its conclusions are not supported by the displayed results.
- Add the missing metrics and comparisons, and state the evaluation conditions and key limitations so the results can be interpreted appropriately.

**Further reading:** [FID paper](https://arxiv.org/abs/1706.08500) · [TorchMetrics FID documentation](https://lightning.ai/docs/torchmetrics/stable/image/frechet_inception_distance.html) · [Evaluating generative models](https://www.tensorflow.org/tgan/tutorial/evaluate)

---

## 6. Validate synthetic data utility through downstream tasks

### Pass feedback
- `03_evaluation.ipynb` implements a CNN classifier trained using only synthetic images generated by the models.
- The trained classifier is evaluated on the real MNIST test set.
- The notebook reports the final test accuracy, providing a quantitative indication of how useful the synthetic training data is for a downstream classification task.
- The data split and training process make clear that real MNIST test images are used for evaluation, not for training the classifier.

**Further reading:** [MNIST dataset](https://yann.lecun.com/exdb/mnist/) · [PyTorch image classification tutorial](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html) · [Scikit-learn classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)

### Fail feedback
- The CNN classifier is missing, or its training data includes real training images instead of only synthetic images from the generative models.
- The classifier is not evaluated against the real MNIST test set, or the final accuracy is not reported.
- The evaluation setup does not clearly separate synthetic training data from real test data.
- Ensure that only generated samples are used to train the classifier, evaluate it on the real MNIST test set, and report the final accuracy along with the data source used for training.

**Further reading:** [MNIST dataset](https://yann.lecun.com/exdb/mnist/) · [PyTorch image classification tutorial](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html) · [Scikit-learn classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)

---

# Overall Project Feedback

## Pass

- The project implements the required class-conditional GAN and Conditional U-Net architectures, including the relevant label and time-step conditioning.
- The training notebooks demonstrate adversarial optimization and forward/reverse diffusion with the required loss functions and sampling process.
- The evaluation notebook compares cGAN and Diffusion outputs using FID and visual samples, then assesses synthetic-data utility with a CNN tested on the real MNIST test set.
- The implementation is supported by clear notebook outputs and concise analysis of sample quality, diversity, and downstream accuracy.

## Fail

- One or more required architectures, training procedures, sampling steps, or evaluation components are missing or do not meet the stated requirements.
- Conditional generation may not be demonstrated clearly, or the diffusion process may have issues with timestep handling, noise prediction, or reverse sampling.
- FID scores, the required visual comparison, analysis of fidelity and diversity, or downstream classifier accuracy may be missing or incomplete.
- Address the failed rubric criteria, verify tensor shapes and loss calculations, and rerun the notebooks so the outputs and conclusions are reproducible and supported by evidence.

## Ungradable — Required Files Missing

- The required files may be absent or incomplete: `model/cgan.py`, `model/diffusion.py`, `01_cGAN_training.ipynb`, `02_diffusion_training.ipynb`, or `03_evaluation.ipynb`.
- Without the relevant source files and executed notebook outputs, the conditional architectures, training loops, sampling process, FID comparison, and downstream utility test cannot be verified.
- Submit the missing files and ensure the notebooks include the outputs needed to assess each criterion before the project is graded.
