# Standard Library
import types

# PIP3 modules
import pytest

# local repo modules
import screenshot_lib.apple_models
import screenshot_lib.filename_models
import screenshot_lib.intelligent_filename
import screenshot_lib.ollama_models
import screenshot_lib.xml_response


#============================================
def test_filename_response_normalizes_separators() -> None:
	"""The established sanitizer still normalizes spaces and case."""
	result = screenshot_lib.intelligent_filename._sanitize_filename_response(
		"Quarterly Results Review.png"
	)
	assert result == "quarterly_results_review.png"


#============================================
def test_filename_xml_is_extracted_after_model_prose() -> None:
	"""Surrounding model prose does not affect the parsed filename value."""
	response = "I considered the OCR and caption.\n<filename>project_notes</filename>"
	filename = screenshot_lib.xml_response.extract_xml_text(response, "filename")
	assert filename == "project_notes"


#============================================
def test_filename_prompt_keeps_naming_rules_and_requests_xml() -> None:
	"""The filename policy is unchanged apart from its parseable result envelope."""
	prompt = screenshot_lib.intelligent_filename._build_filename_prompt("OCR", "caption")
	assert "<filename> XML element" in prompt
	assert prompt.endswith("<filename>snake_case_filename</filename>")


#============================================
def test_filename_prompt_preserves_complete_local_evidence() -> None:
	"""Long OCR and caption clues are not discarded by an artificial context cap."""
	ocr_text = "A" * 2000 + " decisive_ocr_clue"
	caption = "B" * 2000 + " decisive_caption_clue"
	prompt = screenshot_lib.intelligent_filename._build_filename_prompt(ocr_text, caption)
	assert "decisive_ocr_clue" in prompt
	assert "decisive_caption_clue" in prompt


#============================================
def test_missing_xml_falls_back_to_existing_response_handling(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Missing XML does not turn filename generation into a new failure gate."""
	def fake_run_filename_model(
		prompt: str,
		instructions: str,
		*,
		backend: str | None,
		model: str | None,
	) -> str:
		return "Project Notes"

	monkeypatch.setattr(
		screenshot_lib.filename_models,
		"run_filename_model",
		fake_run_filename_model,
	)
	filename = screenshot_lib.intelligent_filename.generate_intelligent_filename("OCR", "caption")
	assert filename == "project_notes.png"


#============================================
def test_custom_ollama_model_is_preserved() -> None:
	"""Callers can select any installed Ollama model name."""
	model = screenshot_lib.filename_models.resolve_ollama_model("custom:7b")
	assert model == "custom:7b"


#============================================
def test_ollama_dispatcher_always_enables_thinking(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Filename generation always enables Ollama thinking."""
	thinking_values = []

	def fake_run_ollama_model(
		prompt: str,
		instructions: str,
		model: str,
		thinking: bool | str,
	) -> str:
		thinking_values.append(thinking)
		return "<filename>project_notes</filename>"

	monkeypatch.setattr(
		screenshot_lib.ollama_models,
		"run_ollama_model",
		fake_run_ollama_model,
	)
	response = screenshot_lib.filename_models.run_filename_model(
		"prompt",
		"instructions",
		backend="ollama",
		model="custom:7b",
	)
	assert response == "<filename>project_notes</filename>"
	assert thinking_values == [True]


#============================================
def test_ollama_request_has_no_generation_token_cap(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The local filename request does not send an output-token limit."""
	calls = []

	def fake_chat(**kwargs: object) -> types.SimpleNamespace:
		calls.append(kwargs)
		message = types.SimpleNamespace(
			content="<filename>project_notes</filename>",
			thinking="reasoning",
		)
		response = types.SimpleNamespace(message=message)
		return response

	monkeypatch.setattr(screenshot_lib.ollama_models.ollama, "chat", fake_chat)
	screenshot_lib.ollama_models.run_ollama_model(
		"prompt",
		"instructions",
		"custom:7b",
		True,
	)
	options = calls[0]["options"]
	assert isinstance(options, dict)
	assert "num_predict" not in options


#============================================
def test_ollama_generation_extracts_xml_from_surrounding_prose(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Ollama responses are parsed by XML instead of bare-text assumptions."""
	def fake_run_filename_model(
		prompt: str,
		instructions: str,
		*,
		backend: str | None,
		model: str | None,
	) -> str:
		return "The best label is:\n<filename>project_notes</filename>"

	monkeypatch.setattr(
		screenshot_lib.filename_models,
		"run_filename_model",
		fake_run_filename_model,
	)
	filename = screenshot_lib.intelligent_filename.generate_intelligent_filename(
		"OCR",
		"caption",
	)
	assert filename == "project_notes.png"


#============================================
def test_official_apple_sdk_adapter_preserves_xml_response(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The official SDK receives instructions and can answer with verbose XML."""
	calls = []

	class FakeSystemLanguageModel:
		def is_available(self) -> tuple[bool, None]:
			return True, None

	class FakeLanguageModelSession:
		def __init__(self, instructions: str, model: object) -> None:
			calls.append(("instructions", instructions, model))

		async def respond(self, prompt: str) -> str:
			calls.append(("prompt", prompt))
			return "Reasoning first.\n<filename>project_notes</filename>"

	monkeypatch.setattr(
		screenshot_lib.apple_models.apple_fm_sdk,
		"SystemLanguageModel",
		FakeSystemLanguageModel,
	)
	monkeypatch.setattr(
		screenshot_lib.apple_models.apple_fm_sdk,
		"LanguageModelSession",
		FakeLanguageModelSession,
	)
	response = screenshot_lib.apple_models.run_apple_model("prompt", "instructions")
	assert response.endswith("<filename>project_notes</filename>")
	assert calls[0][0:2] == ("instructions", "instructions")
	assert calls[1] == ("prompt", "prompt")


#============================================
def test_filename_dispatches_to_official_apple_adapter(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Selecting Apple dispatches to the official SDK adapter."""
	def fake_run_apple_model(prompt: str, instructions: str) -> str:
		return f"{instructions}\n<filename>{prompt}</filename>"

	monkeypatch.setattr(
		screenshot_lib.apple_models,
		"run_apple_model",
		fake_run_apple_model,
	)
	response = screenshot_lib.filename_models.run_filename_model(
		"project_notes",
		"instructions",
		backend="apple",
	)
	assert response.endswith("<filename>project_notes</filename>")


#============================================
def test_apple_backend_rejects_an_ollama_model_name() -> None:
	"""The OS-selected Apple model cannot be combined with an Ollama model name."""
	with pytest.raises(ValueError, match="system model"):
		screenshot_lib.filename_models.describe_filename_model("apple", "custom:7b")
