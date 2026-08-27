import logging
import time

import torch
import transformers

import screenshot_lib.caption_quality
import screenshot_lib.common_func
import screenshot_lib.model_catalog
import screenshot_lib.moondream_photon


#============================================
class _CompatibleVisionEncoderDecoderModel(transformers.VisionEncoderDecoderModel):
	"""Ignore obsolete non-learned attention buffers in the ViT-GPT2 checkpoint."""

	_keys_to_ignore_on_load_unexpected = [
		r"decoder\.transformer\.h\.\d+\.(attn|crossattention)\.masked_bias",
	]


#============================================
def _caption_with_vit_gpt2(image_path: str, ai_components: dict) -> str:
	"""Run caption generation using the ViT-GPT2 encoder-decoder pipeline."""
	import PIL.Image

	image = PIL.Image.open(image_path).convert("RGB")
	image = screenshot_lib.common_func.resize_image(image, ai_components["max_dimension"])
	device = ai_components["device"]
	feature_extractor = ai_components["feature_extractor"]
	model = ai_components["model"]
	tokenizer = ai_components["tokenizer"]
	pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
	decoder_attention_mask = torch.ones(
		(pixel_values.shape[0], 1),
		dtype=torch.long,
		device=device,
	)
	output_ids = model.generate(
		pixel_values,
		num_beams=4,
		early_stopping=True,
		decoder_attention_mask=decoder_attention_mask,
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
def _load_vit_gpt2_model() -> transformers.VisionEncoderDecoderModel:
	"""Load ViT-GPT2 while ignoring only its obsolete attention-mask buffers."""
	model = _CompatibleVisionEncoderDecoderModel.from_pretrained(  # nosec B615
		screenshot_lib.model_catalog.VIT_GPT2_MPS.model.model_id
	)
	return model


#============================================
def generate_caption(image_path: str, ai_components: dict) -> str:
	"""Generate and validate a caption with the configured backend."""
	start_time = time.time()
	if ai_components["backend_family"] == "moondream":
		caption = screenshot_lib.moondream_photon.generate_caption(
			image_path,
			ai_components,
		)
	else:
		caption = _caption_with_vit_gpt2(image_path, ai_components)
	screenshot_lib.caption_quality.require_usable_caption(
		caption,
		ai_components["display_name"],
	)
	ai_components["_last_caption_runtime"] = time.time() - start_time
	return caption


#============================================
def setup_ai_components(prompt: str | None = None, backend: str = "moondream") -> dict:
	"""Load the requested caption backend and return its reusable components."""
	backend_name = backend.lower()
	if backend_name == "moondream":
		components = screenshot_lib.moondream_photon.setup_captioner(prompt)
		components["backend_family"] = "moondream"
		return components

	if backend_name != "vit-gpt2":
		raise ValueError(f"Unknown caption backend: {backend}")

	model_spec = screenshot_lib.model_catalog.VIT_GPT2_MPS
	device = screenshot_lib.common_func.get_mps_device()
	_suppress_transformers_generation_warnings()
	model = _load_vit_gpt2_model()
	feature_extractor = transformers.ViTImageProcessor.from_pretrained(  # nosec B615
		screenshot_lib.model_catalog.VIT_PROCESSOR_MODEL_ID
	)
	tokenizer = transformers.GPT2Tokenizer.from_pretrained(  # nosec B615
		screenshot_lib.model_catalog.GPT2_TOKENIZER_MODEL_ID
	)
	model.to(device)
	components = {
		"backend": model_spec.backend_id,
		"backend_family": "vit-gpt2",
		"display_name": model_spec.display_name,
		"model_id": model_spec.model.model_id,
		"model": model,
		"feature_extractor": feature_extractor,
		"tokenizer": tokenizer,
		"device": device,
		"prompt": prompt,
		"max_dimension": model_spec.max_dimension,
	}
	return components


#============================================
def close_ai_components(ai_components: dict | None) -> None:
	"""Release native caption resources held by one component map."""
	if ai_components is None:
		return
	if ai_components["backend_family"] == "moondream":
		screenshot_lib.moondream_photon.close_captioner(ai_components)
