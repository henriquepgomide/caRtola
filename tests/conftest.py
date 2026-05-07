"""Shared pytest fixtures for the Cartola aggregation pipeline tests."""

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the synthetic test-fixture CSVs."""
    return FIXTURES_DIR


@pytest.fixture
def repo_root() -> Path:
    """Path to the repo root, useful for the real-data smoke test."""
    return REPO_ROOT


@pytest.fixture
def empty_player_df() -> pd.DataFrame:
    """An empty DataFrame with the canonical column set, useful for edge-case tests."""
    from cartola.aggregation.schema import CANONICAL_COLUMNS

    return pd.DataFrame(columns=CANONICAL_COLUMNS)
