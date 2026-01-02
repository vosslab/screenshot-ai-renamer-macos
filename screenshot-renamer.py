#!/usr/bin/env python3

import argparse
import gc
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


RENAMED_PATTERN = re.compile(
	r"^screenshot_(\d{4}-\d{2}-\d{2}|unknown-date)-[a-z0-9_-]+\.png$",
	re.IGNORECASE,
)

COLOR_ENABLED = True


class Ansi:
	"""ANSI escape codes for color output."""

	RESET = "\033[0m"
	BOLD = "\033[1m"
	DIM = "\033[2m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"


def colorize(text: str, *styles: str) -> str:
	"""
	Wrap text with ANSI styles if color output is enabled.
	"""
	if not COLOR_ENABLED:
		return text
	return "".join(styles) + text + Ansi.RESET


def should_use_color(no_color: bool) -> bool:
	"""
	Determine if ANSI color output should be enabled.
	"""
	if no_color:
		return False
	if os.environ.get("NO_COLOR"):
		return False
	if os.environ.get("TERM") == "dumb":
		return False
	return sys.stdout.isatty()


def clear_gpu_memory():
	"""Forcefully clears GPU memory after processing an image to prevent out-of-memory errors."""
	import torch  # Lazy import to avoid slowing CLI help.

	gc.collect()  # Clean Python memory
	if torch.backends.mps.is_available():
		torch.mps.empty_cache()  # Clears MPS (Metal Performance Shaders) memory
	if torch.cuda.is_available():
		torch.cuda.empty_cache()

#============================================
def format_preview(text: str, max_lines: int = 2, line_length: int = 80) -> str:
	"""
	Formats text into a preview with a max number of lines and line length.

	Args:
		text (str): The text to format.
		max_lines (int): The maximum number of lines to show.
		line_length (int): The maximum length per line.

	Returns:
		str: Formatted preview text.
	"""
	words = text.split()
	lines = []
	current_line = ""

	for word in words:
		if len(current_line) + len(word) + 1 > line_length:
			lines.append(current_line)
			current_line = word
			if len(lines) == max_lines:
				break
		else:
			current_line += " " + word if current_line else word

	if current_line and len(lines) < max_lines:
		lines.append(current_line)

	return "\n".join(lines)


def format_duration(seconds: float) -> str:
	"""
	Convert seconds to a human-readable string (e.g., 1m 23s).
	"""
	seconds = max(0, int(seconds))
	minutes, sec = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	if hours:
		return f"{hours}h {minutes}m {sec}s"
	if minutes:
		return f"{minutes}m {sec}s"
	return f"{sec}s"

def _compose_caption_payload(captions: List[Tuple[str, str]]) -> Tuple[str, Optional[str]]:
	"""
	Combine multiple captions into a single blob for the filename LLM.

	Args:
		captions (list[tuple]): List of (backend, caption) entries.

	Returns:
		tuple[str, Optional[str]]: Combined caption text and optional model guidance.
	"""
	parts = []
	backends = set()
	for backend, caption in captions:
		backends.add(backend)
		label = backend.replace("-", " ").title()
		parts.append(f"{label} caption:\n{caption.strip() or 'N/A'}")

	model_note = None
	if {"moondream", "vit-gpt2"}.issubset(backends):
		model_note = (
			"In practice Moondream2 tends to produce richer, more context-aware descriptions than "
			"ViT-GPT2, which is more literal. Blend both perspectives when deciding on the filename."
		)

	return "\n\n".join(parts), model_note


def process_image(
	image_path: str,
	ai_components: dict,
	dry_run: bool,
	secondary_ai_components: Optional[dict] = None,
):
	"""
	Processes a single image: extracts text, generates captions, renames file, and updates metadata.

		Args:
			image_path (str): Path to the image file.
			ai_components (dict): Primary AI model components.
			dry_run (bool): If True, only prints changes without modifying files.
			secondary_ai_components (dict | None): Optional second caption backend.
	"""
	from tools.extract_text import extract_text_from_image
	from tools.generate_caption import generate_caption
	from tools.intelligent_filename import generate_intelligent_filename
	from tools.update_metadata import write_exif_metadata

	filename = os.path.basename(image_path)
	print('\n')
	print(colorize("=" * 60, Ansi.DIM))
	print(colorize(f"Processing image: {filename}", Ansi.BOLD, Ansi.CYAN))

	print(colorize("\nStarting OCR...", Ansi.YELLOW))
	start_time = time.time()
	ocr_text = extract_text_from_image(image_path)
	ocr_time = time.time() - start_time
	print(colorize("OCR Results:", Ansi.BLUE))
	print(format_preview(ocr_text))
	print(colorize(f"Time taken for OCR: {ocr_time:.2f} seconds", Ansi.GREEN))

	print(colorize(f"\nStarting Caption ({ai_components['backend']})...", Ansi.YELLOW))
	start_time = time.time()
	ai_caption = generate_caption(image_path, ai_components)
	caption_time = time.time() - start_time
	print(colorize("Caption Results:", Ansi.BLUE))
	print(format_preview(ai_caption))
	print(colorize(f"Time taken for caption generation: {caption_time:.2f} seconds", Ansi.GREEN))
	captions = [(ai_components["backend"], ai_caption)]

	if secondary_ai_components:
		print(colorize(
			f"\nStarting Secondary Caption ({secondary_ai_components['backend']})...",
			Ansi.YELLOW,
		))
		start_time = time.time()
		secondary_caption = generate_caption(image_path, secondary_ai_components)
		secondary_time = time.time() - start_time
		print(colorize("Secondary Caption Results:", Ansi.BLUE))
		print(format_preview(secondary_caption))
		print(colorize(f"Time taken for secondary caption: {secondary_time:.2f} seconds", Ansi.GREEN))
		captions.append((secondary_ai_components["backend"], secondary_caption))

	clear_gpu_memory()

	print(colorize("\nStarting Get AI Filename with LLM...", Ansi.YELLOW))
	start_time = time.time()
	caption_payload, model_note = _compose_caption_payload(captions)
	filename_stub = generate_intelligent_filename(ocr_text, caption_payload, model_note)
	filename_time = time.time() - start_time
	print(colorize("AI Filename Result:", Ansi.BLUE))
	print(colorize(filename_stub, Ansi.BOLD, Ansi.MAGENTA))
	print(colorize(
		f"Time taken for filename generation: {filename_time:.2f} seconds",
		Ansi.GREEN,
	))
	clear_gpu_memory()

	# Correctly extract only the date from the filename
	match = re.search(r"(\d{4}-\d{2}-\d{2})", filename, re.IGNORECASE)
	date_part = match.group(1) if match else "unknown-date"

	# Construct the final filename with correct date prefix
	new_filename = f"screenshot_{date_part}-{filename_stub}"
	new_path = os.path.join(os.path.dirname(image_path), new_filename)

	if dry_run:
		print(colorize(
			f"Dry Run: Would rename '{filename}' -> '{new_filename}'",
			Ansi.YELLOW,
		))
	else:
		start_time = time.time()
		os.rename(image_path, new_path)
		write_exif_metadata(new_path, ocr_text, ai_caption)
		metadata_time = time.time() - start_time
		print(colorize(
			f"Renamed and updated metadata: '{filename}' -> '{new_filename}'",
			Ansi.GREEN,
		))
		print(colorize(
			f"Time taken for renaming and metadata update: {metadata_time:.2f} seconds",
			Ansi.GREEN,
		))

#============================================
def process_directory(directory: str):
	"""
	Collect all screenshot-style PNGs in the specified directory.

	Returns:
		tuple[list[str], list[str]]: (pending screenshots, already-renamed files that were skipped)
	"""
	image_files = []
	already_renamed = []
	for filename in os.listdir(directory):
		#note macos filesystem are 99% of the time case INsensitive
		lower_filename = filename.lower()
		if not lower_filename.startswith("screen"):
			continue
		extension = os.path.splitext(lower_filename)[-1]
		#if not extension in (".png", ".jpg", ".jpeg"):
		if extension != ".png":
			continue
		if RENAMED_PATTERN.match(lower_filename):
			already_renamed.append(filename)
			continue
		image_files.append(filename)

	if not image_files and already_renamed:
		print(colorize("Only already-renamed screenshots found; nothing to do.", Ansi.YELLOW))
	elif not image_files:
		print(colorize("No images found in the specified directory.", Ansi.YELLOW))

	return image_files, already_renamed

#============================================
def parse_args():
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(description="Batch process images with step-by-step feedback.")
	parser.add_argument("-d", "--directory", dest="directory", nargs="?",
					default=os.path.expanduser("~/Desktop"),
					help="Directory containing images (default: ~/Desktop)")
	parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true",
						help="Perform a dry run without modifying files.")
	parser.add_argument("-t", "--unit-test", dest="unit_test", action="store_true",
						help="Run a unit test (ask LLM to add two numbers).")
	parser.add_argument("--no-color", dest="no_color", action="store_true",
						help="Disable ANSI color output.")
	parser.add_argument("--caption-prompt", dest="caption_prompt",
						help="Custom captioning prompt applied to both caption models.")
	args = parser.parse_args()
	return args

#============================================
def main():
	"""
	Main function
	"""
	args = parse_args()

	global COLOR_ENABLED
	COLOR_ENABLED = should_use_color(args.no_color)

	if args.unit_test:
		import sys
		from tools import config_apple_models
		config_apple_models.unit_test()
		sys.exit(0)

	image_files, already_renamed = process_directory(args.directory)
	if not image_files:
		return
	image_files.sort()
	if args.dry_run is True:
		random.shuffle(image_files)
	else:
		image_files.sort(key=len)

	total_files = len(image_files)
	for i, filename in enumerate(image_files, start=1):
		if i > 9:
			print(colorize(f"... plus {total_files-9} more files", Ansi.DIM))
			break
		print(colorize(f"{i}: {filename}", Ansi.CYAN))

	if already_renamed:
		print(colorize(
			f"Skipping {len(already_renamed)} already-renamed files.",
			Ansi.YELLOW,
		))

	mode = "Dry run (no changes)" if args.dry_run else "Live rename"
	summary = f"\nPlan summary: Found {total_files} screenshots in {args.directory}."
	if already_renamed:
		summary += f" Skipping {len(already_renamed)} already renamed files."
	print(colorize(f"{summary} {mode}.", Ansi.BOLD))

	try:
		from tools.generate_caption import setup_ai_components

		ai_components = setup_ai_components(prompt=args.caption_prompt, backend="moondream")
	except Exception as exc:  # pylint: disable=broad-exception-caught
		print(f"Failed to load Moondream backend: {exc}")
		raise

	try:
		secondary_ai_components = setup_ai_components(prompt=args.caption_prompt, backend="vit-gpt2")
	except Exception as exc:  # pylint: disable=broad-exception-caught
		print(f"Failed to load ViT-GPT2 backend: {exc}")
		secondary_ai_components = None

	print("\nCaption backends: Moondream2", end="")
	if secondary_ai_components:
		print(" + ViT-GPT2")
	else:
		print(" (ViT-GPT2 unavailable)")
	if args.caption_prompt:
		print(colorize(
			f"Custom caption prompt: {format_preview(args.caption_prompt, max_lines=3)}",
			Ansi.BLUE,
		))

	durations: List[float] = []
	for i, filename in enumerate(image_files, start=1):
		image_path = os.path.join(args.directory, filename)
		print(colorize(f"\nProcessing image {i} of {len(image_files)}", Ansi.CYAN))
		image_start = time.time()
		process_image(
			image_path,
			ai_components,
			args.dry_run,
			secondary_ai_components,
		)
		image_duration = time.time() - image_start
		durations.append(image_duration)
		avg_duration = sum(durations) / len(durations)
		remaining = len(image_files) - i
		print(colorize(
			f"Image {i} completed in {format_duration(image_duration)} "
			f"(avg {format_duration(avg_duration)}).",
			Ansi.GREEN,
		))
		if remaining > 0:
			eta_seconds = avg_duration * remaining
			eta_time = datetime.now() + timedelta(seconds=eta_seconds)
			eta_clock = eta_time.strftime("%I:%M %p").lstrip("0")
			print(colorize(
				f"Estimated completion in {format_duration(eta_seconds)} "
				f"(~{eta_clock}).",
				Ansi.MAGENTA,
			))

	total_elapsed = sum(durations)
	if durations:
		print(colorize(
			f"\nCompleted {len(durations)} images in {format_duration(total_elapsed)} "
			f"(avg {format_duration(total_elapsed/len(durations))}).",
			Ansi.GREEN,
		))


if __name__ == "__main__":
	main()
