import logging
import time

import torch
import transformers
import transformers.dynamic_module_utils
import PIL.Image

import screenshot_lib.common_func

MOONDREAM2_MODEL_ID = "vikhyatk/moondream2"
VIT_GPT2_MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"
VIT_PROCESSOR_MODEL_ID = "google/vit-base-patch16-224-in21k"
GPT2_TOKENIZER_MODEL_ID = "gpt2"


#============================================
class _CompatibleVisionEncoderDecoderModel(transformers.VisionEncoderDecoderModel):
	"""Ignore obsolete non-learned attention buffers in the ViT-GPT2 checkpoint."""

	_keys_to_ignore_on_load_unexpected = [
		r"decoder\.transformer\.h\.\d+\.(attn|crossattention)\.masked_bias",
	]


#============================================
def _caption_with_moondream(image_path: str, ai_components: dict) -> str:
	"""Run caption generation using the latest Moondream remote-code model."""
	image = PIL.Image.open(image_path).convert("RGB")
	image = screenshot_lib.common_func.resize_image(image, ai_components.get("max_dimension", 720))

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
	image = screenshot_lib.common_func.resize_image(image, ai_components.get("max_dimension", 1280))

	device = ai_components["device"]
	feature_extractor = ai_components["feature_extractor"]
	model = ai_components["model"]
	tokenizer = ai_components["tokenizer"]

	pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
	attention_mask = screenshot_lib.common_func.get_attention_mask(pixel_values, device)

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
def _get_moondream2_tied_weights_keys(model: object) -> dict:
	"""
	Return tied-weight metadata assigned by Transformers or declared by Moondream2.
	"""
	assigned_key = "_moondream2_all_tied_weights_keys"
	if assigned_key in model.__dict__:
		return model.__dict__[assigned_key]

	tied_keys = getattr(model, "_tied_weights_keys", None) or []
	if isinstance(tied_keys, dict):
		return tied_keys
	key_map = {key: key for key in tied_keys}
	return key_map


#============================================
def _set_moondream2_tied_weights_keys(model: object, tied_weights_keys: dict) -> None:
	"""
	Store tied-weight metadata assigned during Transformers model initialization.
	"""
	model.__dict__["_moondream2_all_tied_weights_keys"] = tied_weights_keys


#============================================
def _load_moondream_model(model_id: str, model_args: dict) -> object:
	"""
	Load Moondream while limiting its compatibility shim to model construction.
	"""
	if model_id != MOONDREAM2_MODEL_ID:
		model = transformers.AutoModelForCausalLM.from_pretrained(  # nosec B615
			model_id,
			**model_args,
		)
		return model

	config = transformers.AutoConfig.from_pretrained(  # nosec B615
		model_id,
		trust_remote_code=True,
	)
	class_reference = config.auto_map["AutoModelForCausalLM"]
	model_class = transformers.dynamic_module_utils.get_class_from_dynamic_module(
		class_reference,
		model_id,
	)
	if not hasattr(model_class, "all_tied_weights_keys"):
		model_class.all_tied_weights_keys = property(
			_get_moondream2_tied_weights_keys,
			_set_moondream2_tied_weights_keys,
		)
	model = model_class.from_pretrained(  # nosec B615
		model_id,
		config=config,
		**model_args,
	)
	return model


#============================================
def _load_vit_gpt2_model() -> transformers.VisionEncoderDecoderModel:
	"""Load ViT-GPT2 while ignoring only its obsolete attention-mask buffers."""
	model = _CompatibleVisionEncoderDecoderModel.from_pretrained(  # nosec B615
		VIT_GPT2_MODEL_ID
	)
	return model


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
	device = screenshot_lib.common_func.get_mps_device()

	if backend == "vit-gpt2":
		_suppress_transformers_generation_warnings()
		model = _load_vit_gpt2_model()
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

	model_id = MOONDREAM2_MODEL_ID
	model_args = {
		"trust_remote_code": True,
		"dtype": torch.float16,
		"device_map": {"": device},
	}
	model = _load_moondream_model(model_id, model_args)
	model.to(device)

	components = {
		"backend": "moondream",
		"model_id": model_id,
		"model": model,
		"device": device,
		"prompt": prompt,
		"max_dimension": 720,
	}
	return components
