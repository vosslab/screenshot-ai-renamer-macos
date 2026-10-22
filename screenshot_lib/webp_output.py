"""Convert a PNG and publish its named WebP before removing the source."""

import os
import pathlib
import tempfile

import PIL.Image

import screenshot_lib.update_metadata


#============================================
def publish_webp(source: str, destination: str, ocr_text: str, caption: str) -> str:
	"""Encode and annotate once, publishing without replacing an existing image."""
	source_path = pathlib.Path(source)
	target = pathlib.Path(destination)
	source_stat = source_path.stat()
	fd, temporary_name = tempfile.mkstemp(prefix=".screenshot_", suffix=".webp", dir=target.parent)
	os.close(fd)
	temporary = pathlib.Path(temporary_name)
	try:
		with PIL.Image.open(source_path) as image:
			# PNG may store metadata after its pixel chunks.
			image.load()
			metadata = {key: image.info[key] for key in ("icc_profile", "exif", "xmp")
				if key in image.info}
			size = image.size
			image.save(temporary, format="WEBP", quality=90, method=4, **metadata)
		screenshot_lib.update_metadata.write_exif_metadata(str(temporary), ocr_text, caption)
		with PIL.Image.open(temporary) as encoded:
			encoded.load()
			if encoded.format != "WEBP" or encoded.size != size:
				raise RuntimeError("WebP verification failed; original PNG retained.")
		os.utime(temporary, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
		# Hard-link publication is atomic and refuses to overwrite another screenshot.
		candidate = target
		counter = 1
		while True:
			try:
				os.link(temporary, candidate)
			except FileExistsError:
				counter += 1
				candidate = target.with_name(f"{target.stem}_{counter}{target.suffix}")
			else:
				break
		source_path.unlink()
	finally:
		temporary.unlink(missing_ok=True)
	return str(candidate)
