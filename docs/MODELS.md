# Models and Mac requirements

This application supports Apple Silicon Macs only. Local caption inference uses
Apple GPU acceleration through Photon Metal or PyTorch MPS. There is no Intel
Mac, CUDA, or automatic CPU caption path.

## Names that are easy to confuse

Moondream model names and Python package versions are independent:

- **Moondream 3.1** is the primary vision model. Its model identifier is
  `moondream3.1-9B-A2B`.
- **Photon** is the native inference engine used to run Moondream 3.1 through
  Metal on a Mac.
- **`moondream`** is the unpinned Python SDK that supplies the Photon API. A
  package version such as `2.1.0` is not a Moondream2 model selection.
- **Kestrel** is Photon's native execution layer. Its MPS bridge must contain a
  binary built for the installed PyTorch major and minor version.
- **Moondream2** is a separate, older vision model. It was removed after live
  validation produced unusable repeated-token output.

Consequently, an error mentioning `moondream 2.1.0` or
`kestrel-mps-torch-ext` can prevent the Moondream 3.1 Photon path even though
the selected model is Moondream 3.1.

## Model stack

| Pipeline stage | Model or tool | Local runtime | Purpose |
| --- | --- | --- | --- |
| OCR | Tesseract | CPU | Extract all visible text for downstream evidence |
| Primary caption | Moondream 3.1 `moondream3.1-9B-A2B` | Photon Metal | Rich visual description and visual questions |
| MPS caption | `nlpconnect/vit-gpt2-image-captioning` | PyTorch MPS | Independent visual evidence when Photon is unavailable |
| Default filename | Ollama `qwen3.5:27b` | Ollama on macOS | Condense OCR and captions into the final filename |
| Optional filename | Apple Foundation Models | macOS system model | System-managed alternative to Ollama |

Most entries in `pip_requirements.txt` remain unpinned. Torch uses
`>=2.12,<2.13`, and Torchvision uses `>=0.27,<0.28`, because Photon's current
native Mac bridge supports the Torch 2.12 ABI and PyTorch pairs that release
with Torchvision 0.27. Patch releases remain free to upgrade within both ranges.

## Mac compatibility

The project requires Apple Silicon and Python 3.12. The upstream Photon runtime
requires an M-series Mac running macOS 13 or later. The application enforces at
least 24 GB of unified memory before attempting Moondream 3.1.

| Mac | Moondream 3.1 Photon | Complete default pipeline |
| --- | --- | --- |
| Less than 24 GB unified memory | Skipped | Use OCR plus ViT-GPT2 MPS and consider a smaller filename model |
| 32 GB M1 MacBook Pro | Eligible; validate the current Photon build | Moondream 3.1 and `qwen3.5:27b` may compete for unified memory |
| 36 GB Mac Studio | Eligible | Expected to fit, but close other GPU-heavy applications and watch swapping |
| 64 GB Mac | Preferred configuration | Best headroom for Photon and the default Ollama model together |

Moondream documents Apple Silicon systems with at least 24 GB for Moondream 3
and notes that Moondream 3 weights exceed the memory of a 16 GB base M4. The 32
GB M1 configuration satisfies the general M-series and application memory
checks, but it is not named in Moondream's published example hardware table.

Unified memory is shared by macOS, the vision models, and Ollama. A model fitting
by itself does not guarantee that the complete pipeline will avoid swapping.
Close other GPU-heavy applications or select a smaller tested Ollama filename
model if the complete pipeline swaps heavily.

## Accelerator requirements

### Photon Metal

Moondream 3.1 runs through custom Metal kernels supplied by Photon. It does not
use CUDA or PyTorch MPS for model execution, but Photon's current Mac stack
includes a PyTorch-minor-specific Kestrel MPS bridge. That native bridge must
provide a matching library for the installed PyTorch minor.

The live environment checked on 2026-08-27 had PyTorch 2.13.0 and
`kestrel-mps-torch-ext` 0.1.1. That bridge wheel contained libraries for PyTorch
2.9, 2.10, 2.11, and 2.12, but not 2.13. This is a native wheel availability
problem, not a Moondream 3.1 model limitation.

With the bounded dependency pair, pip selected Torch 2.12.1 and Torchvision
0.27.1 on the same Mac. Moondream 3.1 then passed a real Photon Metal caption,
and ViT-GPT2 passed a real PyTorch MPS caption.

The repository constrains only the native Torch and Torchvision minor-version
pair. It permits every compatible 2.12 and 0.27 patch release while preventing
pip from upgrading to a Torch minor that the installed Kestrel bridge cannot
load. When a newer bridge adds support for a later Torch minor, these two upper
bounds can advance together.

### PyTorch MPS

ViT-GPT2 requires a PyTorch build with MPS both compiled and available:

```bash
source source_me.sh && python -c \
	'import torch; print(torch.__version__, torch.backends.mps.is_built(), torch.backends.mps.is_available())'
```

Both capability values must be `True`. Torch and Torchvision must come from a
compatible release pair because Transformers imports Torchvision image
operators while loading the caption models.

### Apple Neural Engine

PyTorch does not expose the Apple Neural Engine as a general inference device.
Photon and MPS therefore use the Apple GPU. The optional Apple Foundation Models
provider is managed by macOS; this application does not select which Apple
compute unit the operating system uses.

## Filename model requirements

### Ollama

Ollama with `qwen3.5:27b` is the default. Its model files are intentionally not
installed by `install_models.py`:

```bash
ollama pull qwen3.5:27b
```

Ollama must be running during screenshot processing. A smaller installed model
can be selected in `screenshot_lib/model_catalog.py`, but it should pass
`tests/e2e/e2e_filename_prompt_eval.py` before becoming the default.

### Apple Foundation Models

The optional Apple provider requires macOS 26 or later, Apple Intelligence with
its system model available, and full Xcode 26 or later to build the official
`apple-fm-sdk` bridge. macOS selects and stores the model; there is no repository
model identifier or manual weight download.

## Installation and cache behavior

Install Python dependencies and validate each caption path with a real generated
image:

```bash
source source_me.sh && python install_models.py
```

The installer downloads model weights only when needed. Hugging Face-backed
weights use the Hugging Face cache, and Photon honors `HF_HOME` when it is set.
Ollama maintains a separate model store.

The Hugging Face warning about unauthenticated requests concerns download rate
limits only; caption inference remains local after the files are cached. Set an
optional `HF_TOKEN` when higher Hub download limits are needed.

Cleanup runs only after the required caption paths validate. It removes
explicitly retired Moondream project repositories, including Moondream2 and
Moondream3 Preview, while preserving Photon weights, unrelated Hugging Face
models, and all Ollama models.

## Validation classification

Permanent pytest coverage is limited to deterministic behavior that can regress
without an external model or current package state:

- `tests/test_caption_quality.py` checks acceptance of normal captions and
  rejection of collapsed or runaway output.
- `tests/test_common_func.py` checks the macOS runtime-version boundary.

Live `install_models.py` inference, Metal/MPS access, current package imports,
native bridge compatibility, model downloads, and cache-recovery measurements
are implementation or on-demand operational checks. They depend on the current
Mac and installed packages, so they are not permanent pytest cases.

## Configuration ownership

- `screenshot_lib/model_catalog.py` owns model identities and Mac runtime
  requirements.
- `screenshot_lib/moondream_photon.py` adapts the Moondream SDK and Photon
  runtime without owning model selection.
- `screenshot_lib/generate_caption.py` owns caption dispatch.
- `screenshot_lib/filename_models.py` owns filename-provider dispatch.
- `pip_requirements.txt` owns Python dependencies and the bounded native
  Torch/Torchvision compatibility pair.

See the [official Photon local-inference guide](https://docs.moondream.ai/running-locally/)
and the [Moondream 3.1 model card](https://huggingface.co/moondream/moondream3.1-9B-A2B)
for upstream requirements and model capabilities.
