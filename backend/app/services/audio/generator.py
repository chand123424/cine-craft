import math
import os
import struct
import wave
import base64
from pathlib import Path
from uuid import uuid4

import httpx


def generate_audio(text: str, duration: float, output_dir: str) -> tuple[str, str]:
    """Use Google Cloud TTS when configured, otherwise create deterministic local demo audio."""
    path = Path(output_dir, f"{uuid4()}.wav")
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if api_key and text:
        response = httpx.post(
            "https://texttospeech.googleapis.com/v1/text:synthesize",
            params={"key": api_key},
            json={
                "input": {"text": text},
                "voice": {"languageCode": os.getenv("GOOGLE_TTS_LANGUAGE", "en-US"), "name": os.getenv("GOOGLE_TTS_VOICE", "en-US-Neural2-F")},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 16_000},
            },
            timeout=60,
        )
        response.raise_for_status()
        path.write_bytes(base64.b64decode(response.json()["audioContent"]))
        return str(path), "google"

    sample_rate = 16_000
    frames = int(sample_rate * duration)
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        for index in range(frames):
            value = int(500 * math.sin(2 * math.pi * 220 * index / sample_rate)) if text else 0
            audio.writeframes(struct.pack("<h", value))
    return str(path), "demo"