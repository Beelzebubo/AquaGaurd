import google.generativeai as genai

from app.config import GEMINI_API_KEY

from app.services.voice_service import (
    generate_voice_alert
)


# Make Gemini ready (config)
genai.configure(
    api_key=GEMINI_API_KEY
)


# Load the gemini model( model load garya generate content garna)
model = genai.GenerativeModel(
    "gemini-1.5-flash"
)


def generate_compliance_summary(data):
# summary generate garna ko lagi gemini use garne
# basically yele data lai prompt ma halera summary generate garne kam garxa
    prompt = f"""
    River Flow: {data['river_flow']}
    Rainfall: {data['rainfall']}
    Humidity: {data['humidity']}
    Compliance Score: {data['compliance_score']}

    Generate a concise IFC PS4 compliance summary
    for a hydropower ESG monitoring dashboard.

    Mention:
    - ecological flow conditions
    - environmental risk
    - operational status
    - compliance interpretation

    Keep it professional and concise.
    """

    # ya bata prompt generate garya thyo ni mathi bata tyo prompt lai model ma halera summary generate grinxa
    response = model.generate_content(
        prompt
    )
# gemini le generate gareko summary lai text ma store garne ya bata
    summary = response.text

    # ya bata generated text file lai mp3 ma convert garne kam hunxa
    # yei ma eleven labs ko voice service ko kam lagxa.
    audio_file = generate_voice_alert(
        summary
    )
# ya bata summary ra audio files haru directory ma store garinxa
# ya bata frontend ma summary ra audio file path send garinxa jaslai use garera frontend le response dinxa.
    return {

        "summary": summary,

        "audio_file": audio_file
    }