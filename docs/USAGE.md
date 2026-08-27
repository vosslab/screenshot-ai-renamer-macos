# Usage

The screenshot renamer scans a directory for macOS `Screen*.png` captures,
extracts OCR text, generates local visual captions, asks the configured local text
model for a filename, and optionally renames the image and embeds metadata.

## Basic commands

Preview changes without renaming files:

```bash
source source_me.sh && python screenshot-renamer.py --dry-run
```

Process screenshots on the Desktop:

```bash
source source_me.sh && python screenshot-renamer.py
```

Process another directory:

```bash
source source_me.sh && python screenshot-renamer.py --directory /path/to/screenshots
```

Process screenshots in random order:

```bash
source source_me.sh && python screenshot-renamer.py --shuffle
```

## Filename models

Ollama with `qwen3.5:27b` is the default filename model. Thinking is always
enabled for Ollama. Apple's official Foundation Models SDK is also available as
a selectable provider. Ollama may reason verbosely, then places the selected slug
inside a `<filename>` XML element. Both provider adapters return complete
response text to the shared XML extraction path.

See `docs/MODELS.md` before changing a model or moving the pipeline to another
Apple Silicon Mac.

Model choices are intentionally not production CLI flags because they rarely
change between runs. Customize the model identity in
`screenshot_lib/model_catalog.py` and provider behavior in
[`screenshot_lib/filename_models.py`](../screenshot_lib/filename_models.py):

- `DEFAULT_FILENAME_BACKEND`: `ollama` or `apple`.
- `QWEN_FILENAME_MODEL`: the installed Ollama model identity.
- `FILENAME_MODEL_THINKING`: remains `True` for filename generation.

The Apple provider uses the OS-selected system model, so
`QWEN_FILENAME_MODEL` applies only to Ollama. Neither provider request sets an
output-token budget.

## Caption prompt

Moondream uses its normal caption mode unless a custom question is supplied:

```bash
source source_me.sh && python screenshot-renamer.py \
	--caption-prompt "Describe the screenshot's main task and application."
```

The custom question applies to whichever Moondream runtime is active. ViT-GPT2
remains a literal caption backend and does not accept text prompts. Moondream 3.1
uses Photon Metal. If Photon is unavailable, the pipeline omits its result and
continues with OCR plus ViT-GPT2 through PyTorch MPS.

## CLI options

| Flag | Description |
| --- | --- |
| `-d`, `--directory <path>` | Screenshot directory; defaults to `~/Desktop` |
| `-n`, `--dry-run` | Preview renames and tiny-image deletion without modifying files |
| `-S`, `--shuffle` | Process screenshots in random order |
| `-t`, `--unit-test` | Verify the configured filename model with a math prompt |
| `--caption-prompt` | Supply a custom Moondream caption question |
| `--no-color` | Disable ANSI color output |

## Filename prompt evaluation

Run the committed semantic evaluation cases against the default model:

```bash
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py
```

Evaluate one case after changing the centralized model configuration:

```bash
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py \
	--case invoice_source_conflict
```

Probe the official Apple provider on one case:

```bash
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py \
	--filename-backend apple \
	--case invoice_source_conflict
```

The evaluator checks filename format, expected and forbidden semantic concepts,
an injection-themed regression case, and per-case latency. It runs outside
pytest because it loads a real local model and may take several minutes.
