# Install and setup

## Requirements

- Apple Silicon Mac.
- Python 3.12.
- Full Xcode 26+ with its license agreements accepted. The included official
  Apple SDK builds a native bridge during installation.
- Homebrew.

Ollama remains the default filename provider.

See `docs/MODELS.md` for the complete hardware, accelerator, memory, model, and
native-runtime compatibility matrix.

## System dependencies

```bash
brew bundle
```

The Brewfile installs Ollama, ExifTool, Tesseract, and libvips.

## Python dependencies and caption setup

```bash
source source_me.sh && python install_models.py
```

This installs the Python dependency set and validates two local caption paths:

- Moondream 3.1 through Photon's native Metal runtime.
- ViT-GPT2 through PyTorch MPS as independent caption evidence and the visual
  fallback when Photon is unavailable.

The installer runs a real caption request against a generated sanity-check image;
loading weights alone does not count as validation. Rich sections distinguish
dependencies, Apple hardware, each model, cleanup, and completion. Torch uses
the compatible `>=2.12,<2.13` range, and Torchvision uses the paired
`>=0.27,<0.28` range. The installer can take newer patch releases without
crossing the native Photon bridge's supported minor-version boundary.

Photon requires Apple Silicon, macOS 13+, and at least 24 GB of unified memory.
The installer reports detected memory. Macs below 24 GB skip Moondream 3.1 and
continue with OCR and ViT-GPT2 MPS. CPU and CUDA caption fallbacks remain
disabled. PyTorch does not expose the Apple Neural Engine as a general device.

After validation, cleanup removes the retired Moondream3 Preview and Moondream2
repositories. It preserves Photon weights, unrelated Hugging Face models, and
Ollama models.

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
