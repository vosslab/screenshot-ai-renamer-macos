"""Model identities and Mac-specific runtime requirements."""

import dataclasses


GIBIBYTE = 1024 ** 3


#============================================
@dataclasses.dataclass(frozen=True, slots=True)
class ModelIdentity:
	"""Identify model weights independently of the SDK that executes them."""

	display_name: str
	model_id: str


#============================================
@dataclasses.dataclass(frozen=True, slots=True)
class MacRuntimeRequirements:
	"""Describe the Mac execution environment required by one runtime."""

	runtime_id: str
	accelerator: str
	minimum_macos_major: int
	minimum_memory_bytes: int


#============================================
@dataclasses.dataclass(frozen=True, slots=True)
class CaptionBackendSpec:
	"""Bind one model identity to one runtime adapter and caption contract."""

	backend_id: str
	display_name: str
	model: ModelIdentity
	runtime: MacRuntimeRequirements
	max_dimension: int


PHOTON_METAL_RUNTIME = MacRuntimeRequirements(
	runtime_id="photon",
	accelerator="metal",
	minimum_macos_major=13,
	minimum_memory_bytes=24 * GIBIBYTE,
)

PYTORCH_MPS_RUNTIME = MacRuntimeRequirements(
	runtime_id="mps",
	accelerator="mps",
	minimum_macos_major=12,
	minimum_memory_bytes=0,
)

MOONDREAM31_MODEL = ModelIdentity(
	display_name="Moondream 3.1",
	model_id="moondream3.1-9B-A2B",
)

VIT_GPT2_MODEL = ModelIdentity(
	display_name="ViT-GPT2",
	model_id="nlpconnect/vit-gpt2-image-captioning",
)

QWEN_FILENAME_MODEL = ModelIdentity(
	display_name="Qwen 3.5 27B",
	model_id="qwen3.5:27b",
)


MOONDREAM31_PHOTON = CaptionBackendSpec(
	backend_id="moondream3.1-photon",
	display_name="Moondream 3.1 / Photon Metal",
	model=MOONDREAM31_MODEL,
	runtime=PHOTON_METAL_RUNTIME,
	max_dimension=1280,
)

VIT_GPT2_MPS = CaptionBackendSpec(
	backend_id="vit-gpt2",
	display_name="ViT-GPT2 / PyTorch MPS",
	model=VIT_GPT2_MODEL,
	runtime=PYTORCH_MPS_RUNTIME,
	max_dimension=1280,
)

VIT_PROCESSOR_MODEL_ID = "google/vit-base-patch16-224-in21k"
GPT2_TOKENIZER_MODEL_ID = "gpt2"
CAPTION_MODELS = (
	MOONDREAM31_PHOTON,
	VIT_GPT2_MPS,
)
