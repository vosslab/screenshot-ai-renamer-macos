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
| Default filename | Model selected in `~/bin/local-model.txt` | Ollama on macOS | Condense OCR and captions into the final filename |
| Optional filename | Apple Foundation Models | macOS system model | System-managed alternative to Ollama |

Dependencies track current stable releases except the owner's temporary
`torch>=2.14,<2.15` compatibility constraint. The bridge requires
`kestrel-mps-torch-ext>=0.1.2`; this release
includes the Torch 2.14 native library. Eager upgrades also refresh compatible
transitive dependencies.

As of 2026-11-11, stable Torch is 2.15.0 but the latest published bridge wheel
(0.1.2) supports only Torch 2.9 through 2.14. Moondream 3.1 is therefore
unavailable with the current stable packages. Use the newest Torch 2.14 release
until upstream publishes a matching bridge wheel, then remove the temporary cap
in `pip_requirements.txt`. The adapter checks the bridge before
loading Photon weights or starting warmup. Normal dependency upgrades will pick
up a newer bridge when published; rerun the installer to validate real inference.

## Mac compatibility

The project requires Apple Silicon and Python 3.12. The upstream Photon runtime
requires an M-series Mac running macOS 13 or later. The application enforces at
least 24 GB of unified memory before attempting Moondream 3.1.

| Mac | Moondream 3.1 Photon | Complete default pipeline |
| --- | --- | --- |
| Less than 24 GB unified memory | Skipped | Use OCR plus ViT-GPT2 MPS and consider a smaller filename model |
| 32 GB M1 MacBook Pro | Eligible; validate the current Photon build | Moondream 3.1 and the model in `~/bin/local-model.txt` may compete for unified memory |
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

The adapter explicitly selects `device="mps:0"` because Kestrel compares its
cache tensors against the fully qualified device. It selects `decode_path="native"`
because the current generated decoder assumes CUDA hardware. These are supported
Photon runtime options. Installed third-party package files are not modified.

The application also installs a process-local transfer-handle adapter from
`screenshot_lib/photon_mps_transfer.py`. Kestrel 0.9.1 starts asynchronous token
copies to CPU memory but uses a no-op completion event on MPS. Reading those
buffers before the GPU finishes produces empty, truncated, or duplicated captions.
The adapter waits for MPS completion before returning token IDs to the scheduler.
It preserves the normal wait for real completion events. Remove this adapter when
upstream provides MPS completion events; no upstream code is compiled locally.
Caption and custom visual-query responses use greedy decoding and up to 192 generated tokens to
keep visual evidence concise for the existing 1200-character quality limit.
The filename model's response length remains unrestricted.

Run real inference after dependency updates. A matching bridge alone does not
prove that the runtime works. Use the documented temporary Torch downgrade for
the current bridge mismatch. Failed captioners are reported and
omitted while OCR and remaining visual evidence continue through the pipeline.

On 2026-11-11 both captioners passed generated-image inference on this 64 GB Mac
with the published Torch 2.14.1 wheel, Torchvision 0.29.2, SDK 2.6.1, and bridge 0.1.2.
After fixing token readback and selecting greedy generation, five test-card
captions, five log-screenshot captions, and two visual queries passed through
the production adapter in a fresh process. Test-card answers described both the
red and blue shapes; screenshot captions described the terminal output. This
checks execution and usable output, not perfect transcription of screenshot text.

On 2026-10-22 both captioners passed generated-image inference with Torch 2.14.1,
Torchvision 0.29.1, SDK 2.6.1, and bridge 0.1.2. A real assessment-settings
screenshot produced an empty Moondream caption; the normal quality check omitted
it and the complete launchd pipeline succeeded using OCR and ViT-GPT2. Runtime
compatibility does not guarantee a usable caption on every image.

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

Ollama with the model in `~/bin/local-model.txt` is the default. Its model files are intentionally not
installed by `install_models.py`:

```bash
ollama pull "$(cat ~/bin/local-model.txt)"
```

The 2026-10-22 evaluation passes all six semantic cases with Qwen 3.6 on
Ollama 0.40.8 in 91 seconds. The shared first case produces comparable filenames
with Qwen 3.5 and 3.6, taking 178 and 22 seconds respectively. The remaining
slow baseline run was stopped; these are not six-case comparative timings.

Ollama must be running during screenshot processing. A smaller installed model
can be selected in `~/bin/local-model.txt`, but it should pass
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
- `tests/test_photon_mps_transfer.py` checks that host token readback waits for
  GPU completion without needing a real GPU or model.

Live `install_models.py` inference, Metal/MPS access, current package imports,
native bridge compatibility, model downloads, and cache-recovery measurements
are implementation or on-demand operational checks. They depend on the current
Mac and installed packages, so they are not permanent pytest cases.

## Configuration ownership

- `~/bin/local-model.txt` selects the shared Ollama filename model.
- `screenshot_lib/model_catalog.py` owns caption model identities and Mac runtime
  requirements, and reads the shared filename preference.
- `screenshot_lib/moondream_photon.py` adapts the Moondream SDK and Photon
  runtime without owning model selection.
- `screenshot_lib/photon_mps_transfer.py` owns the temporary token-readback
  synchronization adapter for the upstream MPS completion-event bug.
- `screenshot_lib/generate_caption.py` owns caption dispatch.
- `screenshot_lib/filename_models.py` owns filename-provider dispatch.
- `pip_requirements.txt` owns runtime dependencies and demonstrated minimum versions.

See the [official Photon local-inference guide](https://docs.moondream.ai/running-locally/)
and the [Moondream 3.1 model card](https://huggingface.co/moondream/moondream3.1-9B-A2B)
for upstream requirements and model capabilities.
