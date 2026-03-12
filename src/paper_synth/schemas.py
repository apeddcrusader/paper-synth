"""paper-synth data schemas."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Abstract:
    """A single research abstract with metadata."""

    id: str
    title: str
    text: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    topics: list[str] = field(default_factory=list)


@dataclass
class SynthesisSection:
    """One section of a synthesis report."""

    heading: str
    content: str
    supporting_abstracts: list[str] = field(default_factory=list)


@dataclass
class SynthesisReport:
    """Full synthesis report aggregating findings across abstracts."""

    title: str
    sections: list[SynthesisSection] = field(default_factory=list)
    abstract_count: int = 0
    consensus_points: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    suggested_experiments: list[str] = field(default_factory=list)
