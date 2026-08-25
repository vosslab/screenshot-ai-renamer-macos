# macOS AI screenshot renamer

A local Python CLI for Mac users who want screenshots renamed from OCR, visual captions, and a configurable on-device filename LLM through Ollama or Apple's official Foundation Models SDK.

## Requirements

- Apple Silicon Mac.
- Python 3.12.
- macOS 26+, Apple Intelligence, and full Xcode 26+ for the optional Apple
  Foundation Models provider.
- Homebrew.

## Quick start

```bash
brew bundle
./install_moondream.py
ollama pull qwen3.5:27b
./screenshot-renamer.py -t
./screenshot-renamer.py --dry-run
```

## Usage

```bash
./screenshot-renamer.py --dry-run
./screenshot-renamer.py
./screenshot-renamer.py --directory /path/to/screenshots
```

Filename model defaults are centralized in
[`screenshot_lib/filename_models.py`](screenshot_lib/filename_models.py).

## Documentation

- [AGENTS.md](AGENTS.md): Agent pipeline overview and repo-specific workflow rules.
- [docs/INSTALL.md](docs/INSTALL.md): Requirements and setup details.
- [docs/USAGE.md](docs/USAGE.md): CLI options and examples.
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): Common failures and fixes.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): Component overview and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): Repository file map.

## Testing

```bash
source source_me.sh && pytest tests/
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py
```

## License
GPL v3.0.
