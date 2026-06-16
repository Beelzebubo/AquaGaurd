"""Voice alert generation using ElevenLabs TTS.

Gracefully degrades when the API key is missing.
"""
import os
import uuid

from elevenlabs.client import ElevenLabs

from app.config import ELEVENLABS_API_KEY


def generate_voice_alert(text: str) -> str | None:
    """Generate TTS audio and return the URL path, or None if unavailable."""

    # Graceful degradation if no API key is configured
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY.startswith("your_e"):
        return None

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    os.makedirs("audio", exist_ok=True)

    try:
        audio_stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            text=text,
        )

        filename = f"{uuid.uuid4()}.mp3"
        output_path = f"audio/{filename}"

        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return f"/audio/{filename}"
    except Exception as e:
        print(f"TTS generation failed (non-critical): {e}")
        return None
