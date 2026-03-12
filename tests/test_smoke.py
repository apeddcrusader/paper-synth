"""Smoke tests for paper_synth."""

from __future__ import annotations

from pathlib import Path

from paper_synth.core import format_markdown, load_abstracts, synthesize


def test_import():
    import paper_synth

    assert hasattr(paper_synth, "__version__")


def test_full_pipeline(demo_abstracts_dir: Path):
    """End-to-end: load -> synthesize -> format."""
    abstracts = load_abstracts(demo_abstracts_dir)
    assert len(abstracts) == 8

    report = synthesize(abstracts)
    assert report.abstract_count == 8
    assert len(report.sections) > 0

    md = format_markdown(report)
    assert isinstance(md, str)
    assert len(md) > 100
    assert "Literature Synthesis Report" in md
