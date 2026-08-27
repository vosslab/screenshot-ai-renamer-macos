# Agent Orchestration

This project is essentially a pipeline of cooperating agents: OCR, two
vision-language captioners, and a text-only LLM that condenses everything into a
filename. This document explains how they coordinate so you can adjust prompts or
swap in new models confidently.

## Flow Overview

1. **Finder** - `screenshot-renamer.py` scans the target directory for macOS
   screenshots (`Screen*.png`).
2. **OCR Agent** - `screenshot_lib/extract_text.py` runs Tesseract to capture every bit of
   on-screen text. Its output is passed unchanged to downstream agents.
3. **Caption Agents** - `screenshot_lib/generate_caption.py` loads both backends:
   - `moondream` uses the newest model validated for the required Apple MPS
     runtime. That is currently Moondream2; Moondream3 Preview's path requires
     FlexAttention, which PyTorch MPS does not support.
   - `vit-gpt2` produces literal summaries of visible text and layout.
4. **Aggregator** - `_compose_caption_payload()` in `screenshot-renamer.py`
   merges OCR text and all captions, adding a model note that reminds the final
   LLM how to weigh Moondream vs. ViT-GPT2 if both are present.
5. **Filename Agent** - `screenshot_lib/intelligent_filename.py` sends the
   aggregated context through `screenshot_lib/filename_models.py`. Ollama with
   `qwen3.5:27b` is the default; Apple's official `apple-fm-sdk` is a selectable
   provider. The existing filename policy enforces snake_case, a 64-character
   limit, neutral descriptors for people, and an extension-free model result.
6. **Actions** - The script renames the file and writes EXIF metadata so the new
   caption + OCR text stay embedded in the image, while the CLI reports per-image
   durations and adjusts the ETA for the remaining queue.

## Prompt Design

- **OCR block** contains the complete text Tesseract observed.
- **Caption block** contains one section per backend (e.g., "Moondream caption"
  and "Vit Gpt2 caption"). This redundancy gives the filename agent richer
  context for ambiguous screenshots.
- **Model note** retains the established guidance that Moondream is richer while
  ViT-GPT2 is more literal.
- **Filename instructions** retain the existing intent-focused naming rules.
- **Output contract** asks the LLM to put its final slug in a `<filename>` XML
  element while allowing verbose reasoning outside it. The application prefers
  the XML value and retains the previous sanitizer as a compatibility fallback.

## Filename LLM

`screenshot_lib/filename_models.py` is the single authority for filename
model configuration:

- `DEFAULT_FILENAME_BACKEND` selects `ollama` or `apple`.
- `DEFAULT_FILENAME_MODEL` selects the installed Ollama model.
- `FILENAME_MODEL_THINKING` remains enabled for filename generation.
- Filename requests allow the model to determine its full response length.

`screenshot_lib/ollama_models.py` sends stable policy as a system message and the
task plus evidence as a user message. It disables streaming, keeps the thinking
trace separate, and returns the final answer content for XML extraction by
`screenshot_lib/intelligent_filename.py`.

`screenshot_lib/apple_models.py` uses Apple's official `apple_fm_sdk` module.
It checks system-model availability, opens a short-lived language-model session,
and returns unrestricted response text to the same XML extraction path.

## Extending the Agents

- **Add new captioners** by extending `screenshot_lib/generate_caption.py` with another
  backend and invoking it from `screenshot-renamer.py` alongside the defaults.
- **Customize filename models** by editing the centralized constants in
  `screenshot_lib/filename_models.py`. Keep stable model settings in these
  constants and reserve the production CLI for frequent per-run choices.
- **Evaluate prompt changes** with `tests/e2e/e2e_filename_prompt_eval.py`
  before changing defaults.
- **Metadata** - if you add extra context, update `screenshot_lib/update_metadata.py` to
  embed it so Spotlight / Photos can search for it later.

Keep this file updated whenever the coordination logic changes; it's the quick
reference for anyone debugging or tuning the agent stack.

`install_models.py` validates both current caption models before it deletes any
explicitly retired project-model repositories from the Hugging Face cache. Keep
the retired allowlist narrow; never purge unrelated Hugging Face or Ollama models.

## Human guidance

See [docs/HUMAN_GUIDANCE.md](docs/HUMAN_GUIDANCE.md) for durable model-provider
and installation preferences stated by the project owner.

## Coding Style
See Python coding style in docs/PYTHON_STYLE.md.
See Markdown style in docs/MARKDOWN_STYLE.md.
See repo style in docs/REPO_STYLE.md.
When making edits, document them in docs/CHANGELOG.md.
Agents may run programs in the tests folder, including smoke tests and pyflakes/mypy runner scripts.
Implement clear requested changes and continue through their verification.
Run tests after code changes and use focused documentation checks for documentation-only edits.

## Environment
Codex must run Python using `/opt/homebrew/opt/python@3.12/bin/python3.12` (use Python 3.12 only).
On this user's macOS (Homebrew Python 3.12), Python modules are installed to `/opt/homebrew/lib/python3.12/site-packages/`.
