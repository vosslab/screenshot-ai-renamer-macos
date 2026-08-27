#!/usr/bin/env python3
"""Install, preload, and validate the local image-caption models."""

import gc
import sys
import pathlib
import argparse
import tempfile
import subprocess
import importlib.util


REPO_ROOT = pathlib.Path(__file__).resolve().parent
RETIRED_CAPTION_MODEL_IDS = frozenset((
	"moondream/moondream3-preview",
	"vikhyatk/moondream2",
))


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
	status_text.append(f"{label:<10}", style=style)
	status_text.append(message)
	console = rich.get_console()
	console.print(status_text)


#============================================
def print_setup_summary() -> None:
	"""Explain what the model setup command will do."""
	import rich
	import rich.panel

	summary = "This command will:\n"
	summary += "1. Upgrade Python packages within declared compatibility ranges.\n"
	summary += "2. Verify native Metal and PyTorch MPS acceleration.\n"
	summary += "3. Download and validate Moondream 3.1 through Photon.\n"
	summary += "4. Cache and validate the ViT-GPT2 MPS captioner.\n"
	summary += "5. Clear retired caption-model cache entries.\n\n"
	summary += "Cached model files are reused.\n"
	summary += "Model identities and SDK package versions are separate; see docs/MODELS.md."
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
def print_completion_summary(
	photon_ready: bool,
	photon_issue: str | None,
) -> None:
	"""Print the validated final state and any Photon compatibility issue."""
	import rich
	import rich.panel

	if photon_ready:
		summary = "Moondream 3.1 is ready through Photon Metal.\n"
		border_style = "green"
	elif photon_issue is not None:
		summary = "Moondream 3.1 Photon is not available in this environment.\n"
		issue_summary = photon_issue.splitlines()[0]
		summary += f"Reason: {issue_summary}\n"
		summary += "See the Moondream 3.1 section above for details.\n"
		border_style = "yellow"
	else:
		summary = "Moondream 3.1 was skipped because this Mac has less than 24 GB.\n"
		border_style = "yellow"
	summary += "ViT-GPT2 is ready through PyTorch MPS.\n"
	summary += "Every available caption backend passed a real inference sanity check.\n"
	summary += "Run screenshot-renamer.py to process screenshots."
	panel = rich.panel.Panel(
		summary,
		title="Setup complete",
		title_align="left",
		border_style=border_style,
		expand=False,
	)
	console = rich.get_console()
	console.print(panel, markup=False)


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Install dependencies and validate the local image-caption models."
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
	"""Run a setup command in the repository root."""
	print_message("$ " + " ".join(command), style="dim")
	subprocess.run(command, cwd=REPO_ROOT, check=True)


#============================================
def install_dependencies() -> None:
	"""Install the repository dependency set with the current interpreter."""
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
def create_validation_image(directory: str) -> str:
	"""Create a temporary visual sanity-check image for real model inference."""
	import PIL.Image
	import PIL.ImageDraw

	image_path = pathlib.Path(directory) / "caption_validation.png"
	image = PIL.Image.new("RGB", (640, 360), "white")
	drawing = PIL.ImageDraw.Draw(image)
	drawing.text((30, 25), "CAPTION MODEL TEST", fill="black")
	drawing.rectangle((40, 100, 260, 300), fill="red")
	drawing.ellipse((360, 100, 580, 300), fill="blue")
	image.save(image_path)
	return str(image_path)


#============================================
def validate_caption(caption: str, backend_name: str) -> None:
	"""Reject empty or repetitive model output and show a short successful sample."""
	import screenshot_lib.caption_quality

	screenshot_lib.caption_quality.require_usable_caption(caption, backend_name)
	preview = " ".join(caption.split())[:120]
	print_status("CHECK", preview, "bold green")


#============================================
def collect_retired_cache_entries(cache_info: object) -> list[tuple[str, str, str]]:
	"""Return model-cache entries explicitly retired by this project."""
	entries = []
	for repo in cache_info.repos:
		if repo.repo_type != "model":
			continue
		if repo.repo_id in RETIRED_CAPTION_MODEL_IDS:
			for revision in repo.revisions:
				entries.append((repo.repo_id, revision.commit_hash, "retired model"))
	entries.sort()
	return entries


#============================================
def purge_retired_caption_models() -> None:
	"""Delete only cache revisions explicitly retired by this project."""
	import huggingface_hub

	print_section("5. RETIRED MODEL CLEANUP")
	cache_info = huggingface_hub.scan_cache_dir()
	retired_entries = collect_retired_cache_entries(cache_info)
	if not retired_entries:
		print_status("CLEAN", "No retired screenshot-caption models are cached.", "bold green")
		return

	for repo_id, commit_hash, reason in retired_entries:
		message = f"{repo_id}@{commit_hash[:8]} ({reason})"
		print_status("REMOVE", message, "bold yellow")
	revision_hashes = sorted({entry[1] for entry in retired_entries})
	delete_strategy = cache_info.delete_revisions(*revision_hashes)
	message = f"Expected cache recovery: {delete_strategy.expected_freed_size_str}"
	print_status("INFO", message, "bold cyan")
	delete_strategy.execute()
	remaining_entries = collect_retired_cache_entries(huggingface_hub.scan_cache_dir())
	if remaining_entries:
		remaining_ids = [f"{entry[0]}@{entry[1][:8]}" for entry in remaining_entries]
		raise RuntimeError("Retired model cleanup incomplete: " + ", ".join(remaining_ids))
	print_status("CLEAN", "Retired model cleanup complete.", "bold green")


#============================================
def _validate_photon(validation_path: str) -> None:
	"""Run one Photon caption and always close an initialized engine."""
	import screenshot_lib.moondream_photon

	components = screenshot_lib.moondream_photon.setup_captioner()
	try:
		caption = screenshot_lib.moondream_photon.generate_caption(validation_path, components)
		validate_caption(caption, components["display_name"])
	finally:
		screenshot_lib.moondream_photon.close_captioner(components)


#============================================
def preload_photon(validation_path: str) -> str | None:
	"""Validate Photon, returning its exact availability failure when present."""
	import screenshot_lib.model_catalog

	print_section("3. MOONDREAM 3.1 PRIMARY")
	model_spec = screenshot_lib.model_catalog.MOONDREAM31_PHOTON
	print_status("MODEL", model_spec.model.model_id, "bold magenta")
	runtime_name = model_spec.runtime.runtime_id.title()
	accelerator_name = model_spec.runtime.accelerator.title()
	print_status("RUNTIME", f"{runtime_name} with native Apple {accelerator_name} kernels", "bold cyan")
	print_message("Downloading missing files or reusing the local cache.", style="dim")
	try:
		_validate_photon(validation_path)
	except Exception as exc:  # Native Photon failures do not share one exception hierarchy.
		failure = str(exc)
		print_status("FALLBACK", "Photon validation failed; selecting PyTorch MPS.", "bold yellow")
		print_message(failure, style="yellow")
		return failure
	print_status("READY", f"Moondream 3.1 ready: {model_spec.model.model_id}", "bold green")
	gc.collect()
	return None


#============================================
def preload_vit_gpt2(validation_path: str) -> None:
	"""Download and validate the secondary ViT-GPT2 MPS backend."""
	import screenshot_lib.generate_caption
	import screenshot_lib.model_catalog

	print_section("4. VIT-GPT2 MPS")
	model_spec = screenshot_lib.model_catalog.VIT_GPT2_MPS
	print_status("MODEL", model_spec.model.model_id, "bold magenta")
	print_message("Downloading missing model, processor, and tokenizer files.", style="dim")
	components = screenshot_lib.generate_caption.setup_ai_components(backend="vit-gpt2")
	caption = screenshot_lib.generate_caption.generate_caption(validation_path, components)
	validate_caption(caption, components["display_name"])
	print_status("READY", f"ViT-GPT2 ready on {components['device'].upper()}.", "bold green")
	del components
	gc.collect()


#============================================
def preload_caption_models() -> None:
	"""Download, instantiate, and exercise every production caption backend."""
	import screenshot_lib.common_func
	import screenshot_lib.model_catalog

	print_section("2. APPLE ACCELERATOR CHECK")
	metal_runtime = screenshot_lib.common_func.require_apple_silicon()
	mps_device = screenshot_lib.common_func.get_mps_device()
	total_memory = screenshot_lib.common_func.get_total_memory_bytes()
	memory_gib = total_memory / 1024 ** 3
	print_status("HARDWARE", f"{metal_runtime.upper()} - Apple Silicon Metal detected", "bold cyan")
	print_status("READY", f"{mps_device.upper()} - PyTorch Apple GPU runtime", "bold green")
	print_status("MEMORY", f"{memory_gib:.0f} GB unified memory detected", "bold cyan")

	photon_spec = screenshot_lib.model_catalog.MOONDREAM31_PHOTON
	photon_eligible = total_memory >= photon_spec.runtime.minimum_memory_bytes
	photon_ready = False
	photon_issue = None
	with tempfile.TemporaryDirectory(prefix="screenshot_caption_check_") as temp_directory:
		validation_path = create_validation_image(temp_directory)
		if photon_eligible:
			photon_issue = preload_photon(validation_path)
			photon_ready = photon_issue is None
		else:
			print_section("3. MOONDREAM 3.1 PRIMARY")
			print_status("SKIP", "Photon requires at least 24 GB unified memory.", "bold yellow")
		preload_vit_gpt2(validation_path)

	purge_retired_caption_models()
	print_completion_summary(photon_ready, photon_issue)


#============================================
def main() -> None:
	"""Install dependencies and preload the image-caption models."""
	args = parse_args()
	ensure_rich(args.skip_pip)
	configure_rich()
	print_setup_summary()
	print_section("1. PYTHON DEPENDENCIES")
	if not args.skip_pip:
		message = "Upgrading dependencies; Torch stays on the Photon-compatible 2.12 minor."
		print_status("INFO", message, "bold cyan")
		install_dependencies()
	else:
		print_status("SKIP", "Dependency upgrade skipped by --skip-pip.", "bold yellow")
	preload_caption_models()


if __name__ == "__main__":
	main()
