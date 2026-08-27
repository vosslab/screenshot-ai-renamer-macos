# Changelog

## 2026-08-27

### Behavior or Interface Changes
- Preload both production image-caption backends during setup: the compatible
  Moondream model plus ViT-GPT2 and its processor and tokenizer.
- Rename the caption-model setup command to `install_models.py` and update the
  active documentation routes to match its broader responsibility.
- Render model setup with Rich panels, ASCII section rules, and consistent status
  labels for dependencies, Apple acceleration, model loading, cleanup, and success.
- Require Apple MPS for local PyTorch caption inference instead of silently
  falling back to CPU or CUDA.
- After both current caption models load successfully, purge explicitly retired
  project models from the Hugging Face cache while preserving active revisions,
  unrelated Hugging Face models, and Ollama models.

### Fixes and Maintenance
- Declare Torchvision as a direct runtime dependency so pip upgrades it with
  Torch instead of retaining an incompatible previously installed wheel.
- Make the Moondream installer upgrade the complete dependency set before model
  preload, preventing stale Torchvision native extensions from breaking
  Transformers imports with a missing `torchvision::nms` operator.
- Scope the Moondream2 tied-weights compatibility adapter to Moondream2's
  dynamically loaded model class so the shared Transformers base class remains
  untouched and ViT-GPT2 initializes normally under Transformers 5.
- Filter only the obsolete ViT-GPT2 `masked_bias` checkpoint buffers from its
  load report while preserving all other model compatibility warnings.
- Update Moondream installation and troubleshooting guidance for the supported
  Transformers 5 path, coordinated Torch/Torchvision upgrades, and complete
  image-caption model setup.

### Decisions and Failures
- Keep `ollama pull qwen3.5:27b` separate from `install_models.py` while
  preserving the intended path back to Apple's system filename models.
- Select the newest caption model proven on the required Apple accelerator,
  which keeps Moondream2 in production while Moondream3 Preview requires
  FlexAttention that PyTorch MPS does not support.

### Developer Tests and Notes
- Confirm all 722 fast tests pass under Python 3.12 after the dependency,
  installer, loader, and documentation changes.
- Verify Torch 2.13.0, Torchvision 0.28.0, and Transformers 5.16.1 import
  together; preload Moondream2 followed by ViT-GPT2 in one process; and run a
  real ViT-GPT2 caption against a screenshot successfully.

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
- Keep Ollama model identity in `DEFAULT_FILENAME_MODEL` as the single
  configuration authority; remove the unused per-call model override path.
- Rewrite the filename LLM instructions around desired actions: interpret OCR
  and captions as evidence, select representative thematic terms, use neutral
  functional language, format a snake_case slug, and return it in XML.
- Rewrite operational agent guidance around the intended configuration and
  verification paths while omitting unwanted alternatives.
- Keep the existing filename-selection rules and Moondream-versus-ViT source
  guidance while changing the result envelope to `<filename>` XML.
- Allow verbose model reasoning outside the XML element. Prefer the parsed XML
  value and retain the previous sanitizer when a response omits usable XML.
- Keep Ollama thinking enabled and remove repository-imposed generation-token
  caps from local filename requests.
- Keep model configuration out of the production CLI; centralize the backend
  and model constants in `screenshot_lib/filename_models.py`.
- Remove the E2E evaluator's `--filename-model` argument. Model identity is
  stable configuration rather than a per-run interaction; the evaluator keeps
  only case selection and the provider mode switch.
- Clarify that custom caption questions apply to Moondream while ViT-GPT2
  remains literal. Caption model selection and MPS compatibility are unchanged.

### Fixes and Maintenance
- Document full Xcode 26+ as a baseline installation requirement for building
  the included official `apple-fm-sdk`; Ollama remains the runtime default.
- Route repo-local Python examples through `source source_me.sh && python` so
  installation, usage, and troubleshooting commands use Python 3.12.
- Declare the Ollama Homebrew formula and Python client dependencies.
- Parse model-supplied XML with a hardened `lxml` parser.
- Keep the caption-module import from shadowing the `screenshot_lib` package in
  the main CLI's filename-model unit-test path.
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
- Remove mock-heavy implementation tests and the unapproved external E2E case
  fixture. Keep durable filename behavior in fast pytest and inline the small
  semantic corpus in the manual E2E evaluator.

### Decisions and Failures
- Keep Ollama as the default because `qwen3.5:27b` has passed the filename
  evaluation corpus on the target Mac; retain the official Apple SDK as an
  selectable provider for continued evaluation.
- Record that `apple-fm-sdk` 0.2.1 installed successfully and reported the
  system model as available, but a minimal generation request failed with SDK
  status 255. A direct Swift probe exposed underlying native
  `ModelManagerServices.ModelManagerError` code 1008, so the observed failure is
  below the prompt, XML, thinking, and token-budget layers.

### Developer Tests and Notes
- Complete a fresh six-pass audit covering scope, tests, style, documentation,
  legacy code, and comments. Confirm 684 fast tests pass in 1.22 seconds and the
  simplified default Qwen dispatcher passes its live unit probe in 33.19 seconds.
- Classify live model and provider probes as one-time implementation checks,
  not permanent pytest cases. The manual E2E evaluator remains outside pytest
  for deliberate model and prompt comparisons.
- Retain four permanent, offline filename behavior tests. Confirm the 684-test
  fast lane passes in 1.21 seconds and the inlined `invoice_source_conflict`
  E2E case passes with `qwen3.5:27b` in 58.06 seconds.
- Confirm the positive filename prompt passes all six semantic cases in 515.05
  seconds, with individual cases taking 43.14 to 126.30 seconds. Preserve the
  semantic result and record the slower single-run latency for future comparison
  rather than attributing it to prompt wording without repeated measurements.
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
