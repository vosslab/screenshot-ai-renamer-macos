# macOS AI screenshot renamer

A Python tool that extracts on-screen text, generates two captions, and renames macOS screenshots with concise, context-aware filenames. Filename generation runs on-device with Apple Foundation Models.

## Requirements
- Apple Silicon (arm64) on macOS 26.0 or newer with Apple Intelligence enabled.
- Python 3.9 or newer.
- Xcode command line tools (`xcode-select --install`).
- Homebrew.

## Quick start
```bash
brew bundle
pip install -r pip_requirements.txt
./screenshot-renamer.py -t
```

## Run
```bash
./screenshot-renamer.py --dry-run
./screenshot-renamer.py
./screenshot-renamer.py --directory /path/to/screenshots
```

## How it works
1. Finds macOS screenshots in the target directory.
2. Extracts text with OCR.
3. Generates captions with Moondream2 and ViT-GPT2.
4. Combines OCR text and captions, then requests a snake_case filename from Apple Foundation Models.
5. Renames the file and embeds metadata (OCR text and AI caption).

## Docs
- [AGENTS](AGENTS.md) for the agent pipeline overview.
- [Install and setup](docs/INSTALL.md) for full environment details.
- [Usage](docs/USAGE.md) for CLI options and examples.
- [Troubleshooting](docs/TROUBLESHOOTING.md) for common issues.

## License
GPL v3.0.
