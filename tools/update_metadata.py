import exiftool

#============================================
def write_exif_metadata(image_path: str, ocr_text: str, ai_caption: str):
	"""
	Writes OCR text and AI captions to EXIF metadata, overwriting the original file.

	Args:
		image_path (str): Path to the image file.
		ocr_text (str): Extracted OCR text.
		ai_caption (str): AI-generated caption.
	"""
	with exiftool.ExifTool() as et:
		metadata = {
			"EXIF:ImageDescription": ai_caption,
			"EXIF:UserComment": ocr_text
		}
		et.execute(*[f'-{key}={value}' for key, value in metadata.items()], "-overwrite_original", image_path)
		print(f"Metadata written to {image_path} (original file overwritten)")

