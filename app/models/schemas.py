from pydantic import BaseModel, EmailStr, Field


class LeadWebhookPayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    message: str = Field(min_length=1, max_length=5000)
    company: str = Field(default="", max_length=200)
    phone: str = Field(default="", max_length=50)


class LeadScoreResponse(BaseModel):
    status: str  # "hot" | "warm" | "cold"
    matched_service: str
    confidence: int  # 0-100
    score: int  # 0-100
    summary: str
