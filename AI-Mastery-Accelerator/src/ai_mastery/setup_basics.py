"""Small JSONL statistics program used by the first course lesson."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

Ticket = dict[str, str]
REQUIRED_FIELDS = {"id", "text", "label"}


def load_tickets(path: Path) -> list[Ticket]:
    tickets: list[Ticket] = []

    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Riga {line_number}: JSON non valido") from error

            if not isinstance(value, dict):
                raise TypeError(f"Riga {line_number}: il record deve essere un oggetto")

            missing = REQUIRED_FIELDS - value.keys()
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(f"Riga {line_number}: campi mancanti: {names}")

            if not all(isinstance(value[field], str) for field in REQUIRED_FIELDS):
                raise ValueError(f"Riga {line_number}: id, text e label devono essere stringhe")

            tickets.append({field: value[field] for field in REQUIRED_FIELDS})

    return tickets


def count_labels(tickets: list[Ticket]) -> Counter[str]:
    return Counter(ticket["label"] for ticket in tickets)


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python -m ai_mastery.setup_basics PERCORSO_JSONL")
        return 2

    try:
        tickets = load_tickets(Path(sys.argv[1]))
    except (OSError, TypeError, ValueError) as error:
        print(f"Errore: {error}", file=sys.stderr)
        return 1

    print(f"Record validi: {len(tickets)}")
    print("Conteggi per label:")
    for label, count in sorted(count_labels(tickets).items()):
        print(f"- {label}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
