import subprocess

import exiftool

#============================================
def write_exif_metadata(image_path: str, ocr_text: str, ai_caption: str) -> None:
	"""
	Writes OCR text and AI captions to EXIF metadata, overwriting the original file.

	Args:
		image_path (str): Path to the image file.
		ocr_text (str): Extracted OCR text.
		ai_caption (str): AI-generated caption.
	"""
	metadata = {
		"EXIF:ImageDescription": ai_caption,
		"EXIF:UserComment": ocr_text,
	}
	# Pass multiline OCR as an argv value, not through ExifTool's line-based stdin protocol.
	command = ['exiftool', '-overwrite_original']
	command.extend(f'-{key}={value}' for key, value in metadata.items())
	command.append(image_path)
	subprocess.run(command, check=True, capture_output=True, text=True)
	with exiftool.ExifToolHelper() as et:
		stored = et.get_tags(image_path, list(metadata))[0]
		for key, value in metadata.items():
			if stored.get(key, "") != value:
				raise RuntimeError(f"Metadata readback failed for {key}: {image_path}")
