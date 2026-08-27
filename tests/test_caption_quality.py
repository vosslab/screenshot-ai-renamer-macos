import screenshot_lib.caption_quality


#============================================
def test_normal_caption_is_usable() -> None:
	"""A concise visual description must pass the shared quality contract."""
	caption = "A red rectangle and a blue circle appear on a white test card."
	reason = screenshot_lib.caption_quality.get_caption_failure_reason(caption)
	assert reason is None


#============================================
def test_mixed_repetitive_fragments_are_rejected() -> None:
	"""Compression collapse must catch repeated fragments with changing tokens."""
	caption = "Photators Mel Phot " * 20
	caption += "Mc Sou I will " * 30
	reason = screenshot_lib.caption_quality.get_caption_failure_reason(caption)
	assert reason is not None


#============================================
def test_runaway_caption_is_rejected() -> None:
	"""A runaway generation must not enter the filename-model context."""
	caption = "visual evidence " * 100
	reason = screenshot_lib.caption_quality.get_caption_failure_reason(caption)
	assert reason is not None
