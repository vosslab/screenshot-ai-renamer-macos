# Install and setup

## Requirements

- Apple Silicon Mac.
- Python 3.12.
- Full Xcode 26+ with its license agreements accepted. The official Apple SDK
  builds a native bridge during installation; command line tools alone are not
  sufficient.
- Homebrew.

The optional Apple Foundation Models provider also requires macOS 26+ and Apple
Intelligence enabled. Ollama remains the default provider.

## System dependencies

```bash
brew bundle
```

The Brewfile installs Ollama, ExifTool, Tesseract, and libvips.

## Python dependencies and Moondream setup

```bash
./install_moondream.py
```

This installs the Python dependency set and preloads the newest local Moondream
model compatible with the active device. Apple MPS uses Moondream2 with
Transformers 4.x because the current Transformers 5 path is broken for
Moondream on MPS, and Moondream3 Preview requires FlexAttention, which is not
supported on MPS.

## Filename model setup

The default filename model is `qwen3.5:27b` through Ollama. Download it once:

```bash
ollama pull qwen3.5:27b
```

Ollama must be running while screenshots are processed. Launch the Ollama app
or start `ollama serve` in another terminal.

The same setup installs Apple's official `apple-fm-sdk`. To use that provider,
change `DEFAULT_FILENAME_BACKEND` from `ollama` to `apple` in
[`screenshot_lib/filename_models.py`](../screenshot_lib/filename_models.py).
The Apple provider uses the system-selected model and therefore has no model
name setting.

Verify the default filename model:

```bash
./screenshot-renamer.py -t
```
