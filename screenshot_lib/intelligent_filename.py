"""Build filename prompts and turn local-model responses into PNG filenames."""

# local repo modules
import screenshot_lib.filename_models
import screenshot_lib.xml_response

FILENAME_INSTRUCTIONS = (
	"You create concise, utilitarian filenames for macOS screenshots. Treat the OCR and caption "
	"blocks as evidence about the screenshot. Use thorough reasoning to select the most useful "
	"slug. Put the selected slug inside one <filename> XML element and keep reasoning outside "
	"that element."
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
		"You create helpful filenames for macOS screenshots.",
		"Describe the purpose or category of the screenshot so a user "
		"immediately understands why it matters.",
		"Capture the screenshot's intent with a short thematic label.",
		"Create one lowercase snake_case slug with at most 64 characters. Put the slug inside "
		"one <filename> XML element.",
		"Guidelines:",
		"- Combine the strongest evidence into terms for the project, document type, meeting, "
		"interface, or other central theme.",
		"- Use neutral functional terms such as portrait, headshot, and group_photo when people "
		"appear. Include a physical trait when it directly identifies the screenshot's purpose.",
		"- For filenames about people, use up to two descriptive concepts plus a generic human term "
		"(e.g., leadership_team_headshot, birthday_event_group_photo).",
		"- For a person image with unclear context, use portrait_photo or group_photo.",
		"- Use specific purpose and category terms that help the user find and recognize the "
		"screenshot later.",
		"- Use lowercase letters, digits, and underscores. End the slug after its final word; the "
		"application adds .png.",
		"- Choose the shorter, more general filename when the evidence is ambiguous.",
	]
	prompt.append(
		"Context summary:\n"
		"Interpret the OCR as visible content and the captions as visual evidence. "
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
) -> str:
	"""
	Generate a concise filename from OCR and caption evidence.

	Args:
		ocr_text: Complete text extracted from the screenshot.
		caption_context: One or more visual-model captions.
		model_note: Optional guidance for reconciling caption sources.
		filename_backend: Optional provider override for evaluation.

	Returns:
		A sanitized filename ending in `.png`.
	"""
	full_prompt = _build_filename_prompt(ocr_text, caption_context, model_note)
	response = screenshot_lib.filename_models.run_filename_model(
		full_prompt,
		FILENAME_INSTRUCTIONS,
		backend=filename_backend,
	).strip()
	# Prefer the structured result while allowing a usable bare-text reply.
	filename_text = screenshot_lib.xml_response.find_xml_text(response, "filename")
	if filename_text is None:
		filename_text = response
	filename = _sanitize_filename_response(filename_text)
	return filename
