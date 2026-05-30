import os
import uuid

from elevenlabs.client import ElevenLabs

from app.config import ELEVENLABS_API_KEY

# Client init garya basically api key le service access garya
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)


def generate_voice_alert(text):

    # Audio bhanne directory(Folder) create garya exist gardaina bhane.
    os.makedirs(
        "audio",
        exist_ok=True
    )
    
    # basically 11labs ko api le unique voice generate garya, voice_id le specify garya kun voice use garne, model le kun model use garne specify garya.
    # text le kun text lai voice ma convert garya specify garya.
    audio_stream = client.text_to_speech.convert(
        voice_id="EXAVITQu4vr4xnSDxMaL",
        model_id="eleven_multilingual_v2",
        text=text
    )

    # Unique filename to avoid overrinding
    filename = f"{uuid.uuid4()}.mp3"

    output_path = f"audio/{filename}"

    # the saving of audio takes place here, Chunk ma lekda large audio files handle garna sajilo hunxa, and it alsi helps tosave memory.
    with open(output_path, "wb") as f:

        for chunk in audio_stream:
            f.write(chunk)
# public url path return garya, jasma audio file access garna sakinxa, basically FastApi ko static file use garera audio file serve garya, so it can be accessed via URl.
    return f"/audio/{filename}"