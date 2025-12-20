# Usage

## Basic run
```bash
./screenshot-renamer.py
```

Processes screenshots in `~/Desktop`, renames files, and writes OCR and caption metadata.

## Dry run
```bash
./screenshot-renamer.py --dry-run
```

Prints proposed filenames without modifying files.

## Specify a directory
```bash
./screenshot-renamer.py --directory /path/to/screenshots
```

## Unit test
```bash
./screenshot-renamer.py -t
```

## Install note
Python dependencies are listed in `pip_requirements.txt`.

## Command-line options
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
                   Custom captioning prompt applied to both caption models.
```

## Filename format
- Output filenames follow `screenshot_YYYY-MM-DD-<slug>.png`.
- The slug is snake_case and capped at 64 characters.
- People are described neutrally (for example `portrait_photo`).
