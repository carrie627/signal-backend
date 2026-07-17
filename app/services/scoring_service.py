import re

from app.core.config import get_settings

URGENCY_PATTERNS = re.compile(
    r"\b(asap|urgent|this week|right away|immediately|as soon as possible)\b",
    re.IGNORECASE,
)
BUDGET_PATTERNS = re.compile(
    r"\b(budget|\$\d|invest|pricing|quote|proposal)\b",
    re.IGNORECASE,
)
LOW_INTENT_PATTERNS = re.compile(
    r"\b(just looking|just exploring|not in a rush|curious|no rush)\b",
    re.IGNORECASE,
)


def compute_composite_score(message: str, match_confidence: int) -> int:
    """Blends semantic match confidence with cheap rule-based intent
    signals. Deliberately not ML — thresholds and weights need to stay
    something a non-technical client can understand and you can tune
    per-client without retraining anything."""
    score = match_confidence * 0.6  # semantic match is the base signal

    if URGENCY_PATTERNS.search(message):
        score += 15
    if BUDGET_PATTERNS.search(message):
        score += 15
    if LOW_INTENT_PATTERNS.search(message):
        score -= 25
    if len(message.strip()) < 20:
        score -= 10  # very short messages tend to be low-intent

    return max(0, min(100, round(score)))


def classify_status(score: int) -> str:
    settings = get_settings()
    if score >= settings.hot_threshold:
        return "hot"
    if score >= settings.warm_threshold:
        return "warm"
    return "cold"
