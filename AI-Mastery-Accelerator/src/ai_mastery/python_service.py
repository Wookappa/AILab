"""Small asynchronous service used by the Python beginner lesson."""

from __future__ import annotations

import asyncio
import sys
from typing import Protocol

from pydantic import BaseModel, Field, ValidationError


class Question(BaseModel):
    text: str = Field(min_length=3, max_length=2_000)


class Generator(Protocol):
    async def generate(self, question: str) -> str: ...


class RuleBasedGenerator:
    async def generate(self, question: str) -> str:
        normalized = question.lower()
        if "ferie" in normalized:
            return "Consulta la procedura ferie."
        if "cedolino" in normalized:
            return "Consulta la procedura payroll."
        return "Non conosco ancora la risposta."


class AnswerService:
    def __init__(self, generator: Generator) -> None:
        self._generator = generator

    async def answer(self, question: Question) -> str:
        return await self._generator.generate(question.text)


async def run(question_text: str) -> str:
    service = AnswerService(RuleBasedGenerator())
    return await service.answer(Question(text=question_text))


def main() -> int:
    if len(sys.argv) != 2:
        print('Uso: python -m ai_mastery.python_service "LA TUA DOMANDA"')
        return 2

    try:
        print(asyncio.run(run(sys.argv[1])))
    except ValidationError as error:
        print(f"Domanda non valida:\n{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
