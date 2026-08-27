# Install and setup

## Requirements

- Apple Silicon Mac.
- Python 3.12.
- Full Xcode 26+ with its license agreements accepted. The included official
  Apple SDK builds a native bridge during installation.
- Homebrew.

Ollama remains the default filename provider.

## System dependencies

```bash
brew bundle
```

The Brewfile installs Ollama, ExifTool, Tesseract, and libvips.

## Python dependencies and caption setup

```bash
source source_me.sh && python install_models.py
```

This installs the Python dependency set and preloads both local image-caption
backends: Moondream2 plus ViT-GPT2 and its processor and tokenizer. Rich panels,
section rules, and status labels distinguish dependencies, accelerator validation,
each model, retired-model cleanup, and completion. The installer upgrades Torch
and Torchvision together so their compiled extensions remain compatible.

The caption pipeline requires Apple GPU acceleration through PyTorch MPS. It
does not fall back to CPU or CUDA. Moondream2 remains selected even though
Moondream3 Preview is available because the newer model requires FlexAttention,
which PyTorch MPS does not support. PyTorch does not expose the Apple Neural
Engine as a general device; Apple system models manage accelerator selection
through macOS.

After both current caption models load successfully, the installer removes
explicitly retired project models from the Hugging Face cache. The current
cleanup removes Moondream3 Preview and its Starmie tokenizer dependency. It does
not delete active-model revisions, unrelated Hugging Face models, or Ollama
models. The installer reports each repository and the expected recovered space
before deletion.

## Filename model setup

The default filename model is `qwen3.5:27b` through Ollama. Download it once:

```bash
ollama pull qwen3.5:27b
```

Ollama must be running while screenshots are processed. Launch the Ollama app
or start `ollama serve` in another terminal.

## Apple provider

The standard dependency setup installs Apple's official `apple-fm-sdk`. Using
this provider requires macOS 26+ and Apple Intelligence.

Change `DEFAULT_FILENAME_BACKEND` from `ollama` to `apple` in
[`screenshot_lib/filename_models.py`](../screenshot_lib/filename_models.py).
The operating system supplies the Apple model identity.

Verify the default filename model:

```bash
source source_me.sh && python screenshot-renamer.py -t
```
