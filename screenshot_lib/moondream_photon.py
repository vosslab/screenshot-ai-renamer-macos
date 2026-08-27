#============================================
def setup_captioner(prompt: str | None = None) -> dict:
	"""Load Moondream 3.1 through the official Photon Metal runtime."""
	import moondream

	import screenshot_lib.common_func
	import screenshot_lib.model_catalog

	model_spec = screenshot_lib.model_catalog.MOONDREAM31_PHOTON
	screenshot_lib.common_func.require_apple_silicon()
	screenshot_lib.common_func.require_macos_version(
		model_spec.runtime.minimum_macos_major,
		model_spec.display_name,
	)
	total_memory = screenshot_lib.common_func.get_total_memory_bytes()
	if total_memory < model_spec.runtime.minimum_memory_bytes:
		available_gib = total_memory / 1024 ** 3
		raise RuntimeError(
			f"Moondream 3.1 Photon requires at least 24 GB of unified memory; "
			f"this Mac reports {available_gib:.0f} GB."
		)
	model = moondream.photon(model_spec.model.model_id)
	components = {
		"backend": model_spec.backend_id,
		"display_name": model_spec.display_name,
		"model_id": model_spec.model.model_id,
		"model": model,
		"prompt": prompt,
		"max_dimension": model_spec.max_dimension,
	}
	return components


#============================================
def generate_caption(image_path: str, components: dict) -> str:
	"""Generate one caption or custom visual answer with Photon."""
	import PIL.Image

	import screenshot_lib.common_func

	image = PIL.Image.open(image_path).convert("RGB")
	image = screenshot_lib.common_func.resize_image(image, components["max_dimension"])
	if components["prompt"]:
		result = components["model"].query(image, components["prompt"])
		caption = result["answer"]
	else:
		result = components["model"].caption(image)
		caption = result["caption"]
	caption_text = caption.strip()
	return caption_text


#============================================
def close_captioner(components: dict) -> None:
	"""Release Photon's native Metal engine when the caller is finished."""
	close_model = getattr(components["model"], "close", None)
	if callable(close_model):
		close_model()
