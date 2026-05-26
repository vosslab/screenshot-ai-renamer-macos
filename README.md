# macOS AI screenshot renamer

A local Python CLI for Mac users who want screenshots renamed from OCR, visual captions, and on-device Apple Foundation Models filename generation.

## Requirements
- Apple Silicon (arm64) on macOS 26.0 or newer with Apple Intelligence enabled.
- Python 3.12.
- Xcode command line tools (`xcode-select --install`).
- Homebrew.

## Quick start
```bash
brew bundle
pip install -r pip_requirements.txt
./install_moondream.py
./screenshot-renamer.py -t
```

## Usage
```bash
./screenshot-renamer.py --dry-run
./screenshot-renamer.py
./screenshot-renamer.py --directory /path/to/screenshots
```

## Documentation
- [AGENTS.md](AGENTS.md): Agent pipeline overview and repo-specific workflow rules.
- [docs/INSTALL.md](docs/INSTALL.md): Requirements and setup details.
- [docs/USAGE.md](docs/USAGE.md): CLI options and examples.
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): Common failures and fixes.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): Component overview and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): Repository file map.

## Testing
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/
```

## License
GPL v3.0.
