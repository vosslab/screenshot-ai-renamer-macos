import os

import torch
from PIL import Image

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
def get_attention_mask(pixel_values: torch.Tensor, device: str) -> torch.Tensor:
	"""
	Create an attention mask matching the pixel tensor size for encoder-decoder models.

	Args:
		pixel_values (torch.Tensor): Image tensor returned by a feature extractor.
		device (str): Device to allocate the mask on.

	Returns:
		torch.Tensor: Attention mask of ones sized to the first two dims of pixel_values.
	"""
	return torch.ones(pixel_values.shape[:2], dtype=torch.long, device=device)

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
