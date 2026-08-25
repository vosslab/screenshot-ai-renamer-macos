# Code architecture

## Overview

This repository is a local macOS CLI pipeline for renaming screenshots. The
entry point, [screenshot-renamer.py](../screenshot-renamer.py), scans a target
folder for macOS screenshot PNG files, extracts OCR text, generates visual
captions, asks a configurable local filename LLM for a concise filename, and
optionally renames the image while embedding metadata. Ollama with
`qwen3.5:27b` is the default with thinking enabled. Apple's official
Foundation Models SDK is available behind the same provider boundary.

Reusable runtime modules live in [screenshot_lib/](../screenshot_lib/).
Standalone commands live at the repo root and in [tools/](../tools/), while
developer automation lives in [tests/](../tests/) and [devel/](../devel/).

## Major components

- [screenshot-renamer.py](../screenshot-renamer.py): CLI orchestration, file
  discovery, dry-run/live mode handling, progress output, ETA reporting, and
  per-image processing.
- [install_moondream.py](../install_moondream.py): installs the runtime
  dependency set and preloads the local Moondream model selected for the active
  device.
- [screenshot_lib/extract_text.py](../screenshot_lib/extract_text.py): opens images with Pillow
  and extracts text through Tesseract via `pytesseract`.
- [screenshot_lib/generate_caption.py](../screenshot_lib/generate_caption.py): loads caption
  backends with Transformers. The primary backend is Moondream, selected by
  active device compatibility; the secondary backend is ViT-GPT2.
- [screenshot_lib/intelligent_filename.py](../screenshot_lib/intelligent_filename.py):
  builds the established filename prompt, extracts the preferred XML result,
  and returns a sanitized PNG filename.
- [screenshot_lib/filename_models.py](../screenshot_lib/filename_models.py): owns
  filename model configuration and dispatch.
- [screenshot_lib/apple_models.py](../screenshot_lib/apple_models.py): checks
  Apple's system-model availability and runs a short-lived session through the
  official `apple_fm_sdk` module.
- [screenshot_lib/ollama_models.py](../screenshot_lib/ollama_models.py): sends
  separated system and user messages to the selected local Ollama model.
- [screenshot_lib/update_metadata.py](../screenshot_lib/update_metadata.py): writes OCR text and
  caption metadata into the renamed image through ExifTool.
- [screenshot_lib/common_func.py](../screenshot_lib/common_func.py): shared image resizing,
  device selection, attention-mask, and image-path helpers.

## Data flow

1. [screenshot-renamer.py](../screenshot-renamer.py) scans the selected
   directory for pending `Screen*.png` files and skips already-renamed files that
   match `screenshot_YYYY-MM-DD-<slug>.png`.
2. [screenshot_lib/extract_text.py](../screenshot_lib/extract_text.py) runs OCR and returns the
   extracted screen text.
3. [screenshot_lib/generate_caption.py](../screenshot_lib/generate_caption.py) generates a primary
   Moondream caption and, when available, a secondary ViT-GPT2 caption.
4. `_compose_caption_payload()` in
   [screenshot-renamer.py](../screenshot-renamer.py) combines caption text and
   model guidance for the filename step.
5. [screenshot_lib/intelligent_filename.py](../screenshot_lib/intelligent_filename.py) sends OCR
   and caption context through
   [screenshot_lib/filename_models.py](../screenshot_lib/filename_models.py).
   The dispatcher selects Ollama or the official Apple SDK. Both adapters return
   complete text to the same parser: the final slug is extracted from a
   `<filename>` XML element when present, while the response sanitizer also
   handles usable bare-text replies.
6. [screenshot-renamer.py](../screenshot-renamer.py) combines the original
   screenshot date with the generated slug. In dry-run mode it prints the rename;
   in live mode it renames the file and calls
   [screenshot_lib/update_metadata.py](../screenshot_lib/update_metadata.py).

## Testing and verification

- Fast repo checks run with:
  ```bash
  source source_me.sh && pytest tests/
  ```
- [tests/test_function_typing.py](../tests/test_function_typing.py) enforces
  type annotations repo-wide using builtin generics and PEP 604 unions.
- [tests/test_bandit_security.py](../tests/test_bandit_security.py) runs Bandit
  at medium severity or higher.
- [tests/test_pyflakes_code_lint.py](../tests/test_pyflakes_code_lint.py),
  [tests/test_indentation.py](../tests/test_indentation.py),
  [tests/test_whitespace.py](../tests/test_whitespace.py),
  [tests/test_ascii_compliance.py](../tests/test_ascii_compliance.py),
  [tests/test_import_dot.py](../tests/test_import_dot.py),
  [tests/test_import_star.py](../tests/test_import_star.py),
  [tests/test_shebangs.py](../tests/test_shebangs.py), and
  [tests/test_markdown_links.py](../tests/test_markdown_links.py) enforce the
  repo's Python style, import rules, and file conventions.

## Extension points

- Add or swap caption backends in
  [screenshot_lib/generate_caption.py](../screenshot_lib/generate_caption.py), then update
  `_compose_caption_payload()` in
  [screenshot-renamer.py](../screenshot-renamer.py) if the filename agent needs
  different model guidance.
- Change filename rules in
  [screenshot_lib/intelligent_filename.py](../screenshot_lib/intelligent_filename.py).
- Change filename model defaults and dispatch in
  [screenshot_lib/filename_models.py](../screenshot_lib/filename_models.py).
- Change Ollama request behavior in
  [screenshot_lib/ollama_models.py](../screenshot_lib/ollama_models.py).
- Change official Apple SDK behavior in
  [screenshot_lib/apple_models.py](../screenshot_lib/apple_models.py).
- Add metadata fields in
  [screenshot_lib/update_metadata.py](../screenshot_lib/update_metadata.py).
- Add focused tests under [tests/](../tests/) for stable behavior that can run
  quickly and offline.
- Run [tests/e2e/e2e_filename_prompt_eval.py](../tests/e2e/e2e_filename_prompt_eval.py)
  to compare live filename models and prompts.

## Known gaps

- Verify Moondream memory use and latency on the target Mac after upstream model
  changes, because the project intentionally tracks current upstream packages and
  unpinned model revisions.
