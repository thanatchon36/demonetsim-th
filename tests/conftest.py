"""The model lives in model/ as standalone scripts (the arXiv bundle ships demonet_sim_th.py on its own),
so the tests import it from there rather than from an installed package."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))


@pytest.fixture
def root() -> Path:
    return ROOT
