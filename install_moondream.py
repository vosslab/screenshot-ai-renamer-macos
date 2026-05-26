#!/usr/bin/env python3
"""
Install and preload the latest Moondream caption backend.
"""

import argparse
import pathlib
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Install dependencies and preload the latest Moondream model."
	)
	parser.add_argument(
		'-s', '--skip-pip',
		dest='skip_pip',
		action='store_true',
		help="Skip pip installation and only preload the model.",
	)
	args = parser.parse_args()
	return args


#============================================
def run_command(command: list[str]) -> None:
	"""
	Run a setup command in the repository root.
	"""
	print(" ".join(command))
	subprocess.run(command, cwd=REPO_ROOT, check=True)


#============================================
def install_dependencies() -> None:
	"""
	Install the repository dependency set with the current Python interpreter.
	"""
	command = [
		sys.executable,
		"-m",
		"pip",
		"install",
		"-r",
		"pip_requirements.txt",
	]
	run_command(command)


#============================================
def preload_moondream() -> None:
	"""
	Download and instantiate the latest Moondream model.
	"""
	import tools.generate_caption

	print("Downloading model files from Hugging Face if needed.")
	print("Caption inference runs locally after the files are cached.")
	print("Preloading latest Moondream model...")
	components = tools.generate_caption.setup_ai_components(backend="moondream")
	model_id = tools.generate_caption.MOONDREAM_MODEL_ID
	print(f"Moondream ready: {model_id}")
	del components


#============================================
def main() -> None:
	"""
	Install dependencies and preload Moondream.
	"""
	args = parse_args()
	if not args.skip_pip:
		install_dependencies()
	preload_moondream()


if __name__ == "__main__":
	main()
