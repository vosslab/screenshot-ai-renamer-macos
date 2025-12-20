# Troubleshooting

## Apple Intelligence unavailable
- Confirm the Mac is Apple Silicon (arm64).
- Confirm macOS is 26.0 or newer and Apple Intelligence is enabled.
- Run the unit test to verify connectivity: `./screenshot-renamer.py -t`.

## Tesseract not found
If OCR fails with a Tesseract error, install it with Homebrew:
```bash
brew install tesseract
```

## Context window exceeded
Prompts are trimmed automatically, but if you still see context errors, reduce the caption prompt or split large batches.

## Slow or hot GPU
All generation runs on-device. Close other GPU-heavy apps and reduce batch size.
