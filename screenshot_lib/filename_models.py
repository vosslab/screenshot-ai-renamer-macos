"""Configure and run the local text model used for screenshot filenames."""

APPLE_FILENAME_BACKEND = "apple"
OLLAMA_FILENAME_BACKEND = "ollama"
SUPPORTED_FILENAME_BACKENDS = (
	OLLAMA_FILENAME_BACKEND,
	APPLE_FILENAME_BACKEND,
)
DEFAULT_FILENAME_BACKEND = OLLAMA_FILENAME_BACKEND
DEFAULT_FILENAME_MODEL = "qwen3.5:27b"
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
	resolved_backend = DEFAULT_FILENAME_BACKEND if backend is None else backend.strip().lower()
	if resolved_backend not in SUPPORTED_FILENAME_BACKENDS:
		choices = ", ".join(SUPPORTED_FILENAME_BACKENDS)
		raise ValueError(f"Unknown filename backend '{resolved_backend}'. Choose from: {choices}.")
	return resolved_backend


#============================================
def resolve_ollama_model(model: str | None) -> str:
	"""Resolve the installed Ollama model used for filename generation."""
	if model is None:
		return DEFAULT_FILENAME_MODEL
	model_name = model.strip()
	if not model_name:
		raise ValueError("The filename model name cannot be empty.")
	return model_name


#============================================
def _validate_model_override(backend: str, model: str | None) -> None:
	"""Reject model names for providers whose model is selected by the OS."""
	if backend == APPLE_FILENAME_BACKEND and model is not None:
		raise ValueError("Apple Foundation Models uses the system model and accepts no model name.")


#============================================
def describe_filename_model(
	backend: str | None = None,
	model: str | None = None,
) -> str:
	"""
	Return a concise human-readable filename model description.

	Args:
		backend: Optional provider override.
		model: Optional Ollama model override.

	Returns:
		A model description for CLI status output.
	"""
	resolved_backend = normalize_filename_backend(backend)
	_validate_model_override(resolved_backend, model)
	if resolved_backend == APPLE_FILENAME_BACKEND:
		return "Apple Foundation Models (official apple-fm-sdk)"
	resolved_model = resolve_ollama_model(model)
	return f"Ollama {resolved_model} (thinking enabled)"


#============================================
def run_filename_model(
	prompt: str,
	instructions: str,
	*,
	backend: str | None = None,
	model: str | None = None,
) -> str:
	"""
	Run the configured filename model through its provider adapter.

	Args:
		prompt: Filename task and screenshot evidence.
		instructions: Stable system instructions for the filename task.
		backend: Optional provider override.
		model: Optional Ollama model override.

	Returns:
		The model's complete response text.
	"""
	resolved_backend = normalize_filename_backend(backend)
	_validate_model_override(resolved_backend, model)
	if resolved_backend == APPLE_FILENAME_BACKEND:
		import screenshot_lib.apple_models

		return screenshot_lib.apple_models.run_apple_model(prompt, instructions)

	import screenshot_lib.ollama_models

	resolved_model = resolve_ollama_model(model)
	return screenshot_lib.ollama_models.run_ollama_model(
		prompt,
		instructions,
		resolved_model,
		FILENAME_MODEL_THINKING,
	)


#============================================
def unit_test(
	backend: str | None = None,
	model: str | None = None,
) -> None:
	"""
	Run the configured filename model's availability test.

	Args:
		backend: Optional provider override.
		model: Optional Ollama model override.
	"""
	resolved_backend = normalize_filename_backend(backend)
	_validate_model_override(resolved_backend, model)
	if resolved_backend == APPLE_FILENAME_BACKEND:
		import screenshot_lib.apple_models

		screenshot_lib.apple_models.unit_test()
		return

	import screenshot_lib.ollama_models

	resolved_model = resolve_ollama_model(model)
	screenshot_lib.ollama_models.unit_test(resolved_model, FILENAME_MODEL_THINKING)
