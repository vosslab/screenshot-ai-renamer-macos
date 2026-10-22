#!/usr/bin/env python3
"""Update this project's runtime, then process screenshots with what is usable."""

import re
import sys
import pathlib
import argparse
import datetime
import subprocess

import screenshot_lib.model_catalog


#============================================
def run_step(command: list[str], directory: pathlib.Path) -> bool:
	"""Log a command; an update failure does not prevent subsequent work."""
	stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
	print(f"\n[{stamp}] {' '.join(command)}", flush=True)
	try:
		result = subprocess.run(command, cwd=directory, check=False)
	except OSError as exc:
		print(f"WARNING: {exc}", flush=True)
		return False
	if result.returncode:
		print(f"WARNING: command exited {result.returncode}", flush=True)
	return result.returncode == 0


#============================================
def main() -> None:
	"""Perform bounded dependency updates and launch a fresh processing process."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-d', '--directory', dest='directory',
		default=str(pathlib.Path.home() / 'Documents/SynDocuments/ScreenShots'))
	parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true',
		help='Skip updates and preview screenshot processing without changing images.')
	args = parser.parse_args()
	root = pathlib.Path(subprocess.check_output(
		['git', 'rev-parse', '--show-toplevel'],
		cwd=pathlib.Path(__file__).resolve().parent, text=True,
	).strip())
	if not args.dry_run:
		brew = '/opt/homebrew/bin/brew'
		run_step([brew, 'update'], root)
		formulas = re.findall(r'^brew "([^"]+)"', (root / 'Brewfile').read_text(), re.MULTILINE)
		for formula in formulas:
			# Restart Ollama only if Homebrew actually replaces its executable.
			ollama_path = pathlib.Path('/opt/homebrew/opt/ollama').resolve()
			run_step([brew, 'upgrade', '--formula', formula], root)
			if formula == 'ollama' and pathlib.Path('/opt/homebrew/opt/ollama').resolve() != ollama_path:
				run_step([brew, 'services', 'restart', 'ollama'], root)
		run_step([sys.executable, '-m', 'pip', 'install', '--upgrade',
			'--upgrade-strategy', 'eager', '-r', 'pip_requirements.txt'], root)
		run_step([sys.executable, 'install_models.py', '--skip-pip'], root)
		model_id = screenshot_lib.model_catalog.QWEN_FILENAME_MODEL.model_id
		run_step(['/opt/homebrew/bin/ollama', 'pull', model_id], root)
	# The normal pipeline checks actual usability and omits unavailable captioners.
	# Always start it in a fresh interpreter after package updates, even failed ones.
	command = [sys.executable, 'screenshot-renamer.py', '--directory', args.directory,
		'--shuffle', '--no-color']
	if args.dry_run:
		command.append('--dry-run')
	success = run_step(command, root)
	print(f"Nightly processing {'completed' if success else 'failed'}.", flush=True)
	if not success:
		raise RuntimeError('Screenshot processing failed; see the preceding log output.')


if __name__ == '__main__':
	main()
