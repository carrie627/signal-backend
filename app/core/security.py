import hmac

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def verify_webhook_secret(x_webhook_secret: str = Header(default="")) -> None:
    settings = get_settings()

    # hmac.compare_digest avoids leaking timing information about how much
    # of the secret matched, which a simple `==` check would not.
    if not hmac.compare_digest(x_webhook_secret, settings.webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Webhook-Secret header",
        )
