#!/usr/bin/env python3

import argparse

MAX_CONTEXT_CHARS = 1500  # Keep prompts within the Apple Foundation Models context limits.
MODEL_ERROR_MARKERS = (
	"error_code",
	"foundationmodels",
	"generationerror",
	"operation_couldnt_be_completed",
	"operation_couldn",
)


#============================================
def _truncate(text: str, limit: int = MAX_CONTEXT_CHARS) -> str:
	"""Trim text to a safe length for the on-device model."""
	if not text:
		return "N/A"
	text = text.strip()
	if len(text) <= limit:
		return text
	truncated = text[: limit - 3].rstrip() + "..."
	return truncated


#============================================
def _response_looks_like_model_error(text: str) -> bool:
	"""Check whether a model response is actually backend error text."""
	normalized = text.strip().lower()
	normalized = normalized.replace(" ", "_")
	normalized = normalized.replace("-", "_")
	for marker in MODEL_ERROR_MARKERS:
		if marker in normalized:
			return True
	return False


#============================================
def _sanitize_filename_response(response: str) -> str:
	"""Convert a model response into a validated PNG filename."""
	if _response_looks_like_model_error(response):
		raise ValueError(f"Apple Foundation Models returned error text: {response}")

	first_line = response.split("\n")[0].lower()
	filename = first_line.replace(" ", "_").replace("__", "_")
	filename = "".join(c for c in filename if c.isalnum() or c in "._-")
	filename = filename.strip("._-")
	filename = filename[:64]

	if not filename:
		raise ValueError("Apple Foundation Models returned an empty filename.")
	if _response_looks_like_model_error(filename):
		raise ValueError(f"Apple Foundation Models returned invalid filename text: {filename}")
	if not filename.endswith(".png"):
		filename += ".png"
	return filename


#============================================
def generate_intelligent_filename(
	ocr_text: str,
	caption_context: str,
	model_note: str | None = None,
) -> str:
	"""
	Generate a concise, valid filename using an LLM based on OCR and caption data.

	Args:
		ocr_text (str): Extracted text from the image.
		caption_context (str): Aggregated AI caption details (can include multiple models).
		model_note (str, optional): Guidance about the caption sources/quality.

	Returns:
		str: Valid filename ending with .png.
	"""
	prompt = [
		"You are an assistant that writes helpful filenames for macOS screenshots.",
		"Filenames should describe the purpose or category of the screenshot so a user "
		"immediately understands why it matters.",
		"Never narrate every visible attribute; capture the intent.",
		"Generate a single snake_case filename (max 64 characters) and output only the filename.",
		"Rules:",
		"- Focus on themes (project, document type, meeting, UI, etc.). Summarize instead of "
		"listing all words.",
		"- When people appear, avoid physical descriptors (age, gender, clothing, expressions) "
		"unless essential to the function. Prefer neutral terms like portrait, headshot, "
		"group_photo.",
		"- Limit people-related filenames to two descriptive concepts plus a generic human term "
		"(e.g., leadership_team_headshot, birthday_event_group_photo).",
		"- If the image is simply a person with no clear context, use a neutral fallback such as "
		"portrait_photo or group_photo.",
		"- Avoid redundant words like screenshot/macOS/date references.",
		"- No punctuation besides underscores; no file extension in the output.",
		"- When in doubt, choose the shorter, more general filename.",
	]
	prompt.append(
		"Context summary:\n"
		"Use the information below to infer the screenshot's purpose. "
		"Prioritize themes over literal text so the filename reflects what the screenshot is about."
	)
	prompt.append(f"OCR Text:\n{_truncate(ocr_text)}")
	if model_note:
		prompt.append(model_note)
	prompt.append(f"Caption Intelligence:\n{_truncate(caption_context)}")
	prompt.append("Filename:")
	full_prompt = "\n\n".join(prompt)

	from tools import config_apple_models

	response = config_apple_models.run_apple_model(full_prompt).strip()
	filename = _sanitize_filename_response(response)
	return filename


#============================================
def main() -> None:
	"""Main function for standalone execution and unit testing."""
	parser = argparse.ArgumentParser(description="Generate intelligent filenames for images.")
	parser.add_argument(
		"ocr_text",
		type=str,
		nargs="?",
		default="Example OCR Text",
		help="Extracted text from the image.",
	)
	parser.add_argument(
		"ai_caption",
		type=str,
		nargs="?",
		default="Example AI Caption",
		help="AI-generated caption details (use \\n\\n between sources).",
	)
	parser.add_argument(
		"--model-note",
		help="Optional hint about the caption sources or quality.",
	)
	parser.add_argument(
		"-t", "--test",
		action="store_true",
		help="Run a unit test (ask LLM 'What is 2+2?').",
	)
	args = parser.parse_args()

	if args.test:
		from tools import config_apple_models
		config_apple_models.unit_test()
	else:
		new_filename = generate_intelligent_filename(args.ocr_text, args.ai_caption, args.model_note)
		print(f"Generated Filename: {new_filename}")


if __name__ == "__main__":
	main()
