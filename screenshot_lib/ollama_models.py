"""Ollama integration for local filename generation."""

# Standard Library
import time

# PIP3 modules
import ollama

# local repo modules
import screenshot_lib.xml_response


#============================================
def run_ollama_model(
	prompt: str,
	instructions: str,
	model: str,
	thinking: bool | str,
) -> str:
	"""
	Generate a filename response through a local Ollama model.

	Args:
		prompt: Filename task and screenshot evidence.
		instructions: Stable system instructions for the filename task.
		model: Installed Ollama model name.
		thinking: Ollama thinking control; filename calls keep this enabled.

	Returns:
		The model's final response content, excluding its thinking trace.
	"""
	start_time = time.time()
	response = ollama.chat(
		model=model,
		messages=[
			{"role": "system", "content": instructions},
			{"role": "user", "content": prompt},
		],
		think=thinking,
		options={
			"seed": 0,
			"temperature": 0.2,
		},
	)
	content = response.message.content
	if content is None or not content.strip():
		thinking_text = response.message.thinking
		thinking_chars = len(thinking_text) if thinking_text else 0
		raise RuntimeError(
			f"Ollama model '{model}' returned no final content after "
			f"{thinking_chars} thinking characters."
		)
	elapsed = time.time() - start_time
	print(f"Ollama model {model} completed in {elapsed:.2f} seconds")
	return content.strip()


#============================================
def unit_test(model: str, thinking: bool | str) -> None:
	"""
	Validate that an Ollama model can return a short deterministic answer.

	Args:
		model: Installed Ollama model name.
		thinking: Ollama thinking control.
	"""
	print(f"Running Ollama unit test with {model}...")
	instructions = "Place the final integer answer inside one <answer> XML element."
	response = run_ollama_model(
		"What is 19 + 23? Finish with <answer>integer</answer>.",
		instructions,
		model,
		thinking,
	)
	answer = screenshot_lib.xml_response.extract_xml_text(response, "answer")
	if answer != "42":
		raise RuntimeError(f"Expected 42, but got {answer}")
	print("SUCCESS! 19 + 23 = 42")
