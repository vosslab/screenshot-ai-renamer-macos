# Install and setup

## Requirements
- Apple Silicon (arm64) on macOS 26.0 or newer with Apple Intelligence enabled.
- Python 3.9 or newer.
- Xcode command line tools (`xcode-select --install`).
- Homebrew.

## System dependencies
```bash
brew bundle
```

The Brewfile installs `exiftool`, `tesseract`, and `vips`.

## Python dependencies
```bash
pip install -r pip_requirements.txt
```

## Verify Apple Intelligence
```bash
./screenshot-renamer.py -t
```

Example output:
```
Running Apple Foundation Models unit test...
Apple Foundation Models completed in 0.42 seconds (attempt 1)
SUCCESS! 95 + 48 = 143
```
