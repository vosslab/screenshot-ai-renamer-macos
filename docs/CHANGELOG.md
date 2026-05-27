# Changelog

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
