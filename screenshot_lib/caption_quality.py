import collections
import zlib


MAX_CAPTION_CHARACTERS = 1200
MINIMUM_COMPRESSION_SAMPLE = 96
MINIMUM_COMPRESSION_RATIO = 0.35


#============================================
def get_caption_failure_reason(caption: str) -> str | None:
	"""Return a reason when caption text is empty or trapped in token repetition."""
	caption_text = caption.strip()
	if not caption_text:
		return "empty caption"
	if len(caption_text) > MAX_CAPTION_CHARACTERS:
		return f"caption exceeds {MAX_CAPTION_CHARACTERS} characters"

	# Repetition failures may contain no spaces, so inspect character n-grams.
	normalized = "".join(character.casefold() for character in caption_text if character.isalnum())
	if len(normalized) < 32:
		return None
	if len(normalized) >= MINIMUM_COMPRESSION_SAMPLE:
		encoded = normalized.encode("utf-8")
		compressed = zlib.compress(encoded, level=9)
		compression_ratio = len(compressed) / len(encoded)
		if compression_ratio < MINIMUM_COMPRESSION_RATIO:
			return "repetitive token collapse"

	for width in range(2, 7):
		ngrams = [normalized[index:index + width] for index in range(len(normalized) - width + 1)]
		most_common_count = collections.Counter(ngrams).most_common(1)[0][1]
		coverage = most_common_count * width / len(normalized)
		if coverage >= 0.45:
			return "repetitive token collapse"

	return None


#============================================
def require_usable_caption(caption: str, backend_name: str) -> None:
	"""Raise when a caption backend returns unusable text."""
	failure_reason = get_caption_failure_reason(caption)
	if failure_reason is not None:
		raise ValueError(f"{backend_name} produced an unusable caption: {failure_reason}.")
