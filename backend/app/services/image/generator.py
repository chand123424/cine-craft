import os
from pathlib import Path
from uuid import uuid4

import httpx
from PIL import Image, ImageDraw


def generate_image(prompt: str, output_dir: str, provider: str = "demo") -> tuple[str, str]:
    """Use Hugging Face when configured, otherwise create deterministic local demo media."""
    filename = f"{uuid4()}.png"
    path = Path(output_dir, filename)
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if api_key:
        model = os.getenv("HUGGINGFACE_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
        response = httpx.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": prompt},
            timeout=120,
        )
        response.raise_for_status()
        path.write_bytes(response.content)
        return str(path), "huggingface"

    image = Image.new("RGB", (1080, 1920), (21, 31, 46))
    draw = ImageDraw.Draw(image)
    draw.text((70, 140), "CineCraft", fill=(240, 210, 130))
    draw.text((70, 190), prompt[:180], fill=(235, 235, 235))
    image.save(path)
    return str(path), provider