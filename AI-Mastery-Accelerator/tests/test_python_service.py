import pytest
from pydantic import ValidationError

from ai_mastery.python_service import AnswerService, Question, RuleBasedGenerator


class FakeGenerator:
    async def generate(self, question: str) -> str:
        return f"fake:{question}"


@pytest.mark.asyncio
async def test_service_uses_generator() -> None:
    service = AnswerService(FakeGenerator())

    result = await service.answer(Question(text="Domanda valida"))

    assert result == "fake:Domanda valida"


@pytest.mark.asyncio
async def test_rule_based_generator_handles_leave_question() -> None:
    generator = RuleBasedGenerator()

    result = await generator.generate("Come richiedo le ferie?")

    assert result == "Consulta la procedura ferie."


def test_question_rejects_short_text() -> None:
    with pytest.raises(ValidationError):
        Question(text="x")
