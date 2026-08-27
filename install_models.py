#!/usr/bin/env python3
"""
Install and preload the local image caption models.
"""

import gc
import sys
import pathlib
import argparse
import subprocess
import importlib.util


REPO_ROOT = pathlib.Path(__file__).resolve().parent
RETIRED_CAPTION_MODEL_IDS = frozenset(
	(
		"moondream/moondream3-preview",
		"moondream/starmie-v1",
	)
)


#============================================
def ensure_rich(skip_pip: bool) -> None:
	"""Install Rich first when a fresh environment does not have it yet."""
	if importlib.util.find_spec("rich") is not None:
		return
	if skip_pip:
		raise RuntimeError(
			"Rich is not installed. Run install_models.py without --skip-pip first."
		)
	print("Preparing the Rich installer interface...")
	command = [sys.executable, "-m", "pip", "install", "--upgrade", "rich"]
	subprocess.run(command, cwd=REPO_ROOT, check=True)


#============================================
def configure_rich() -> None:
	"""Configure Rich for deliberate styling without automatic token highlighting."""
	import rich

	rich.reconfigure(highlight=False)


#============================================
def print_section(title: str) -> None:
	"""Print a visible Rich setup-stage heading."""
	import rich

	console = rich.get_console()
	console.print()
	console.rule(title, characters="=", style="bold cyan", align="left")


#============================================
def print_message(message: str, style: str | None = None) -> None:
	"""Print one literal message through Rich."""
	import rich

	console = rich.get_console()
	console.print(message, style=style, markup=False)


#============================================
def print_status(label: str, message: str, style: str) -> None:
	"""Print a compact styled status label followed by a literal message."""
	import rich
	import rich.text

	status_text = rich.text.Text()
	status_text.append(f"{label:<8}", style=style)
	status_text.append(message)
	console = rich.get_console()
	console.print(status_text)


#============================================
def print_setup_summary() -> None:
	"""Explain what the model setup command will do."""
	import rich
	import rich.panel

	summary = "This command will:\n"
	summary += "1. Upgrade the required Python packages.\n"
	summary += "2. Require Apple GPU acceleration through PyTorch MPS.\n"
	summary += "3. Download and validate Moondream2 and ViT-GPT2.\n"
	summary += "4. Remove explicitly retired screenshot-caption models.\n\n"
	summary += "Cached model files are reused. Ollama models are not downloaded."
	panel = rich.panel.Panel(
		summary,
		title="Image caption model setup",
		title_align="left",
		border_style="cyan",
		expand=False,
	)
	console = rich.get_console()
	console.print(panel, markup=False)


#============================================
def print_completion_summary() -> None:
	"""Print the successful final state in a green Rich panel."""
	import rich
	import rich.panel

	summary = "Moondream2 and ViT-GPT2 are cached and validated on Apple MPS.\n"
	summary += "Retired screenshot-caption cache entries are absent.\n"
	summary += "Run screenshot-renamer.py to process screenshots."
	panel = rich.panel.Panel(
		summary,
		title="Setup complete",
		title_align="left",
		border_style="green",
		expand=False,
	)
	console = rich.get_console()
	console.print(panel, markup=False)


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Install dependencies and preload the local image caption models."
	)
	parser.add_argument(
		'-s', '--skip-pip',
		dest='skip_pip',
		action='store_true',
		help="Skip pip installation and only preload the caption models.",
	)
	args = parser.parse_args()
	return args


#============================================
def run_command(command: list[str]) -> None:
	"""
	Run a setup command in the repository root.
	"""
	print_message("$ " + " ".join(command), style="dim")
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
		"--upgrade",
		"-r",
		"pip_requirements.txt",
	]
	run_command(command)


#============================================
def purge_retired_caption_models() -> None:
	"""Delete explicitly retired project models from the Hugging Face cache."""
	import huggingface_hub

	print_section("5. RETIRED MODEL CLEANUP")
	cache_info = huggingface_hub.scan_cache_dir()
	retired_repos = [
		repo
		for repo in cache_info.repos
		if repo.repo_type == "model" and repo.repo_id in RETIRED_CAPTION_MODEL_IDS
	]
	retired_repos.sort(key=lambda repo: repo.repo_id)

	if not retired_repos:
		print_status("CLEAN", "No retired screenshot-caption models are cached.", "bold green")
		return

	revision_hashes = []
	for repo in retired_repos:
		message = f"{repo.repo_id} ({repo.size_on_disk_str})"
		print_status("REMOVE", message, "bold yellow")
		for revision in repo.revisions:
			revision_hashes.append(revision.commit_hash)

	delete_strategy = cache_info.delete_revisions(*revision_hashes)
	message = f"Expected cache recovery: {delete_strategy.expected_freed_size_str}"
	print_status("INFO", message, "bold cyan")
	delete_strategy.execute()
	remaining_cache_info = huggingface_hub.scan_cache_dir()
	remaining_retired_ids = sorted(
		repo.repo_id
		for repo in remaining_cache_info.repos
		if repo.repo_type == "model" and repo.repo_id in RETIRED_CAPTION_MODEL_IDS
	)
	if remaining_retired_ids:
		raise RuntimeError(
			"Retired model cleanup incomplete: " + ", ".join(remaining_retired_ids)
		)
	print_status("CLEAN", "Retired model cleanup complete.", "bold green")


#============================================
def preload_caption_models() -> None:
	"""
	Download and instantiate each local image caption model.
	"""
	import screenshot_lib.common_func

	print_section("2. APPLE ACCELERATOR CHECK")
	device = screenshot_lib.common_func.get_mps_device()
	message = f"{device.upper()} - Apple GPU through Metal Performance Shaders"
	print_status("READY", message, "bold green")
	print_message("CPU and CUDA fallbacks are disabled for local caption models.", style="dim")
	print_message("PyTorch does not expose the Apple Neural Engine as a general device.", style="dim")
	print_message("Apple system models choose their supported accelerators through macOS.", style="dim")

	import screenshot_lib.generate_caption

	print_section("3. MOONDREAM CAPTION MODEL")
	print_status("MODEL", screenshot_lib.generate_caption.MOONDREAM2_MODEL_ID, "bold magenta")
	print_message(
		"Moondream3 Preview requires FlexAttention, so Moondream2 is the current "
		"MPS-compatible release.",
		style="dim",
	)
	print_status("INFO", "Downloading missing Hugging Face files or using the cache.", "bold cyan")
	components = screenshot_lib.generate_caption.setup_ai_components(backend="moondream")
	model_id = components["model_id"]
	print_status("READY", f"Moondream ready: {model_id}", "bold green")
	del components
	gc.collect()

	print_section("4. VIT-GPT2 CAPTION MODEL")
	print_status("MODEL", screenshot_lib.generate_caption.VIT_GPT2_MODEL_ID, "bold magenta")
	print_status("INFO", "Downloading missing model, processor, and tokenizer files.", "bold cyan")
	components = screenshot_lib.generate_caption.setup_ai_components(backend="vit-gpt2")
	print_status("READY", f"ViT-GPT2 ready on {components['device'].upper()}.", "bold green")
	del components
	gc.collect()

	purge_retired_caption_models()
	print_completion_summary()


#============================================
def main() -> None:
	"""
	Install dependencies and preload the image caption models.
	"""
	args = parse_args()
	ensure_rich(args.skip_pip)
	configure_rich()
	print_setup_summary()
	print_section("1. PYTHON DEPENDENCIES")
	if not args.skip_pip:
		print_status("INFO", "Upgrading the declared Python dependency set.", "bold cyan")
		install_dependencies()
	else:
		print_status("SKIP", "Dependency upgrade skipped by --skip-pip.", "bold yellow")
	preload_caption_models()


if __name__ == "__main__":
	main()
