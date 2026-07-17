import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def notify_zapier(
    status: str,
    name: str,
    company: str,
    matched_service: str,
    confidence: int,
    score: int,
    summary: str,
) -> None:
    """Fires the correct Zapier 'Catch Hook' URL depending on lead status.
    Two separate 2-step Zaps (hot-path and default-path) is how the free
    plan's lack of built-in Paths/Filters gets worked around — the branch
    decision already happened in this backend, so each Zap just reacts."""
    settings = get_settings()
    url = (
        settings.zapier_hot_webhook_url
        if status == "hot"
        else settings.zapier_default_webhook_url
    )

    if not url:
        logger.info("No Zapier webhook URL configured for status=%s, skipping", status)
        return

    payload = {
        "status": status,
        "name": name,
        "company": company,
        "matched_service": matched_service,
        "confidence": confidence,
        "score": score,
        "summary": summary,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.HTTPError:
        logger.exception("Failed to notify Zapier for status=%s", status)
