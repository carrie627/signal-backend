import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


async def summarize_lead(message: str) -> str:
    """Condenses the lead's message into one line for the Slack alert.
    Falls back to a truncated version of the raw message if no API key is
    configured or the call fails — this must never block lead processing."""
    settings = get_settings()

    if not settings.groq_api_key:
        return _fallback_summary(message)

    payload = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Summarize the lead's message in one short sentence "
                    "focused on their need. No preamble, no quotes."
                ),
            },
            {"role": "user", "content": message},
        ],
        "max_tokens": 60,
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(GROQ_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        logger.warning("Groq summary failed, falling back: %s", exc)
        return _fallback_summary(message)


def _fallback_summary(message: str) -> str:
    stripped = message.strip()
    return stripped if len(stripped) <= 100 else f"{stripped[:97]}..."
