# Changelog

## 2026-08-25

### Additions and New Features
- Add a configurable filename-model provider layer backed by Ollama and Apple's
  official `apple-fm-sdk`.
- Default filename generation to the installed `qwen3.5:27b` Ollama model with
  thinking enabled.
- Add focused filename unit tests and a six-case live semantic evaluator for
  model and prompt comparisons.
- Create `screenshot_lib/` for reusable pipeline modules; keep `tools/` for
  standalone commands and remove all imports from `tools/`.

### Behavior or Interface Changes
- Keep the existing filename-selection rules and Moondream-versus-ViT source
  guidance while changing the result envelope to `<filename>` XML.
- Allow verbose model reasoning outside the XML element. Prefer the parsed XML
  value and retain the previous sanitizer when a response omits usable XML.
- Keep Ollama thinking enabled and remove repository-imposed generation-token
  caps from local filename requests.
- Keep model configuration out of the production CLI; centralize the backend
  and model constants in `screenshot_lib/filename_models.py`.
- Clarify that custom caption questions apply to Moondream while ViT-GPT2
  remains literal. Caption model selection and MPS compatibility are unchanged.

### Fixes and Maintenance
- Declare the Ollama Homebrew formula and Python client dependencies.
- Parse model-supplied XML with a hardened `lxml` parser.
- Enable the canonical repo-root `PYTHONPATH` extension so standalone commands
  under `tools/` can import `screenshot_lib` after sourcing `source_me.sh`.
- Refresh install, usage, architecture, file-structure, troubleshooting,
  README, and agent-pipeline documentation.

### Removals and Deprecations
- Remove all imports, dependencies, and compatibility paths for the deprecated
  third-party `apple-foundation-models` package.
- Remove the redundant `tools/intelligent_filename.py` wrapper after moving
  runtime ownership to `screenshot_lib/intelligent_filename.py`; use the live
  E2E evaluator for standalone filename-model experiments.

### Decisions and Failures
- Keep Ollama as the default because `qwen3.5:27b` has passed the filename
  evaluation corpus on the target Mac; retain the official Apple SDK as an
  optional provider for continued evaluation.
- Record that `apple-fm-sdk` 0.2.1 installed successfully and reported the
  system model as available, but a minimal generation request failed with SDK
  status 255. A direct Swift probe exposed underlying native
  `ModelManagerServices.ModelManagerError` code 1008, so the observed failure is
  below the prompt, XML, thinking, and token-budget layers.

### Developer Tests and Notes
- Keep Apple MPS on Moondream2 because Moondream3 Preview still requires
  unsupported FlexAttention operations.
- Confirm `qwen3.5:27b` passed all six live filename evaluation cases in
  315.67 seconds; individual cases took 16.95 to 100.96 seconds.

## 2026-06-16

### Behavior or Interface Changes
- Skip screenshots whose smaller dimension is under 16 px, since they are accidental click-drag captures with no usable content.
- Hard delete captures whose smaller dimension is under 4 px (respecting `--dry-run`), as they are pure garbage.

### Fixes and Maintenance
- Fix a crash where a 2x1 px screenshot reached the ViT-GPT2 backend and raised `ValueError: mean must have 1 elements if it is an iterable, got 3`; the size guard now stops degenerate images before any vision model runs.
- Add the missing type annotations flagged by `tests/test_function_typing.py` across `screenshot-renamer.py`, `tests/conftest.py`, and the `tools/` modules; replace `typing` imports with builtin generics and PEP 604 unions.
- Refresh `docs/CODE_ARCHITECTURE.md` and `docs/FILE_STRUCTURE.md` to match the current test layout, dropping the removed `tests/test_import_requirements.py` reference and the hardcoded interpreter path.

## 2026-05-26
- Add `docs/CODE_ARCHITECTURE.md` and refresh `docs/FILE_STRUCTURE.md` from the current repo layout.
- Remove dependency and model revision pins so installs track current upstream packages and models.
- Add `install_moondream.py` to install dependencies and preload the latest Moondream model.
- Remove the non-pip `exiftool` entry from `pip_requirements.txt`.
- Remove stale `einops` runtime dependency after switching to the latest Moondream model.
- Stop loading a separate Moondream tokenizer during setup because Moondream 3 handles tokenization inside the model.
- Clarify in the Moondream installer that Hugging Face is used for model downloads while caption inference runs locally.
- Select Moondream2 automatically on Apple MPS because Moondream3 Preview's FlexAttention path does not support MPS tensors.
- Load Moondream2 on CPU before moving it to MPS to avoid a Transformers 5 device-map warmup error.
- Add a small Transformers 5 compatibility shim for Moondream2's tied-weight metadata.
- Restore a `transformers<5` compatibility cap because the current Transformers 5 path is broken for Moondream on Apple MPS.
- Reject Apple Foundation Models error text before it can become a screenshot filename.
- Document the Moondream setup step in README, install, and usage docs.

## 2026-01-02
- Add ANSI color output with `--no-color` support for clearer CLI status cues.
- Silence noisy ViT-GPT2 attention mask warnings during caption generation.
- Color ETA lines distinctly from other runtime output.
- Format ETA clock as AM/PM without seconds.
- Skip screenshots that disappear mid-run instead of crashing.
- Print rename actions using basenames with a wrapped `->` line for readability.

## 2025-12-20
- Refresh README structure and shorten the main overview.
- Add install, usage, and troubleshooting docs.
- Update repo documentation guidance and add an authors cleanup.
- Align dependency docs and filenames with `pip_requirements.txt`.
- Add a file structure reference.
- Keep `Brewfile` for standard `brew bundle` discovery and update docs.
