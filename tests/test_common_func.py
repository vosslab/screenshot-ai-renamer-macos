import platform

import pytest

import screenshot_lib.common_func


#============================================
def test_required_macos_version_accepts_compatible_system(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""A runtime may start when the detected macOS major satisfies its contract."""
	def compatible_version() -> tuple[str, tuple, str]:
		return ("14.7.1", (), "")

	monkeypatch.setattr(platform, "mac_ver", compatible_version)
	major_version = screenshot_lib.common_func.require_macos_version(13, "Photon")
	assert major_version == 14


#============================================
def test_required_macos_version_rejects_old_system(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""A runtime must fail before loading weights on an unsupported macOS major."""
	def old_version() -> tuple[str, tuple, str]:
		return ("12.6.9", (), "")

	monkeypatch.setattr(platform, "mac_ver", old_version)
	with pytest.raises(RuntimeError, match="requires macOS 13"):
		screenshot_lib.common_func.require_macos_version(13, "Photon")
