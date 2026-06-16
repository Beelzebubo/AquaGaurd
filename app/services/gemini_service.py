"""Gemini-powered compliance summary generation.

Falls back to a rule-based summary when the API key is missing.
"""
from app.config import GEMINI_API_KEY


def generate_compliance_summary(data: dict) -> dict:
    """Generate a compliance summary using Gemini AI (or rule-based fallback)."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_g...n":
        return _fallback_summary(data)

    try:
        import google.genai as genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        model = "gemini-2.0-flash"

        prompt = f"""
River Flow: {data.get('river_flow', 'N/A')}
Rainfall: {data.get('rainfall', 'N/A')}
Humidity: {data.get('humidity', 'N/A')}
Compliance Score: {data.get('compliance_score', 'N/A')}

Generate a concise IFC PS4 compliance summary
for a hydropower ESG monitoring dashboard in Nepal.
Mention:
- ecological flow conditions
- environmental risk
- operational status
- compliance interpretation

Keep it professional and concise.
"""
        response = client.models.generate_content(model=model, contents=prompt)
        return {"summary": response.text.strip()}

    except Exception as e:
        print(f"Gemini summary failed: {e}")
        return _fallback_summary(data)


def _fallback_summary(data: dict) -> dict:
    """Rule-based fallback when Gemini is unavailable."""
    rf = data.get("river_flow", 0)
    cs = data.get("compliance_score", 50)
    status = "meeting" if cs >= 70 else "approaching" if cs >= 50 else "falling below"
    summary = (
        f"River flow is {rf} m³/s. "
        f"IFC PS4 compliance score is {cs}/100 — {status} ecological-flow requirements. "
        f"Environmental risk is {'low' if cs >= 70 else 'moderate' if cs >= 50 else 'elevated'}. "
        "Operational status: nominal."
    )
    return {"summary": summary}
