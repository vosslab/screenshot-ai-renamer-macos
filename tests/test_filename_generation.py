# PIP3 modules
import pytest

# local repo modules
import screenshot_lib.filename_models
import screenshot_lib.intelligent_filename


#============================================
def test_filename_response_normalizes_separators() -> None:
	"""The established sanitizer still normalizes spaces and case."""
	result = screenshot_lib.intelligent_filename._sanitize_filename_response(
		"Quarterly Results Review.png"
	)
	assert result == "quarterly_results_review.png"


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
def test_filename_generation_extracts_xml_from_surrounding_prose(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Ollama responses are parsed by XML instead of bare-text assumptions."""
	def fake_run_filename_model(
		prompt: str,
		instructions: str,
		*,
		backend: str | None,
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
