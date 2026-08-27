# Troubleshooting

## Ollama connection failed
- Confirm Ollama is running with `ollama list`.
- Launch the Ollama app or run `ollama serve` in another terminal.
- Confirm the default model is installed with `ollama list`.
- Download a missing default model with `ollama pull qwen3.5:27b`.

## Ollama model is too slow

Thinking remains enabled for filename generation. Evaluate a smaller installed
model by changing `DEFAULT_FILENAME_MODEL` in
`screenshot_lib/filename_models.py`, then run the committed E2E filename cases
before accepting the new default.

## Apple Foundation Models generation fails

- Confirm macOS 26+, Apple Intelligence, and the system language-model download
  are ready.
- Confirm full Xcode 26+ is selected with `xcode-select -p`; the official
  `apple-fm-sdk` package includes a native bridge.

Test one committed case:

```bash
source source_me.sh && python tests/e2e/e2e_filename_prompt_eval.py \
	--filename-backend apple \
	--case invoice_source_conflict
```

When availability succeeds but generation raises status 255, focus diagnosis
on the macOS model service. On the target Mac, a direct Swift probe traced this
symptom to native `ModelManagerServices.ModelManagerError` code 1008. Recheck
the service after system or Xcode updates; Ollama remains the working default.

## Tesseract not found

If OCR fails with a Tesseract error, install it with Homebrew:
```bash
brew install tesseract
```

## Context window exceeded

The filename model receives complete OCR and caption evidence. If a selected
model reports a context error, choose a model with a larger context window.

## Slow or hot GPU

All generation runs on-device. Close other GPU-heavy apps and reduce batch size.

## Apple MPS is unavailable

The local caption models require Apple GPU acceleration through PyTorch MPS.
The application intentionally does not fall back to CPU or CUDA. Confirm the
Mac uses Apple Silicon and that Python is loading the macOS arm64 PyTorch build:

```bash
source source_me.sh && python -c \
	'import torch; print(torch.backends.mps.is_built(), torch.backends.mps.is_available())'
```

Both values must be `True`. If MPS is built but unavailable, run the command in
the normal macOS terminal rather than a restricted environment that cannot
access Metal devices.

## Moondream3 FlexAttention error on MPS

Moondream3 Preview's Transformers path uses FlexAttention, which does not run on
PyTorch MPS. The repo therefore enforces Moondream2 as the local Moondream
caption backend even while Moondream3 is available. After dependency or model
changes, preload the caption models:

```bash
source source_me.sh && python install_models.py
```

## Torchvision NMS operator is missing

An error such as `RuntimeError: operator torchvision::nms does not exist`
means the installed Torch and Torchvision wheels are incompatible. Upgrade the
declared dependency set together, then preload Moondream again:

```bash
source source_me.sh && python install_models.py
```

## ViT-GPT2 reports unexpected masked-bias keys

Older ViT-GPT2 checkpoints contain non-learned `masked_bias` attention buffers
that current Transformers versions no longer use. The loader filters only those
known-safe keys. Missing learned weights or any other unexpected keys remain
visible as real compatibility warnings.
