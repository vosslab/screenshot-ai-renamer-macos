# macOS AI Screenshot Renamer

A Python tool that extracts on-screen text, generates AI captions, and renames macOS screenshots with clear, context-aware filenames. It uses OCR, vision captioners, and an LLM to keep names concise and searchable.

---

## Get Running

### Install required dependencies

#### Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### System dependencies (macOS)
```bash
# Option A: install individually
brew install ollama exiftool vips

# Option B: use the bundled Brewfile
brew bundle
```

#### Python dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

### Start the Ollama server
```bash
ollama serve
```

### Verify the LLM path (unit test)
```bash
./screenshot-renamer.py -t
```
Example output:
```
Selected Ollama model: phi4:14b-q8_0
Running unit test...
Ollama completed in 2.38 seconds
SUCCESS! 95 + 48 = 143
```

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
- Set the `OLLAMA_MODEL` environment variable to force a specific Ollama model (overrides VRAM-based auto selection).

---

## How It Works

1. Finds macOS screenshots in the target directory.
2. Extracts text with OCR.
3. Generates captions with **Moondream2** (context-rich) and **ViT-GPT2** (literal).
4. Combines OCR text and captions, then sends them to an Ollama LLM for snake_case filename suggestions (with guidance on each captioner’s strengths).
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

### Ollama server not running
Start the server:
```bash
ollama serve
```

### Model not found (`ollama._types.ResponseError: model not found`)
If you see:
```bash
ollama._types.ResponseError: model "llama3.2:3b-instruct-q5_K_M" not found, try pulling it first (status code: 404)
```
Download the model:
```bash
ollama pull llama3.2:3b-instruct-q5_K_M
```

### Selecting the right Ollama model
The script picks a model based on available VRAM:

| VRAM Size      | Model Used                          |
|---------------|--------------------------------|
| **>30GB**     | `phi4:14b-q8_0`               |
| **>14GB**     | `phi4:14b-q4_K_M`             |
| **>4GB**      | `llama3.2:3b-instruct-q5_K_M` |
| **Default**   | `llama3.2:1b-instruct-q4_K_M` |

If VRAM is limited, pull a smaller model:
```bash
ollama pull llama3.2:1b-instruct-q4_K_M
```
Then update `config_ollama.py` to force that model.

---

## Resources

- **[AGENTS.md](./AGENTS.md)** – How OCR, captioning, and Ollama prompts cooperate.
- **[Ollama Documentation](https://ollama.com/docs)**
- **[Ollama Phi Model](https://ollama.com/library/phi)**
- **[Moondream2 Model](https://huggingface.co/vikhyatk/moondream2)**
- **[Homebrew Documentation](https://brew.sh/)**
- **[ExifTool Documentation](https://exiftool.org/)**

---

## Contributing

Pull requests are welcome. Open an issue for bugs or feature requests.

---

## License

Licensed under the **GPL v3.0**.
