"""paper-synth utilities."""

from __future__ import annotations

import json
from pathlib import Path

from paper_synth.schemas import Abstract


def load_abstract(path: Path) -> Abstract:
    """Load a single abstract from a JSON file.

    Expected JSON keys: id, title, text, authors, year, topics.
    Missing optional keys get defaults (empty list / None).
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    return Abstract(
        id=data["id"],
        title=data["title"],
        text=data["text"],
        authors=data.get("authors", []),
        year=data.get("year"),
        topics=data.get("topics", []),
    )


def write_output(content: str, path: Path) -> None:
    """Write string content to *path*, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
