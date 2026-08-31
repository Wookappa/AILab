"""Minimal FastAPI service used by the production beginner lesson."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AI Mastery Example")


class AnswerRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)


class AnswerResponse(BaseModel):
    answer: str
    status: str


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/answers")
async def answer(request: AnswerRequest) -> AnswerResponse:
    return AnswerResponse(
        answer=f"Ricevuto: {request.question}",
        status="answered",
    )
