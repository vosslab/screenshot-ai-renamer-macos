import os
import sys
import platform

import torch
from PIL import Image

#============================================
def require_apple_silicon() -> str:
	"""Require the Apple Silicon platform used by Photon's Metal runtime."""
	if sys.platform != "darwin" or platform.machine() != "arm64":
		raise RuntimeError(
			"Photon Metal captioning requires an Apple Silicon Mac running macOS."
		)
	runtime = "metal"
	return runtime


#============================================
def get_total_memory_bytes() -> int:
	"""Return the physical unified-memory capacity visible to macOS."""
	page_size = os.sysconf("SC_PAGE_SIZE")
	page_count = os.sysconf("SC_PHYS_PAGES")
	total_memory = page_size * page_count
	return total_memory


#============================================
def require_macos_version(minimum_major: int, component_name: str) -> int:
	"""Require the minimum macOS major version for a local model runtime."""
	version_text = platform.mac_ver()[0]
	if not version_text:
		raise RuntimeError(f"Cannot determine macOS version for {component_name}.")
	major_version = int(version_text.split(".")[0])
	if major_version < minimum_major:
		raise RuntimeError(
			f"{component_name} requires macOS {minimum_major} or later; "
			f"this Mac reports macOS {major_version}."
		)
	return major_version


#============================================
def get_mps_device() -> str:
	"""
	Require Apple Metal GPU acceleration for local caption inference.
	"""
	if not torch.backends.mps.is_built():
		raise RuntimeError(
			"PyTorch was installed without Apple MPS support. Install the macOS "
			"arm64 PyTorch build before loading caption models."
		)
	if not torch.backends.mps.is_available():
		raise RuntimeError(
			"Apple MPS is unavailable. This project requires Apple Silicon with "
			"Metal GPU support; unaccelerated CPU fallback is disabled."
		)
	device = "mps"
	return device

def resize_image(image: Image.Image, max_dimension: int) -> Image.Image:
	"""
	Resizes an image while maintaining its aspect ratio.

	Args:
		image (PIL.Image): Input image.
		max_dimension (int): Maximum width or height.

	Returns:
		PIL.Image: Resized image.
	"""
	width, height = image.size
	if max(width, height) <= max_dimension:
		return image

	if width > height:
		new_width = max_dimension
		new_height = int((height / width) * max_dimension)
	else:
		new_height = max_dimension
		new_width = int((width / height) * max_dimension)

	resample_filter = (
		Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
	)
	return image.resize((new_width, new_height), resample_filter)

#============================================
def get_image_paths(directory: str) -> list[str]:
	"""
	Returns a list of image file paths in a directory.

	Args:
		directory (str): Path to directory.

	Returns:
		list: List of image file paths.
	"""
	return [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
