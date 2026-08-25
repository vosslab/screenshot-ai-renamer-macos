# Usage

The screenshot renamer scans a directory for macOS `Screen*.png` captures,
extracts OCR text, generates local visual captions, asks the configured local text
model for a filename, and optionally renames the image and embeds metadata.

## Basic commands

Preview changes without renaming files:

```bash
./screenshot-renamer.py --dry-run
```

Process screenshots on the Desktop:

```bash
./screenshot-renamer.py
```

Process another directory:

```bash
./screenshot-renamer.py --directory /path/to/screenshots
```

## Filename models

Ollama with `qwen3.5:27b` is the default filename model. Thinking is always
enabled for Ollama. Apple's official Foundation Models SDK is also available as
an optional provider. Either model may reason verbosely, then places the selected
slug inside a `<filename>` XML element for extraction.

Model choices are intentionally not production CLI flags because they rarely
change between runs. Customize these constants in
[`screenshot_lib/filename_models.py`](../screenshot_lib/filename_models.py):

- `DEFAULT_FILENAME_BACKEND`: `ollama` or `apple`.
- `DEFAULT_FILENAME_MODEL`: any installed Ollama model name.
- `FILENAME_MODEL_THINKING`: remains `True` for filename generation.

The Apple provider uses the OS-selected system model, so
`DEFAULT_FILENAME_MODEL` applies only to Ollama. Neither provider request sets an
output-token budget.

## Caption prompt

Moondream uses its normal caption mode unless a custom question is supplied:

```bash
./screenshot-renamer.py --caption-prompt "Describe the screenshot's main task and application."
```

The custom question applies to Moondream. ViT-GPT2 remains a literal caption
backend and does not accept text prompts. Apple MPS continues to use Moondream2
because Moondream3 Preview requires unsupported FlexAttention operations.

## CLI options

| Flag | Description |
| --- | --- |
| `-d`, `--directory <path>` | Screenshot directory; defaults to `~/Desktop` |
| `-n`, `--dry-run` | Preview renames and tiny-image deletion without modifying files |
| `-t`, `--unit-test` | Verify the configured filename model with a math prompt |
| `--caption-prompt` | Supply a custom Moondream caption question |
| `--no-color` | Disable ANSI color output |

## Filename prompt evaluation

Run the committed semantic evaluation cases against the default model:

```bash
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py
```

Compare a candidate model on one case without changing production configuration:

```bash
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py \
	--filename-model qwen3.5:27b \
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
