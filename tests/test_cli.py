"""Tests for paper_synth.cli."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "paper_synth", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "paper-synth" in result.stdout.lower() or "paper_synth" in result.stdout.lower()


def test_cli_synthesize_demo(demo_abstracts_dir: Path, tmp_path: Path):
    out_file = tmp_path / "report.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_synth",
            "synthesize",
            "--input-dir",
            str(demo_abstracts_dir),
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "# Literature Synthesis Report" in content
    assert "## Consensus Points" in content


def test_cli_synthesize_json(demo_abstracts_dir: Path, tmp_path: Path):
    out_file = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_synth",
            "synthesize",
            "--input-dir",
            str(demo_abstracts_dir),
            "--output",
            str(out_file),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["abstract_count"] == 8
    assert isinstance(data["consensus_points"], list)


def test_cli_synthesize_stdout(demo_abstracts_dir: Path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_synth",
            "synthesize",
            "--input-dir",
            str(demo_abstracts_dir),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "# Literature Synthesis Report" in result.stdout


def test_cli_synthesize_missing_dir(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_synth",
            "synthesize",
            "--input-dir",
            str(tmp_path / "nope"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
