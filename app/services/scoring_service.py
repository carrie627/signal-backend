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
    per-client without retraining anything.

    Confidence alone is capped at 0.5 weight (max 50 points) rather than
    0.6, specifically so that a lead hitting every intent signal (urgency +
    budget + strong match) can still cross the hot threshold even when the
    semantic match isn't a perfect 100% — a moderate-confidence match with
    explicit urgency and budget language is a stronger buying signal than
    confidence alone would suggest.
    """
    score = match_confidence * 0.5

    has_urgency = bool(URGENCY_PATTERNS.search(message))
    has_budget = bool(BUDGET_PATTERNS.search(message))

    if has_urgency:
        score += 20
    if has_budget:
        score += 20
    if has_urgency and has_budget:
        score += 10

    if LOW_INTENT_PATTERNS.search(message):
        score -= 30
    if len(message.strip()) < 20:
        score -= 10

    return max(0, min(100, round(score)))


def classify_status(score: int) -> str:
    settings = get_settings()
    if score >= settings.hot_threshold:
        return "hot"
    if score >= settings.warm_threshold:
        return "warm"
    return "cold"
