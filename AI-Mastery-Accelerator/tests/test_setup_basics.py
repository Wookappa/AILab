from pathlib import Path

import pytest

from ai_mastery.setup_basics import count_labels, load_tickets


def test_load_and_count_example_tickets() -> None:
    path = Path(__file__).parents[1] / "examples" / "tickets.jsonl"

    tickets = load_tickets(path)

    assert len(tickets) == 4
    assert count_labels(tickets) == {
        "contract": 1,
        "leave": 1,
        "payroll": 2,
    }


def test_missing_field_reports_line_number(tmp_path: Path) -> None:
    path = tmp_path / "invalid.jsonl"
    path.write_text('{"id":"t-001","text":"Missing label"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"Riga 1: campi mancanti: label"):
        load_tickets(path)
