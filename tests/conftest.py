from __future__ import annotations

from pathlib import Path

import pytest

DEMO_DATA = Path(__file__).parent.parent / "demo_data"
DEMO_ABSTRACTS = DEMO_DATA / "abstracts"
DEMO_OUTPUT = Path(__file__).parent.parent / "demo_output"


@pytest.fixture
def demo_data_dir():
    return DEMO_DATA


@pytest.fixture
def demo_abstracts_dir():
    return DEMO_ABSTRACTS


@pytest.fixture
def demo_output_dir():
    return DEMO_OUTPUT
