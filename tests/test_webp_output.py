"""Protect source images and existing outputs during WebP publication."""

import pathlib

import pytest
import PIL.Image

import screenshot_lib.webp_output
import screenshot_lib.update_metadata


#============================================
def ignore_metadata(image_path: str, ocr_text: str, ai_caption: str) -> None:
	"""Keep ExifTool subprocess verification in the live validation lane."""
	return None


#============================================
def test_conversion_replaces_source_with_decodable_webp(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	source = tmp_path / 'source.png'
	PIL.Image.new('RGBA', (32, 32), (20, 80, 150, 120)).save(source)
	monkeypatch.setattr(screenshot_lib.update_metadata, 'write_exif_metadata', ignore_metadata)
	result = screenshot_lib.webp_output.publish_webp(str(source), str(tmp_path / 'named.webp'), '', '')
	with PIL.Image.open(result) as image:
		image.load()
		assert (image.format, image.size, image.getpixel((0, 0))[3]) == ('WEBP', (32, 32), 120)
	assert not source.exists()


#============================================
def test_collision_keeps_existing_output(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	source = tmp_path / 'source.png'
	target = tmp_path / 'named.webp'
	PIL.Image.new('RGB', (32, 32), 'red').save(source)
	target.write_bytes(b'existing screenshot')
	monkeypatch.setattr(screenshot_lib.update_metadata, 'write_exif_metadata', ignore_metadata)
	result = screenshot_lib.webp_output.publish_webp(str(source), str(target), '', '')
	assert target.read_bytes() == b'existing screenshot'
	assert pathlib.Path(result).name == 'named_2.webp'


#============================================
@pytest.mark.parametrize('failure', ['encode', 'metadata', 'publish'])
def test_failed_output_preserves_original(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, failure: str,
) -> None:
	source = tmp_path / 'source.png'
	PIL.Image.new('RGB', (32, 32), 'blue').save(source)
	original = source.read_bytes()
	monkeypatch.setattr(screenshot_lib.update_metadata, 'write_exif_metadata', ignore_metadata)
	def fail(*args, **kwargs) -> None:
		raise OSError('simulated output failure')
	if failure == 'encode':
		monkeypatch.setattr(PIL.Image.Image, 'save', fail)
	elif failure == 'metadata':
		monkeypatch.setattr(screenshot_lib.update_metadata, 'write_exif_metadata', fail)
	else:
		monkeypatch.setattr(screenshot_lib.webp_output.os, 'link', fail)
	with pytest.raises(OSError, match='simulated'):
		screenshot_lib.webp_output.publish_webp(str(source), str(tmp_path / 'named.webp'), '', '')
	assert source.read_bytes() == original
	assert sorted(path.name for path in tmp_path.iterdir()) == ['source.png']
