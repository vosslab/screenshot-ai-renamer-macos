# macOS AI Screenshot Renamer

A Python tool that extracts on-screen text, generates AI captions, and renames macOS screenshots with clear, context-aware filenames. It now targets Apple Foundation Models on Apple Silicon for fast, on-device filename generation.

---

## Get Running

### Requirements
- Apple Silicon (arm64) running macOS 26.0+ with Apple Intelligence enabled.
- Python 3.9+.
- Xcode command line tools (`xcode-select --install`).

### Install required dependencies

#### Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### System dependencies (macOS)
```bash
# Option A: install individually
brew install exiftool vips

# Option B: use the bundled Brewfile
brew bundle
```

#### Python dependencies
```bash
pip install -r requirements.txt
```

### Verify Apple Intelligence availability
The unit test will fail fast if Apple Intelligence is unavailable:
```bash
./screenshot-renamer.py -t
```
Example output:
```
Running Apple Foundation Models unit test...
Apple Foundation Models completed in 0.42 seconds (attempt 1)
SUCCESS! 95 + 48 = 143
```

---

## How to Run

### Preview changes (dry run)
```bash
./screenshot-renamer.py --dry-run
```
Shows proposed filenames without modifying files.

### Process screenshots
```bash
./screenshot-renamer.py
```
Renames and updates metadata for all screenshots in `~/Desktop` by default.

---

## Usage Help

```bash
./screenshot-renamer.py -h
```

### Command-line options
```
usage: screenshot-renamer.py [-h] [-d [DIRECTORY]] [-n] [-t]
                             [--caption-prompt CAPTION_PROMPT]

Batch process images with step-by-step feedback.

positional arguments:
  directory        Directory containing images (default: ~/Desktop)

options:
  -h, --help       Show this help message and exit.
  -d [DIRECTORY], --directory [DIRECTORY]
                   Directory containing images (default: ~/Desktop)
  -n, --dry-run    Perform a dry run without modifying files.
  -t, --unit-test  Run a unit test (ask LLM to add two numbers).
  --caption-prompt CAPTION_PROMPT
                    Custom captioning prompt applied to both Moondream2 and
                    ViT-GPT2.
```

### Advanced options
- Both Moondream2 (context-heavy) and ViT-GPT2 (literal) captions run for every screenshot; steer both with `--caption-prompt "..."`.
- Before processing, the script prints a plan summary (screenshots found, mode). After each image it logs per-image duration and an updated ETA.
- Filename generation prioritizes the screenshot’s purpose or category. It avoids verbatim OCR lists and uses neutral terms for people images (e.g., `leadership_team_headshot`, `portrait_photo`).
- Prompts are trimmed to fit the Apple Foundation Models 4,096-token context window.

---

## How It Works

1. Finds macOS screenshots in the target directory.
2. Extracts text with OCR.
3. Generates captions with **Moondream2** (context-rich) and **ViT-GPT2** (literal).
4. Combines OCR text and captions, then sends them to Apple Foundation Models for snake_case filename suggestions (with guidance on each captioner’s strengths).
5. Renames the file, keeping the original date prefix (`screenshot_YYYY-MM-DD`).
6. Writes metadata (OCR text and AI caption) into EXIF.

---

## Example Before and After

### Original macOS screenshot
```
Screenshot_2025-01-09_at_6.16.30_PM.png
```

### AI-processed filename
```
screenshot_2025-01-09-wifi_networking_interface_details.png
```

---

## Troubleshooting

### Apple Intelligence not available
- Confirm the Mac is Apple Silicon (arm64).
- Confirm macOS is 26.0 or newer and Apple Intelligence is enabled.
- Ensure Xcode command line tools are installed (`xcode-select --install`).

### Context window exceeded
Prompts are trimmed automatically, but if you see context-related errors, reduce the caption prompt or move large OCR-heavy screenshots out of the batch.

### Performance
All generation runs on-device. If processing still runs hot, close other GPU-heavy apps and reduce batch size.

---

## Resources

- **[AGENTS.md](./AGENTS.md)** – How OCR, captioning, and filename prompts cooperate.
- **[apple-foundation-models](https://pypi.org/project/apple-foundation-models/)** – Python bindings for Apple Foundation Models.
- **[Moondream2 Model](https://huggingface.co/vikhyatk/moondream2)**
- **[Homebrew Documentation](https://brew.sh/)**
- **[ExifTool Documentation](https://exiftool.org/)**

---

## Contributing

Pull requests are welcome. Open an issue for bugs or feature requests.

---

## License

Licensed under the **GPL v3.0**.
