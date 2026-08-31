from fastapi.testclient import TestClient

from ai_mastery.production_app import app

client = TestClient(app)


def test_liveness() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_answer_validates_and_echoes_question() -> None:
    response = client.post(
        "/v1/answers",
        json={"question": "Come richiedo le ferie?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Ricevuto: Come richiedo le ferie?",
        "status": "answered",
    }


def test_answer_rejects_short_question() -> None:
    response = client.post("/v1/answers", json={"question": "x"})

    assert response.status_code == 422
