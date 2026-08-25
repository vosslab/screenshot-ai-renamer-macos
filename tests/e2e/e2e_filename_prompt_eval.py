"""Evaluate live filename generation against stable semantic cases."""

# Standard Library
import os
import re
import sys
import json
import time
import argparse

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

# local repo modules
import file_utils

REPO_ROOT = file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)

# local repo modules
import screenshot_lib.filename_models
import screenshot_lib.intelligent_filename

CASES_PATH = os.path.join(os.path.dirname(__file__), "filename_prompt_cases.json")
FILENAME_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*\.png$")


#============================================
def load_cases() -> list[dict]:
	"""Load the committed filename evaluation cases."""
	with open(CASES_PATH, encoding="ascii") as handle:
		cases = json.load(handle)
	return cases


#============================================
def select_cases(cases: list[dict], case_name: str | None) -> list[dict]:
	"""Select one named case or the entire evaluation corpus."""
	if case_name is None:
		return cases
	selected = [case for case in cases if case["name"] == case_name]
	if not selected:
		raise ValueError(f"Unknown evaluation case '{case_name}'.")
	return selected


#============================================
def evaluate_case(
	case: dict,
	backend: str | None,
	model: str | None,
) -> tuple[str, float, list[str]]:
	"""Generate one filename and return its latency and validation failures."""
	start_time = time.time()
	filename = screenshot_lib.intelligent_filename.generate_intelligent_filename(
		case["ocr_text"],
		case["caption_context"],
		case["source_guidance"],
		filename_backend=backend,
		filename_model=model,
	)
	elapsed = time.time() - start_time
	slug = filename.removesuffix(".png")
	slug_terms = set(slug.split("_"))
	failures = []
	if FILENAME_PATTERN.fullmatch(filename) is None:
		failures.append("format")
	if not any(term in slug_terms for term in case["expected_any"]):
		failures.append("expected concept")
	if any(term in slug_terms for term in case["forbidden"]):
		failures.append("forbidden concept")
	return filename, elapsed, failures


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse evaluation runner arguments."""
	parser = argparse.ArgumentParser(description="Evaluate the live filename LLM prompt.")
	parser.add_argument(
		"-b", "--filename-backend",
		dest="filename_backend",
		choices=screenshot_lib.filename_models.SUPPORTED_FILENAME_BACKENDS,
		help="Filename provider (default: ollama).",
	)
	parser.add_argument(
		"-m", "--filename-model",
		dest="filename_model",
		help="Ollama filename model (default: qwen3.5:27b).",
	)
	parser.add_argument(
		"-c", "--case",
		dest="case_name",
		help="Run one named evaluation case.",
	)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Run the selected filename evaluation cases."""
	args = parse_args()
	cases = select_cases(load_cases(), args.case_name)
	description = screenshot_lib.filename_models.describe_filename_model(
		args.filename_backend,
		args.filename_model,
	)
	print(f"Filename prompt evaluation: {description}")
	total_time = 0.0
	failed_cases = []
	for case in cases:
		filename, elapsed, failures = evaluate_case(
			case,
			args.filename_backend,
			args.filename_model,
		)
		total_time += elapsed
		status = "PASS" if not failures else "FAIL: " + ", ".join(failures)
		print(f"{case['name']}: {filename} ({elapsed:.2f}s) - {status}")
		if failures:
			failed_cases.append(case["name"])

	print(f"Completed {len(cases)} cases in {total_time:.2f}s; failures: {len(failed_cases)}")
	if failed_cases:
		names = ", ".join(failed_cases)
		raise RuntimeError(f"Filename prompt evaluation failed: {names}")


if __name__ == "__main__":
	main()
