# Code architecture

## Overview

This repository is a local macOS CLI pipeline for renaming screenshots. The
entry point, [screenshot-renamer.py](../screenshot-renamer.py), scans a target
folder for macOS screenshot PNG files, extracts OCR text, generates visual
captions, asks Apple Foundation Models for a concise filename, and optionally
renames the image while embedding metadata.

The pipeline is intentionally script-oriented rather than packaged as a Python
library. Runtime helpers live in [tools/](../tools/), setup helpers live at the
repo root, and developer automation lives in [tests/](../tests/) and
[devel/](../devel/).

## Major components

- [screenshot-renamer.py](../screenshot-renamer.py): CLI orchestration, file
  discovery, dry-run/live mode handling, progress output, ETA reporting, and
  per-image processing.
- [install_moondream.py](../install_moondream.py): installs the runtime
  dependency set and preloads the local Moondream model selected for the active
  device.
- [tools/extract_text.py](../tools/extract_text.py): opens images with Pillow
  and extracts text through Tesseract via `pytesseract`.
- [tools/generate_caption.py](../tools/generate_caption.py): loads caption
  backends with Transformers. The primary backend is Moondream, selected by
  active device compatibility; the secondary backend is ViT-GPT2.
- [tools/intelligent_filename.py](../tools/intelligent_filename.py): builds the
  filename prompt, trims OCR/caption context, validates Apple model output, and
  returns a sanitized PNG filename.
- [tools/config_apple_models.py](../tools/config_apple_models.py): validates
  Apple Silicon, macOS 26+, and Apple Intelligence availability, then wraps one
  short-lived Foundation Models generation session.
- [tools/update_metadata.py](../tools/update_metadata.py): writes OCR text and
  caption metadata into the renamed image through ExifTool.
- [tools/common_func.py](../tools/common_func.py): shared image resizing,
  device selection, attention-mask, and image-path helpers.

## Data flow

1. [screenshot-renamer.py](../screenshot-renamer.py) scans the selected
   directory for pending `Screen*.png` files and skips already-renamed files that
   match `screenshot_YYYY-MM-DD-<slug>.png`.
2. [tools/extract_text.py](../tools/extract_text.py) runs OCR and returns the
   extracted screen text.
3. [tools/generate_caption.py](../tools/generate_caption.py) generates a primary
   Moondream caption and, when available, a secondary ViT-GPT2 caption.
4. `_compose_caption_payload()` in
   [screenshot-renamer.py](../screenshot-renamer.py) combines caption text and
   model guidance for the filename step.
5. [tools/intelligent_filename.py](../tools/intelligent_filename.py) sends OCR
   and caption context to
   [tools/config_apple_models.py](../tools/config_apple_models.py), sanitizes the
   returned text, and rejects backend error text before it can become a filename.
6. [screenshot-renamer.py](../screenshot-renamer.py) combines the original
   screenshot date with the generated slug. In dry-run mode it prints the rename;
   in live mode it renames the file and calls
   [tools/update_metadata.py](../tools/update_metadata.py).

## Testing and verification

- Fast repo checks run with:
  ```bash
  /opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/
  ```
- [tests/test_import_requirements.py](../tests/test_import_requirements.py)
  checks Python imports against runtime and developer dependency manifests.
- [tests/test_bandit_security.py](../tests/test_bandit_security.py) runs Bandit
  at medium severity or higher.
- [tests/test_pyflakes_code_lint.py](../tests/test_pyflakes_code_lint.py),
  [tests/test_indentation.py](../tests/test_indentation.py), and related hygiene
  tests enforce the repo's Python style and file conventions.
- Focused filename tests verify that Apple Foundation Models error text is
  rejected instead of being accepted as a filename.

## Extension points

- Add or swap caption backends in
  [tools/generate_caption.py](../tools/generate_caption.py), then update
  `_compose_caption_payload()` in
  [screenshot-renamer.py](../screenshot-renamer.py) if the filename agent needs
  different model guidance.
- Change filename rules in
  [tools/intelligent_filename.py](../tools/intelligent_filename.py).
- Change Apple Foundation Models session behavior in
  [tools/config_apple_models.py](../tools/config_apple_models.py).
- Add metadata fields in [tools/update_metadata.py](../tools/update_metadata.py).
- Add focused tests under [tests/](../tests/) for stable behavior that can run
  quickly and offline.

## Known gaps

- Verify Moondream memory use and latency on the target Mac after upstream model
  changes, because the project intentionally tracks current upstream packages and
  unpinned model revisions.
