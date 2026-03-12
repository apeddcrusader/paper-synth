"""Tests for paper_synth.core."""

from __future__ import annotations

from pathlib import Path

from paper_synth.core import (
    extract_topics,
    find_consensus,
    find_disagreements,
    format_markdown,
    identify_gaps,
    load_abstracts,
    suggest_experiments,
    synthesize,
)
from paper_synth.schemas import Abstract, SynthesisReport

# ---- fixtures local to core tests ----


def _make_abstracts() -> list[Abstract]:
    """Build a small in-memory set of abstracts for unit tests."""
    return [
        Abstract(
            id="t1",
            title="Alpha Study",
            text=(
                "Cytokines drive inflammation in the tumor microenvironment. "
                "Further research is needed on IL-6 signaling pathways."
            ),
            authors=["A"],
            year=2024,
            topics=["cytokines", "inflammation", "tumor microenvironment"],
        ),
        Abstract(
            id="t2",
            title="Beta Study",
            text=(
                "Inflammation is linked to drug resistance. However, the "
                "causal mechanism remains unclear. Immune response plays a "
                "critical role."
            ),
            authors=["B"],
            year=2024,
            topics=["inflammation", "drug resistance", "immune response"],
        ),
        Abstract(
            id="t3",
            title="Gamma Study",
            text=(
                "Immune response in the tumor microenvironment is modulated "
                "by cytokines. In contrast to earlier models, we find that "
                "metabolic factors dominate. Future work should address "
                "combination therapies."
            ),
            authors=["C"],
            year=2023,
            topics=[
                "immune response",
                "tumor microenvironment",
                "cytokines",
            ],
        ),
    ]


# ---- load_abstracts ----


def test_load_abstracts(demo_abstracts_dir: Path):
    abstracts = load_abstracts(demo_abstracts_dir)
    assert len(abstracts) == 8
    assert all(a.id.startswith("abs-") for a in abstracts)


def test_load_abstracts_missing_dir(tmp_path: Path):
    result = load_abstracts(tmp_path / "nonexistent")
    assert result == []


# ---- extract_topics ----


def test_extract_topics():
    abstracts = _make_abstracts()
    topics = extract_topics(abstracts)
    # 'inflammation' appears in t1 and t2 topics -- should be present
    assert "inflammation" in topics
    assert len(topics["inflammation"]) == 2
    # 'drug resistance' appears in only t2 -- below threshold of 2
    assert "drug resistance" not in topics


# ---- find_consensus ----


def test_find_consensus_nonempty():
    abstracts = _make_abstracts()
    consensus = find_consensus(abstracts)
    # 'inflammation' is a topic in all 3 -- should be consensus
    assert "inflammation" in consensus
    assert isinstance(consensus, list)
    assert len(consensus) > 0


def test_find_consensus_empty():
    assert find_consensus([]) == []


# ---- find_disagreements ----


def test_find_disagreements():
    abstracts = _make_abstracts()
    disagreements = find_disagreements(abstracts)
    # t2 contains "however", t3 contains "in contrast"
    assert len(disagreements) >= 2
    assert any("Beta Study" in d for d in disagreements)
    assert any("Gamma Study" in d for d in disagreements)


# ---- identify_gaps ----


def test_identify_gaps():
    abstracts = _make_abstracts()
    gaps = identify_gaps(abstracts)
    # t1 mentions "further research", t2 "remains unclear", t3 "future work"
    assert len(gaps) >= 3
    assert any("further research" in g for g in gaps)
    assert any("remains unclear" in g for g in gaps)
    assert any("future work" in g for g in gaps)


# ---- suggest_experiments ----


def test_suggest_experiments():
    gaps = ["gap A", "gap B"]
    suggestions = suggest_experiments(gaps)
    assert len(suggestions) == 2
    assert all(isinstance(s, str) and len(s) > 0 for s in suggestions)


def test_suggest_experiments_empty():
    assert suggest_experiments([]) == []


# ---- synthesize ----


def test_synthesize_report_structure(demo_abstracts_dir: Path):
    abstracts = load_abstracts(demo_abstracts_dir)
    report = synthesize(abstracts)

    assert isinstance(report, SynthesisReport)
    assert report.abstract_count == 8
    assert len(report.sections) > 0
    assert len(report.consensus_points) > 0
    assert len(report.disagreements) > 0
    assert len(report.gaps) > 0
    assert len(report.suggested_experiments) > 0


def test_synthesize_empty():
    report = synthesize([])
    assert report.abstract_count == 0
    assert report.sections == []


# ---- format_markdown ----


def test_format_markdown():
    abstracts = _make_abstracts()
    report = synthesize(abstracts)
    md = format_markdown(report)

    assert md.startswith("# ")
    assert "## Topic Sections" in md
    assert "## Consensus Points" in md
    assert "## Disagreements" in md
    assert "## Knowledge Gaps" in md
    assert "## Suggested Experiments" in md


def test_format_markdown_empty():
    report = synthesize([])
    md = format_markdown(report)
    assert "Empty Synthesis" in md
    assert "**Abstracts analysed:** 0" in md


# ---- empty input handling ----


def test_empty_input_handling():
    """All analysis functions gracefully handle empty input."""
    assert extract_topics([]) == {}
    assert find_consensus([]) == []
    assert find_disagreements([]) == []
    assert identify_gaps([]) == []
    assert suggest_experiments([]) == []
    report = synthesize([])
    assert report.abstract_count == 0
