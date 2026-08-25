# Troubleshooting

## Ollama connection failed
- Confirm Ollama is running with `ollama list`.
- Launch the Ollama app or run `ollama serve` in another terminal.
- Confirm the default model is installed with `ollama list`.
- Download a missing default model with `ollama pull qwen3.5:27b`.

## Ollama model is too slow

Thinking remains enabled for filename generation. Evaluate a smaller installed
model with `tests/e2e/e2e_filename_prompt_eval.py --filename-model MODEL` before
changing `DEFAULT_FILENAME_MODEL` in `screenshot_lib/filename_models.py`.

## Apple Foundation Models generation fails

- Confirm macOS 26+, Apple Intelligence, and the system language-model download
  are ready.
- Confirm full Xcode 26+ is selected with `xcode-select -p`; the official
  `apple-fm-sdk` package includes a native bridge.
- Test one committed case with
  `tests/e2e/e2e_filename_prompt_eval.py --filename-backend apple --case
  invoice_source_conflict`.
- If availability succeeds but generation raises status 255, do not tune the
  filename prompt, XML instructions, thinking, or a response-token limit. On the
  target Mac, a direct Swift probe traced this symptom to native
  `ModelManagerServices.ModelManagerError` code 1008. Recheck the macOS model
  service after system or Xcode updates; Ollama remains the working default.

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

## Moondream3 FlexAttention error on MPS

Moondream3 Preview's Transformers path uses FlexAttention, which does not run on
PyTorch MPS. On Apple Silicon, the repo uses Moondream2 for the local Moondream
caption backend. Use `./install_moondream.py` after dependency or model changes
to preload the compatible model for the active device.
