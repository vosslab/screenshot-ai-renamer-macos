# Agent Orchestration

This project is essentially a pipeline of cooperating agents: OCR, two
vision-language captioners, and a text-only LLM that condenses everything into a
filename. This document explains how they coordinate so you can adjust prompts or
swap in new models confidently.

## Flow Overview

1. **Finder** – `screenshot-renamer.py` scans the target directory for macOS
   screenshots (`Screen*.png`).
2. **OCR Agent** – `tools/extract_text.py` runs Tesseract to capture every bit of
   on-screen text. Its output is passed unchanged to downstream agents.
3. **Caption Agents** – `tools/generate_caption.py` loads both backends:
   - `moondream` excels at context-rich descriptions of UI/visuals.
   - `vit-gpt2` produces literal summaries of visible text and layout.
4. **Aggregator** – `_compose_caption_payload()` in `screenshot-renamer.py`
   merges OCR text and all captions, adding a model note that reminds the final
   LLM how to weigh Moondream vs. ViT-GPT2 if both are present.
5. **Filename Agent** – `tools/intelligent_filename.py` sends the aggregated
   context to Apple Foundation Models via `tools/config_apple_models.py`,
   enforcing snake_case, 64-character limits, neutral descriptors for people, and
   “no extension” rules.
6. **Actions** – The script renames the file and writes EXIF metadata so the new
   caption + OCR text stay embedded in the image, while the CLI reports per-image
   durations and adjusts the ETA for the remaining queue.

## Prompt Design

- **OCR block** is always included verbatim so the filename LLM can reference any
  text that Tesseract saw, even if the caption models missed it.
- **Caption block** contains one section per backend (e.g., “Moondream caption”
  and “Vit Gpt2 caption”). This redundancy gives the filename agent richer
  context for ambiguous screenshots.
- **Model note** clarifies that “Moondream2 tends to produce richer descriptions
  while ViT-GPT2 is literal” whenever both are used. Feel free to edit this
  sentence in `_compose_caption_payload()` if you swap models.
- **Filename instructions** demand snake_case, no extension, and concise intent-
  focused wording. Update `tools/intelligent_filename.py` if you want different
  rules. OCR and caption inputs are trimmed to stay within the Apple Foundation
  Models 4,096-token context window.

## Apple Foundation Models Backend

`tools/config_apple_models.py` wraps the Python bindings for Apple Foundation
Models:

- The code requires an Apple Silicon Mac running macOS 26+ with Apple
  Intelligence enabled.
- `run_apple_model()` opens a short-lived session, executes a text generation
  with low temperature, and retries transient failures.
- `unit_test()` validates availability by solving a simple math prompt.
- If you need structured output or streaming, extend `run_apple_model()` to
  accept schema/stream parameters and pass them through to `Session.generate()`.

## Extending the Agents

- **Add new captioners** by extending `tools/generate_caption.py` with another
  backend and invoking it from `screenshot-renamer.py` alongside the defaults.
- **Customize prompts** by editing `tools/intelligent_filename.py` or exposing
  new CLI arguments. Anything echoed into the prompt will reach the filename LLM.
- **Metadata** – if you add extra context, update `tools/update_metadata.py` to
  embed it so Spotlight / Photos can search for it later.

Keep this file updated whenever the coordination logic changes; it’s the quick
reference for anyone debugging or tuning the agent stack.
## Coding Style
See Python coding style in docs/PYTHON_STYLE.md.
See Markdown style in docs/MARKDOWN_STYLE.md.
See repo style in docs/REPO_STYLE.md.
When making edits, document them in docs/CHANGELOG.md.
Agents may run programs in the tests folder, including smoke tests and pyflakes/mypy runner scripts.
