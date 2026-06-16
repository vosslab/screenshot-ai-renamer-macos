import logging
import time

import torch
import transformers
import PIL.Image

from tools import common_func

MOONDREAM_MODEL_ID = "moondream/moondream3-preview"
MOONDREAM_MPS_MODEL_ID = "vikhyatk/moondream2"
VIT_GPT2_MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"
VIT_PROCESSOR_MODEL_ID = "google/vit-base-patch16-224-in21k"
GPT2_TOKENIZER_MODEL_ID = "gpt2"


#============================================
def _caption_with_moondream(image_path: str, ai_components: dict) -> str:
	"""Run caption generation using the latest Moondream remote-code model."""
	image = PIL.Image.open(image_path).convert("RGB")
	image = common_func.resize_image(image, ai_components.get("max_dimension", 720))

	if ai_components.get("prompt"):
		caption_result = ai_components["model"].query(
			image=image,
			question=ai_components["prompt"],
			reasoning=False,
		)
		caption = caption_result.get("answer", "")
	else:
		caption_result = ai_components["model"].caption(image, length="normal")
		caption = caption_result.get("caption", "")

	caption_text = caption.strip()
	return caption_text


#============================================
def _caption_with_vit_gpt2(image_path: str, ai_components: dict) -> str:
	"""Run caption generation using the ViT-GPT2 encoder-decoder pipeline."""
	image = PIL.Image.open(image_path).convert("RGB")
	image = common_func.resize_image(image, ai_components.get("max_dimension", 1280))

	device = ai_components["device"]
	feature_extractor = ai_components["feature_extractor"]
	model = ai_components["model"]
	tokenizer = ai_components["tokenizer"]

	pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
	attention_mask = common_func.get_attention_mask(pixel_values, device)

	output_ids = model.generate(
		pixel_values,
		num_beams=4,
		early_stopping=True,
		attention_mask=attention_mask,
		max_new_tokens=32,
	)

	caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
	caption_text = caption.strip()
	return caption_text


#============================================
def _suppress_transformers_generation_warnings() -> None:
	"""Silence noisy generation warnings that do not affect output quality."""
	logger = logging.getLogger("transformers.generation.utils")
	logger.setLevel(logging.ERROR)


#============================================
def _resolve_moondream_model_id(device: str) -> str:
	"""
	Choose the newest Moondream model compatible with the active local device.
	"""
	if device == "mps":
		return MOONDREAM_MPS_MODEL_ID
	return MOONDREAM_MODEL_ID


#============================================
def _resolve_moondream_device(device: str) -> str:
	"""
	Choose a stable local device for Moondream inference.
	"""
	return device


#============================================
def _install_moondream2_transformers_shim() -> None:
	"""
	Add the tied-weights attribute expected by Transformers 5.
	"""
	if hasattr(transformers.PreTrainedModel, "all_tied_weights_keys"):
		return

	def all_tied_weights_keys(model: object) -> dict:
		tied_keys = getattr(model, "_tied_weights_keys", None) or []
		if isinstance(tied_keys, dict):
			return tied_keys
		key_map = {key: key for key in tied_keys}
		return key_map

	transformers.PreTrainedModel.all_tied_weights_keys = property(all_tied_weights_keys)


#============================================
def generate_caption(image_path: str, ai_components: dict) -> str:
	"""Generate a caption for a given image using the configured backend."""
	backend = ai_components.get("backend", "moondream")
	start_time = time.time()

	if backend == "vit-gpt2":
		caption = _caption_with_vit_gpt2(image_path, ai_components)
	else:
		caption = _caption_with_moondream(image_path, ai_components)

	if not caption:
		raise ValueError(f"Caption generation failed for backend '{backend}'.")

	ai_components["_last_caption_runtime"] = time.time() - start_time
	return caption


#============================================
def setup_ai_components(prompt: str = None, backend: str = "moondream") -> dict:
	"""Setup AI components, loading the requested captioning backend."""
	backend = (backend or "moondream").lower()
	device = common_func.get_mps_device()

	if backend == "vit-gpt2":
		_suppress_transformers_generation_warnings()
		model = transformers.VisionEncoderDecoderModel.from_pretrained(VIT_GPT2_MODEL_ID)  # nosec B615
		feature_extractor = transformers.ViTImageProcessor.from_pretrained(VIT_PROCESSOR_MODEL_ID)  # nosec B615
		tokenizer = transformers.GPT2Tokenizer.from_pretrained(GPT2_TOKENIZER_MODEL_ID)  # nosec B615
		model.to(device)

		components = {
			"backend": backend,
			"model": model,
			"feature_extractor": feature_extractor,
			"tokenizer": tokenizer,
			"device": device,
			"prompt": prompt,
			"max_dimension": 1280,
		}
		return components

	model_id = _resolve_moondream_model_id(device)
	if model_id == MOONDREAM_MPS_MODEL_ID:
		_install_moondream2_transformers_shim()
	moondream_device = _resolve_moondream_device(device)
	dtype = torch.float16 if moondream_device == "mps" else torch.bfloat16
	model_args = {
		"trust_remote_code": True,
		"dtype": dtype,
	}
	if moondream_device != "cpu":
		model_args["device_map"] = {"": moondream_device}
	model = transformers.AutoModelForCausalLM.from_pretrained(model_id, **model_args)  # nosec B615
	model.to(moondream_device)

	components = {
		"backend": "moondream",
		"model_id": model_id,
		"model": model,
		"device": moondream_device,
		"prompt": prompt,
		"max_dimension": 720,
	}
	return components
