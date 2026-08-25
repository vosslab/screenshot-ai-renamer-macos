"""Build filename prompts and turn local-model responses into PNG filenames."""

# local repo modules
import screenshot_lib.filename_models
import screenshot_lib.xml_response

FILENAME_INSTRUCTIONS = (
	"You write concise, utilitarian filenames for macOS screenshots. You may reason or explain "
	"before the result. Place only the selected filename slug inside one <filename> XML element."
)


#============================================
def _context_text(text: str) -> str:
	"""Return complete local evidence or an explicit empty-evidence marker."""
	cleaned = text.strip()
	if not cleaned:
		return "N/A"
	return cleaned


#============================================
def _sanitize_filename_response(response: str) -> str:
	"""Convert a model response into a validated PNG filename."""
	first_line = response.split("\n")[0].lower()
	filename = first_line.replace(" ", "_").replace("__", "_")
	filename = "".join(c for c in filename if c.isalnum() or c in "._-")
	filename = filename.strip("._-")
	filename = filename[:64]

	if not filename:
		raise ValueError("Filename model returned an empty filename.")
	if not filename.endswith(".png"):
		filename += ".png"
	return filename


#============================================
def _build_filename_prompt(
	ocr_text: str,
	caption_context: str,
	model_note: str | None = None,
) -> str:
	"""Build the established naming prompt with an XML result element."""
	prompt = [
		"You are an assistant that writes helpful filenames for macOS screenshots.",
		"Filenames should describe the purpose or category of the screenshot so a user "
		"immediately understands why it matters.",
		"Never narrate every visible attribute; capture the intent.",
		"Generate a single snake_case filename (max 64 characters). Place only the filename "
		"inside one <filename> XML element.",
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
	prompt.append(f"OCR Text:\n{_context_text(ocr_text)}")
	if model_note:
		prompt.append(model_note)
	prompt.append(f"Caption Intelligence:\n{_context_text(caption_context)}")
	prompt.append("Final result: <filename>snake_case_filename</filename>")
	full_prompt = "\n\n".join(prompt)
	return full_prompt


#============================================
def generate_intelligent_filename(
	ocr_text: str,
	caption_context: str,
	model_note: str | None = None,
	*,
	filename_backend: str | None = None,
	filename_model: str | None = None,
) -> str:
	"""
	Generate a concise filename from OCR and caption evidence.

	Args:
		ocr_text: Complete text extracted from the screenshot.
		caption_context: One or more visual-model captions.
		model_note: Optional guidance for reconciling caption sources.
		filename_backend: Optional provider override for evaluation.
		filename_model: Optional Ollama model override for evaluation.

	Returns:
		A sanitized filename ending in `.png`.
	"""
	full_prompt = _build_filename_prompt(ocr_text, caption_context, model_note)
	response = screenshot_lib.filename_models.run_filename_model(
		full_prompt,
		FILENAME_INSTRUCTIONS,
		backend=filename_backend,
		model=filename_model,
	).strip()
	# Prefer the structured result while allowing a usable bare-text reply.
	filename_text = screenshot_lib.xml_response.find_xml_text(response, "filename")
	if filename_text is None:
		filename_text = response
	filename = _sanitize_filename_response(filename_text)
	return filename
