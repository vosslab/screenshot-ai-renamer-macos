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

## Python dependencies and Moondream setup

```bash
source source_me.sh && python install_moondream.py
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
