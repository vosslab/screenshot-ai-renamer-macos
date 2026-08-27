"""Configure and run the local text model used for screenshot filenames."""

import screenshot_lib.model_catalog

APPLE_FILENAME_BACKEND = "apple"
OLLAMA_FILENAME_BACKEND = "ollama"
SUPPORTED_FILENAME_BACKENDS = (
	OLLAMA_FILENAME_BACKEND,
	APPLE_FILENAME_BACKEND,
)
DEFAULT_FILENAME_BACKEND = OLLAMA_FILENAME_BACKEND
FILENAME_MODEL_THINKING = True


#============================================
def normalize_filename_backend(backend: str | None) -> str:
	"""
	Resolve and validate a filename provider name.

	Args:
		backend: Optional provider override.

	Returns:
		A normalized provider name.
	"""
	if backend is None:
		resolved_backend = DEFAULT_FILENAME_BACKEND
	else:
		resolved_backend = backend.strip().lower()
	if resolved_backend not in SUPPORTED_FILENAME_BACKENDS:
		choices = ", ".join(SUPPORTED_FILENAME_BACKENDS)
		raise ValueError(f"Unknown filename backend '{resolved_backend}'. Choose from: {choices}.")
	return resolved_backend


#============================================
def describe_filename_model(
	backend: str | None = None,
) -> str:
	"""
	Return a concise human-readable filename model description.

	Args:
		backend: Optional provider override.

	Returns:
		A model description for CLI status output.
	"""
	resolved_backend = normalize_filename_backend(backend)
	if resolved_backend == APPLE_FILENAME_BACKEND:
		description = "Apple Foundation Models (official apple-fm-sdk)"
	else:
		model_id = screenshot_lib.model_catalog.QWEN_FILENAME_MODEL.model_id
		description = f"Ollama {model_id} (thinking enabled)"
	return description


#============================================
def run_filename_model(
	prompt: str,
	instructions: str,
	*,
	backend: str | None = None,
) -> str:
	"""
	Run the configured filename model through its provider adapter.

	Args:
		prompt: Filename task and screenshot evidence.
		instructions: Stable system instructions for the filename task.
		backend: Optional provider override.

	Returns:
		The model's complete response text.
	"""
	resolved_backend = normalize_filename_backend(backend)
	if resolved_backend == APPLE_FILENAME_BACKEND:
		import screenshot_lib.apple_models

		response = screenshot_lib.apple_models.run_apple_model(prompt, instructions)
		return response

	import screenshot_lib.ollama_models

	response = screenshot_lib.ollama_models.run_ollama_model(
		prompt,
		instructions,
		screenshot_lib.model_catalog.QWEN_FILENAME_MODEL.model_id,
		FILENAME_MODEL_THINKING,
	)
	return response


#============================================
def unit_test(
	backend: str | None = None,
) -> None:
	"""
	Run the configured filename model's availability test.

	Args:
		backend: Optional provider override.
	"""
	resolved_backend = normalize_filename_backend(backend)
	if resolved_backend == APPLE_FILENAME_BACKEND:
		import screenshot_lib.apple_models

		screenshot_lib.apple_models.unit_test()
		return

	import screenshot_lib.ollama_models

	model_id = screenshot_lib.model_catalog.QWEN_FILENAME_MODEL.model_id
	screenshot_lib.ollama_models.unit_test(model_id, FILENAME_MODEL_THINKING)
