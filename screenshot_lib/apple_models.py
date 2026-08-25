"""Official Apple Foundation Models SDK integration for filename generation."""

# Standard Library
import time
import asyncio

# PIP3 modules
import apple_fm_sdk

# local repo modules
import screenshot_lib.xml_response


#============================================
async def _respond_with_apple_model(prompt: str, instructions: str) -> str:
	"""Run one request through Apple's on-device system language model."""
	model = apple_fm_sdk.SystemLanguageModel()
	is_available, reason = model.is_available()
	if not is_available:
		reason_name = reason.name if reason is not None else "UNKNOWN"
		raise RuntimeError(f"Apple Foundation Models is unavailable: {reason_name}.")

	session = apple_fm_sdk.LanguageModelSession(
		instructions=instructions,
		model=model,
	)
	response = await session.respond(prompt)
	if not response.strip():
		raise RuntimeError("Apple Foundation Models returned no final content.")
	return response.strip()


#============================================
def run_apple_model(prompt: str, instructions: str) -> str:
	"""
	Generate a filename response with Apple's official Python SDK.

	Args:
		prompt: Filename task and screenshot evidence.
		instructions: Stable system instructions for the filename task.

	Returns:
		The model's complete response text.
	"""
	start_time = time.time()
	response = asyncio.run(_respond_with_apple_model(prompt, instructions))
	elapsed = time.time() - start_time
	print(f"Apple Foundation Models completed in {elapsed:.2f} seconds")
	return response


#============================================
def unit_test() -> None:
	"""Validate that Apple's system model can return a deterministic answer."""
	print("Running Apple Foundation Models unit test...")
	instructions = "Place the final integer answer inside one <answer> XML element."
	response = run_apple_model(
		"What is 19 + 23? Finish with <answer>integer</answer>.",
		instructions,
	)
	answer = screenshot_lib.xml_response.extract_xml_text(response, "answer")
	if answer != "42":
		raise RuntimeError(f"Expected 42, but got {answer}")
	print("SUCCESS! 19 + 23 = 42")
