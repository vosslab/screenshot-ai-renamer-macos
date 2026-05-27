# File structure

## Top-level layout

- [AGENTS.md](../AGENTS.md): agent pipeline overview, repo-specific workflow
  rules, and Python execution constraints.
- [Brewfile](../Brewfile): Homebrew system dependencies: ExifTool, Tesseract,
  and libvips.
- [CLAUDE.md](../CLAUDE.md): Claude-specific instructions for environments that
  use that file.
- [LICENSE](../LICENSE): project license.
- [README.md](../README.md): short project overview, quick start, and core
  documentation links.
- [install_moondream.py](../install_moondream.py): installs runtime Python
  dependencies and preloads the local Moondream model for the active device.
- [pip_requirements.txt](../pip_requirements.txt): runtime Python dependencies.
- [pip_requirements-dev.txt](../pip_requirements-dev.txt): developer and test
  dependencies.
- [screenshot-renamer.py](../screenshot-renamer.py): main CLI entry point.
- [docs/](.): durable project documentation and style guides.
- [tools/](../tools/): OCR, captioning, filename, Apple model, metadata, and
  shared image helpers.
- [tests/](../tests/): pytest checks, style gates, and helper scripts.
- [devel/](../devel/): developer maintenance scripts for changelog and release
  workflows.

## Key subtrees

### [tools/](../tools/)

- [tools/common_func.py](../tools/common_func.py): shared device, image resize,
  attention-mask, and image discovery helpers.
- [tools/config_apple_models.py](../tools/config_apple_models.py): Apple
  Foundation Models availability checks and text-generation wrapper.
- [tools/extract_text.py](../tools/extract_text.py): Tesseract OCR helper.
- [tools/generate_caption.py](../tools/generate_caption.py): Moondream and
  ViT-GPT2 caption backend setup and inference.
- [tools/intelligent_filename.py](../tools/intelligent_filename.py): filename
  prompt construction and response validation.
- [tools/update_metadata.py](../tools/update_metadata.py): ExifTool metadata
  writer.

### [tests/](../tests/)

- [tests/conftest.py](../tests/conftest.py): pytest fixtures and repo hygiene
  options.
- [tests/git_file_utils.py](../tests/git_file_utils.py): shared git-root and
  tracked-file helpers for tests.
- [tests/test_import_requirements.py](../tests/test_import_requirements.py):
  import-to-requirements validation.
- [tests/test_bandit_security.py](../tests/test_bandit_security.py): Bandit
  security gate.
- [tests/test_pyflakes_code_lint.py](../tests/test_pyflakes_code_lint.py):
  pyflakes gate.
- [tests/test_indentation.py](../tests/test_indentation.py),
  [tests/test_whitespace.py](../tests/test_whitespace.py), and
  [tests/test_ascii_compliance.py](../tests/test_ascii_compliance.py): file
  hygiene checks.
- Focused filename tests: filename response validation checks.
- [tests/TESTS_README.md](../tests/TESTS_README.md): test layout and execution
  notes.

### [devel/](../devel/)

- [devel/changelog_lib.py](../devel/changelog_lib.py): shared changelog parsing
  and git helpers.
- [devel/query_changelog.py](../devel/query_changelog.py): changelog query
  utility.
- [devel/rotate_changelog.py](../devel/rotate_changelog.py): active changelog
  rotation utility.
- [devel/commit_changelog.py](../devel/commit_changelog.py): commit-message seed
  helper based on changelog entries.
- [devel/bump_version.py](../devel/bump_version.py): version maintenance helper.
- [devel/submit_to_pypi.py](../devel/submit_to_pypi.py): package publishing
  helper.
- [devel/dist_clean.sh](../devel/dist_clean.sh): distribution cleanup helper.

## Generated artifacts

- Screenshot image files (`*.png`) are ignored by [.gitignore](../.gitignore).
- Python bytecode and cache folders such as `__pycache__/`, `.pytest_cache/`,
  `.mypy_cache/`, and `.ruff_cache/` are ignored.
- Build and packaging outputs such as `build/`, `dist/`, `*.egg-info/`, and
  wheel folders are ignored.
- Repo hygiene reports named `report_*.txt` are ignored.
- Scratch files matching `_temp*.?*` are ignored.
- Hugging Face model downloads are cached outside the repo by the Hugging Face
  tooling, not tracked here.

## Documentation map

- [docs/CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md): component overview and
  primary data flow.
- [docs/FILE_STRUCTURE.md](FILE_STRUCTURE.md): this file map.
- [docs/INSTALL.md](INSTALL.md): setup requirements and install steps.
- [docs/USAGE.md](USAGE.md): CLI usage and examples.
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md): common failures and fixes.
- [docs/CHANGELOG.md](CHANGELOG.md): dated change history.
- [docs/E2E_TESTS.md](E2E_TESTS.md): end-to-end test layout conventions.
- [docs/REPO_STYLE.md](REPO_STYLE.md), [docs/PYTHON_STYLE.md](PYTHON_STYLE.md),
  [docs/PYTEST_STYLE.md](PYTEST_STYLE.md), and
  [docs/MARKDOWN_STYLE.md](MARKDOWN_STYLE.md): repo style and test conventions.
- [docs/CLAUDE_HOOK_USAGE_GUIDE.md](CLAUDE_HOOK_USAGE_GUIDE.md): generated
  Claude hook reference.
- [docs/AUTHORS.md](AUTHORS.md): authorship and maintainer information.

## Where to add new work

- Add runtime helpers under [tools/](../tools/) when they support the screenshot
  pipeline.
- Add repo-level CLI scripts at the root when they are user-facing and
  single-purpose.
- Add developer maintenance automation under [devel/](../devel/).
- Add fast deterministic pytest checks under [tests/](../tests/).
- Add durable user or developer documentation under [docs/](.) using
  SCREAMING_SNAKE_CASE filenames.
- Keep generated image outputs, reports, caches, and scratch files out of git.
