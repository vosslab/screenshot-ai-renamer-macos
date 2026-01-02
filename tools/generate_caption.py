#!/usr/bin/env python3

import logging
import time
from typing import Dict

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

from tools import common_func


def _caption_with_moondream(image_path: str, ai_components: Dict) -> str:
    """Run caption generation using the Moondream2 remote-code model."""
    image = Image.open(image_path).convert("RGB")
    image = common_func.resize_image(image, ai_components.get("max_dimension", 720))

    if ai_components.get("prompt"):
        caption_result = ai_components["model"].query(image, ai_components["prompt"])
        caption = caption_result.get("answer", "")
    else:
        caption_result = ai_components["model"].caption(image, length="normal")
        caption = caption_result.get("caption", "")

    return caption.strip()


def _caption_with_vit_gpt2(image_path: str, ai_components: Dict) -> str:
    """Run caption generation using the ViT-GPT2 encoder-decoder pipeline."""
    image = Image.open(image_path).convert("RGB")
    image = common_func.resize_image(image, ai_components.get("max_dimension", 1280))

    device = ai_components["device"]
    feature_extractor = ai_components["feature_extractor"]
    model = ai_components["model"]
    tokenizer = ai_components["tokenizer"]

    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
    attention_mask = common_func.get_attention_mask(pixel_values, device)

    output_ids = model.generate(
        pixel_values,
        num_beams=4,
        early_stopping=True,
        attention_mask=attention_mask,
        max_new_tokens=32,
    )

    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption.strip()


def _suppress_transformers_generation_warnings() -> None:
    """Silence noisy generation warnings that do not affect output quality."""
    logger = logging.getLogger("transformers.generation.utils")
    logger.setLevel(logging.ERROR)


def generate_caption(image_path: str, ai_components: Dict) -> str:
    """Generate a caption for a given image using the configured backend."""
    backend = ai_components.get("backend", "moondream")
    start_time = time.time()

    if backend == "vit-gpt2":
        caption = _caption_with_vit_gpt2(image_path, ai_components)
    else:
        caption = _caption_with_moondream(image_path, ai_components)

    if not caption:
        raise ValueError(f"Caption generation failed for backend '{backend}'.")

    ai_components["_last_caption_runtime"] = time.time() - start_time
    return caption


def setup_ai_components(prompt: str = None, backend: str = "moondream") -> Dict:
    """Setup AI components, loading the requested captioning backend."""
    backend = (backend or "moondream").lower()
    device = common_func.get_mps_device()

    if backend == "vit-gpt2":
        _suppress_transformers_generation_warnings()
        from transformers import GPT2Tokenizer, ViTImageProcessor, VisionEncoderDecoderModel

        model_name = "nlpconnect/vit-gpt2-image-captioning"
        model = VisionEncoderDecoderModel.from_pretrained(model_name)
        feature_extractor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model.to(device)

        return {
            "backend": backend,
            "model": model,
            "feature_extractor": feature_extractor,
            "tokenizer": tokenizer,
            "device": device,
            "prompt": prompt,
            "max_dimension": 1280,
        }

    model_id = "vikhyatk/moondream2"
    revision = "2025-01-09"
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        revision=revision,
        dtype=torch.float16,
        device_map={"": device},
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
    model.to(device)

    return {
        "backend": "moondream",
        "model": model,
        "tokenizer": tokenizer,
        "device": device,
        "prompt": prompt,
        "max_dimension": 720,
    }
