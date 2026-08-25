"""Extract machine-readable values from LLM responses containing XML."""

# PIP3 modules
import lxml.etree


#============================================
def find_xml_text(response: str, tag: str) -> str | None:
	"""Return an XML element's text, or None when no usable element is present."""
	opening = f"<{tag}>"
	closing = f"</{tag}>"
	start = response.find(opening)
	end = response.find(closing, start + len(opening))
	if start < 0 or end < 0:
		return None
	fragment = response[start : end + len(closing)]
	parser = lxml.etree.XMLParser(
		load_dtd=False,
		no_network=True,
		resolve_entities=False,
	)
	try:
		element = lxml.etree.fromstring(fragment, parser=parser)
	except lxml.etree.XMLSyntaxError:
		return None
	if element.tag != tag:
		return None
	value = "".join(element.itertext()).strip()
	if not value:
		return None
	return value


#============================================
def extract_xml_text(response: str, tag: str) -> str:
	"""Extract one required XML element's text from a model response."""
	value = find_xml_text(response, tag)
	if value is None:
		raise ValueError(f"Model response did not contain a usable <{tag}> XML element.")
	return value
