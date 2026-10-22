#!/usr/bin/env python3
"""Run screenshot processing or manage its daily 22:30 user LaunchAgent."""

import os
import plistlib
import pathlib
import argparse
import subprocess


LABEL = 'local.vosslab.screenshot-renamer'
PYTHON = '/opt/homebrew/opt/python@3.12/bin/python3.12'


#============================================
def agent_config(root: pathlib.Path, directory: pathlib.Path, logs: pathlib.Path) -> dict:
	"""Describe a scheduled job without running it on installation."""
	config = {
		'Label': LABEL,
		'ProgramArguments': [PYTHON, '-u', str(root / 'run_nightly.py'),
			'--directory', str(directory)],
		'WorkingDirectory': str(root),
		'StartCalendarInterval': {'Hour': 22, 'Minute': 30},
		'EnvironmentVariables': {
			'PATH': '/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin',
			'PYTHONDONTWRITEBYTECODE': '1',
		},
		'StandardOutPath': str(logs / 'screenshot-renamer.log'),
		'StandardErrorPath': str(logs / 'screenshot-renamer.error.log'),
	}
	return config


#============================================
def main() -> None:
	"""Write and register the user agent, or remove this agent alone."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-d', '--directory', dest='directory', type=pathlib.Path,
		default=pathlib.Path.home() / 'Documents/SynDocuments/ScreenShots')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-c', '--check', action='store_true',
		help='Show the installed schedule and launchd status.')
	group.add_argument('-R', '--run', action='store_true',
		help='Update project dependencies and process screenshots now.')
	group.add_argument('-n', '--dry-run', action='store_true',
		help='Preview screenshot processing without updates or image changes.')
	group.add_argument('-i', '--install-schedule', '--install', action='store_true',
		help='Install or replace the daily 22:30 user LaunchAgent.')
	group.add_argument('-r', '--remove-schedule', '-u', '--uninstall', action='store_true',
		help='Unload and remove the user LaunchAgent.')
	args = parser.parse_args()
	domain = f'gui/{os.getuid()}'
	target = f'{domain}/{LABEL}'
	plist_path = pathlib.Path.home() / 'Library/LaunchAgents' / f'{LABEL}.plist'
	if args.check:
		print(f'LaunchAgent: {plist_path}', flush=True)
		if plist_path.exists():
			config = plistlib.loads(plist_path.read_bytes())
			print(f'Schedule: {config.get("StartCalendarInterval")}', flush=True)
			print(f'Command: {config.get("ProgramArguments")}', flush=True)
		result = subprocess.run(['launchctl', 'print', target], check=False)
		raise SystemExit(result.returncode)
	if args.run or args.dry_run:
		command = [PYTHON, str(pathlib.Path(__file__).resolve().with_name('run_nightly.py')),
			'--directory', str(args.directory.expanduser())]
		if args.dry_run:
			command.append('--dry-run')
		raise SystemExit(subprocess.run(command, check=False).returncode)
	if args.remove_schedule:
		subprocess.run(['launchctl', 'bootout', target], check=False, capture_output=True)
		plist_path.unlink(missing_ok=True)
		print(f'Removed {LABEL}; logs and screenshots retained.')
		return
	directory = args.directory.expanduser().resolve(strict=True)
	if not directory.is_dir():
		raise NotADirectoryError(directory)
	root = pathlib.Path(subprocess.check_output(
		['git', 'rev-parse', '--show-toplevel'],
		cwd=pathlib.Path(__file__).resolve().parent, text=True,
	).strip())
	logs = pathlib.Path.home() / 'Library/Logs'
	logs.mkdir(parents=True, exist_ok=True)
	plist_path.parent.mkdir(parents=True, exist_ok=True)
	plist_path.write_bytes(plistlib.dumps(agent_config(root, directory, logs)))
	subprocess.run(['plutil', '-lint', str(plist_path)], check=True)
	subprocess.run(['launchctl', 'bootout', target], check=False, capture_output=True)
	subprocess.run(['launchctl', 'enable', target], check=True)
	subprocess.run(['launchctl', 'bootstrap', domain, str(plist_path)], check=True)
	print(f'Installed {LABEL}: every day at 22:30 local time for {directory}.')
	print(f'Logs: {logs / "screenshot-renamer.log"} and screenshot-renamer.error.log')


if __name__ == '__main__':
	main()
