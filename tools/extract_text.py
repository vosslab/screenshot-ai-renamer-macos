#!/usr/bin/env python3

import os
import pytesseract  # Heavy import; keep at module level for runtime clarity.
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
	"""
	Extracts text from an image using Tesseract OCR.

	Args:
		image_path (str): Path to the image file.

	Returns:
		str: Extracted text from the image.
	"""
	image = Image.open(image_path)
	text = pytesseract.image_to_string(image)
	return text.strip()

def process_directory(directory: str):
	"""
	Process all images in a directory and extract text.

	Args:
		directory (str): Path to the directory containing images.
	"""
	if not os.path.isdir(directory):
		raise FileNotFoundError(f"The specified path {directory} is not a valid directory.")

	for filename in os.listdir(directory):
		if filename.lower().endswith(".png") or filename.lower().endswith(".jpg"):
			image_path = os.path.join(directory, filename)
			text = extract_text_from_image(image_path)
			print(f"Extracted text from {filename}:\n{text}\n")

if __name__ == "__main__":
	directory = os.path.expanduser("~/Desktop")  # Default to Desktop
	print(f"Processing images in: {directory}")
	process_directory(directory)
