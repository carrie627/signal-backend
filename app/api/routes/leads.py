from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.security import verify_webhook_secret
from app.models.schemas import LeadScoreResponse, LeadWebhookPayload
from app.services import (
    embedding_service,
    notification_service,
    scoring_service,
    sheets_service,
    summary_service,
)

router = APIRouter()


@router.post(
    "/webhook/lead",
    response_model=LeadScoreResponse,
    dependencies=[Depends(verify_webhook_secret)],
)
async def score_lead(
    payload: LeadWebhookPayload, background_tasks: BackgroundTasks
) -> LeadScoreResponse:
    lead_embedding = embedding_service.embed_text(payload.message)
    matched_service, confidence = embedding_service.match_service(lead_embedding)

    score = scoring_service.compute_composite_score(payload.message, confidence)
    status = scoring_service.classify_status(score)

    # Awaited here (not backgrounded) because the summary is part of the
    # response body and feeds the Slack alert — Groq's free tier is fast
    # enough that this doesn't meaningfully delay the ack to Zap 1.
    summary = await summary_service.summarize_lead(payload.message)

    # Sheet write and outbound webhook run after the response is sent —
    # neither should add latency to Zap 1's request.
    background_tasks.add_task(
        sheets_service.append_lead_row,
        name=payload.name,
        email=payload.email,
        company=payload.company,
        message=payload.message,
        matched_service=matched_service,
        confidence=confidence,
        score=score,
        status=status,
        summary=summary,
    )
    background_tasks.add_task(
        notification_service.notify_zapier,
        status=status,
        name=payload.name,
        company=payload.company,
        matched_service=matched_service,
        confidence=confidence,
        score=score,
        summary=summary,
    )

    return LeadScoreResponse(
        status=status,
        matched_service=matched_service,
        confidence=confidence,
        score=score,
        summary=summary,
    )
