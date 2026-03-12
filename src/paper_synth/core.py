"""paper-synth core logic.

Pure-Python, offline-first synthesis engine.  No LLM calls -- every
function is deterministic and runs in milliseconds on typical inputs.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from paper_synth.schemas import Abstract, SynthesisReport, SynthesisSection
from paper_synth.utils import load_abstract

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_abstracts(dir_path: Path) -> list[Abstract]:
    """Load every ``*.json`` file in *dir_path* as an :class:`Abstract`.

    Files are sorted by name so results are deterministic.
    Returns an empty list when the directory is empty or missing.
    """
    if not dir_path.is_dir():
        return []
    paths = sorted(dir_path.glob("*.json"))
    return [load_abstract(p) for p in paths]


# ---------------------------------------------------------------------------
# Topic extraction
# ---------------------------------------------------------------------------

# Minimum number of abstracts that must share a topic for it to appear in the
# grouped output.
_MIN_TOPIC_FREQUENCY = 2


def extract_topics(abstracts: list[Abstract]) -> dict[str, list[str]]:
    """Group abstract IDs by shared topic keywords.

    Only topics that appear in at least ``_MIN_TOPIC_FREQUENCY`` abstracts are
    returned so that singletons do not clutter the output.
    """
    topic_map: dict[str, list[str]] = {}
    for ab in abstracts:
        for topic in ab.topics:
            normed = topic.strip().lower()
            topic_map.setdefault(normed, []).append(ab.id)

    # Keep only topics shared by enough abstracts.
    return {t: ids for t, ids in topic_map.items() if len(ids) >= _MIN_TOPIC_FREQUENCY}


# ---------------------------------------------------------------------------
# Consensus detection
# ---------------------------------------------------------------------------

# A term is considered "consensus" when it appears in more than this fraction
# of abstracts.
_CONSENSUS_THRESHOLD = 0.50


def _tokenize(text: str) -> list[str]:
    """Lowercase word tokenisation (letters, digits, hyphens kept)."""
    return re.findall(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", text.lower())


def find_consensus(abstracts: list[Abstract]) -> list[str]:
    """Find terms/topics that appear in >50 % of abstracts.

    We combine each abstract's *topics* list with unigrams from its *text*,
    then count how many distinct abstracts mention each term.  Terms that
    cross the ``_CONSENSUS_THRESHOLD`` are returned, sorted by frequency
    (descending).
    """
    if not abstracts:
        return []

    n = len(abstracts)
    term_doc_freq: Counter[str] = Counter()
    # Short stop-list so that common English words do not dominate.
    stop = _stopwords()

    for ab in abstracts:
        terms: set[str] = set()
        for topic in ab.topics:
            terms.add(topic.strip().lower())
        for token in _tokenize(ab.text):
            if len(token) > 2 and token not in stop:  # noqa: PLR2004
                terms.add(token)
        for t in terms:
            term_doc_freq[t] += 1

    threshold = n * _CONSENSUS_THRESHOLD
    consensus = [term for term, count in term_doc_freq.most_common() if count > threshold]
    return consensus


# ---------------------------------------------------------------------------
# Disagreement detection
# ---------------------------------------------------------------------------

_CONTRAST_MARKERS = [
    "however",
    "in contrast",
    "unlike",
    "conflicting",
    "contradicts",
    "on the other hand",
    "conversely",
    "disputed",
    "controversy",
    "inconsistent",
    "debate",
]


def find_disagreements(abstracts: list[Abstract]) -> list[str]:
    """Find abstracts containing contrastive / disagreement language.

    Returns one short summary string per abstract that contains at least
    one marker phrase, quoting the marker and the abstract title.
    """
    results: list[str] = []
    for ab in abstracts:
        lower = ab.text.lower()
        matched = [m for m in _CONTRAST_MARKERS if m in lower]
        if matched:
            markers_str = ", ".join(matched)
            results.append(f'"{ab.title}" contains contrasting language ({markers_str})')
    return results


# ---------------------------------------------------------------------------
# Gap identification
# ---------------------------------------------------------------------------

_GAP_PHRASES = [
    "future work",
    "remains unclear",
    "not yet",
    "needs investigation",
    "poorly understood",
    "further research",
    "further studies",
    "remains to be",
    "unknown whether",
    "limited understanding",
    "warrants further",
]


def identify_gaps(abstracts: list[Abstract]) -> list[str]:
    """Find knowledge gaps signaled by hedging / future-work language.

    Returns one entry per matched phrase-abstract pair so that the gap list
    is granular enough for downstream experiment suggestion.
    """
    gaps: list[str] = []
    for ab in abstracts:
        lower = ab.text.lower()
        for phrase in _GAP_PHRASES:
            if phrase in lower:
                gaps.append(f'Gap in "{ab.title}": text mentions "{phrase}"')
    return gaps


# ---------------------------------------------------------------------------
# Experiment suggestion (template-based)
# ---------------------------------------------------------------------------

_EXPERIMENT_TEMPLATES = [
    "Design a controlled study to address: {gap}",
    "Conduct a systematic review focusing on: {gap}",
    "Develop an in-vitro assay to test: {gap}",
    "Perform longitudinal cohort analysis for: {gap}",
]


def suggest_experiments(gaps: list[str]) -> list[str]:
    """Generate template-based experiment suggestions from gap strings.

    Each gap produces one suggestion, cycling through templates so that
    the output is varied.
    """
    if not gaps:
        return []
    suggestions: list[str] = []
    for i, gap in enumerate(gaps):
        tmpl = _EXPERIMENT_TEMPLATES[i % len(_EXPERIMENT_TEMPLATES)]
        suggestions.append(tmpl.format(gap=gap))
    return suggestions


# ---------------------------------------------------------------------------
# Synthesis orchestration
# ---------------------------------------------------------------------------


def synthesize(abstracts: list[Abstract]) -> SynthesisReport:
    """Orchestrate all analysis steps into a single :class:`SynthesisReport`."""
    if not abstracts:
        return SynthesisReport(title="Empty Synthesis", abstract_count=0)

    topics = extract_topics(abstracts)
    consensus = find_consensus(abstracts)
    disagreements = find_disagreements(abstracts)
    gaps = identify_gaps(abstracts)
    experiments = suggest_experiments(gaps)

    # Build per-topic sections.
    sections: list[SynthesisSection] = []
    for topic, ab_ids in sorted(topics.items()):
        relevant = [a for a in abstracts if a.id in ab_ids]
        titles = [a.title for a in relevant]
        content = f"Topic '{topic}' appears in {len(ab_ids)} abstracts: " + "; ".join(titles) + "."
        sections.append(
            SynthesisSection(
                heading=topic.title(),
                content=content,
                supporting_abstracts=ab_ids,
            )
        )

    return SynthesisReport(
        title="Literature Synthesis Report",
        sections=sections,
        abstract_count=len(abstracts),
        consensus_points=consensus,
        disagreements=disagreements,
        gaps=gaps,
        suggested_experiments=experiments,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def format_markdown(report: SynthesisReport) -> str:
    """Render a :class:`SynthesisReport` as a Markdown string."""
    lines: list[str] = []
    lines.append(f"# {report.title}")
    lines.append("")
    lines.append(f"**Abstracts analysed:** {report.abstract_count}")
    lines.append("")

    # Sections
    if report.sections:
        lines.append("## Topic Sections")
        lines.append("")
        for sec in report.sections:
            lines.append(f"### {sec.heading}")
            lines.append("")
            lines.append(sec.content)
            lines.append("")
            if sec.supporting_abstracts:
                refs = ", ".join(sec.supporting_abstracts)
                lines.append(f"*Supporting abstracts:* {refs}")
                lines.append("")

    # Consensus
    if report.consensus_points:
        lines.append("## Consensus Points")
        lines.append("")
        for pt in report.consensus_points:
            lines.append(f"- {pt}")
        lines.append("")

    # Disagreements
    if report.disagreements:
        lines.append("## Disagreements")
        lines.append("")
        for d in report.disagreements:
            lines.append(f"- {d}")
        lines.append("")

    # Gaps
    if report.gaps:
        lines.append("## Knowledge Gaps")
        lines.append("")
        for g in report.gaps:
            lines.append(f"- {g}")
        lines.append("")

    # Experiments
    if report.suggested_experiments:
        lines.append("## Suggested Experiments")
        lines.append("")
        for e in report.suggested_experiments:
            lines.append(f"- {e}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stopwords() -> set[str]:
    """Minimal English stop-word set -- just enough to keep consensus clean."""
    return {
        "the",
        "and",
        "for",
        "are",
        "but",
        "not",
        "you",
        "all",
        "can",
        "had",
        "her",
        "was",
        "one",
        "our",
        "out",
        "has",
        "have",
        "been",
        "were",
        "they",
        "their",
        "will",
        "when",
        "who",
        "with",
        "this",
        "that",
        "from",
        "been",
        "also",
        "than",
        "its",
        "into",
        "may",
        "which",
        "these",
        "such",
        "more",
        "other",
        "both",
        "each",
        "between",
        "through",
        "after",
        "those",
        "most",
        "well",
        "while",
        "where",
        "over",
        "some",
        "only",
    }
