# Troubleshooting

Use `docs/MODELS.md` to distinguish model limitations, unified-memory limits,
accelerator availability, and native Python ABI failures.

## Ollama connection failed
- Confirm Ollama is running with `ollama list`.
- Launch the Ollama app or run `ollama serve` in another terminal.
- Confirm the default model is installed with `ollama list`.
- Download a missing default model with `ollama pull qwen3.5:27b`.

## Ollama model is too slow

Thinking remains enabled for filename generation. Evaluate a smaller installed
model by changing `QWEN_FILENAME_MODEL` in
`screenshot_lib/model_catalog.py`, then run the committed E2E filename cases
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

All generation runs on-device. Close other GPU-heavy apps. Moondream 3.1 fits on
Apple Silicon with at least 24 GB, but running it alongside the default
`qwen3.5:27b` filename model can create additional memory pressure on 32 GB and
36 GB Macs. Close other GPU-heavy applications or select a smaller Ollama model
in `screenshot_lib/model_catalog.py` if the complete pipeline swaps heavily.

## Apple MPS is unavailable

ViT-GPT2 requires Apple GPU acceleration through PyTorch MPS. The application
intentionally does not fall back to CPU or CUDA. Confirm the Mac uses Apple
Silicon and that Python is loading the macOS arm64 PyTorch build:

```bash
source source_me.sh && python -c \
	'import torch; print(torch.backends.mps.is_built(), torch.backends.mps.is_available())'
```

Both values must be `True`. If MPS is built but unavailable, run the command in
the normal macOS terminal rather than a restricted environment that cannot
access Metal devices.

## Moondream3 Preview FlexAttention error

Moondream3 Preview's Transformers path uses FlexAttention, which does not run on
PyTorch MPS. The application uses Moondream 3.1 through the official Photon
Metal runtime instead. After dependency or model changes, validate all caption
paths:

```bash
source source_me.sh && python install_models.py
```

## Photon is unavailable

The CLI reports the reason when Photon setup, inference, or caption validation
fails. Run `install_models.py` to reproduce the failure with a small validation
image. The screenshot pipeline continues with OCR and ViT-GPT2 MPS. Empty,
runaway, or repetitive output is rejected rather than forwarded to the filename
model.

If Photon reports that `kestrel-mps-torch-ext` does not support the installed
PyTorch minor, the installed environment predates the current dependency
constraints or contains packages installed outside this project. Run
`install_models.py` without `--skip-pip`. It selects a Torch 2.12 patch and the
paired Torchvision 0.27 patch before validating Photon again.

Moondream2 is not used as a fallback. Live validation produced a 2,706-character
repeated-token collapse, so the pre-production backend and its Transformers shim
were removed instead of retained as legacy compatibility code.

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
