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


@pytest.fixture(scope="session")
def aggregated_df(tmp_path_factory) -> pd.DataFrame:
    """Runs the full pipeline against real raw data exactly once per test
    session, so every ``slow`` data-quality test that needs the real
    aggregated DataFrame shares a single ~10s pipeline run instead of
    re-running it per test module.

    Redirects the driver's outputs to a tmp dir so a full test run never
    clobbers the real ``data/03_primary`` / ``data/04_aggregated`` on disk.
    """
    from cartola.aggregation import driver

    out_dir = tmp_path_factory.mktemp("smoke")
    driver.PRIMARY_DIR = out_dir / "03_primary"
    driver.AGGREGATED_DIR = out_dir / "04_aggregated"
    return driver.run(years=None)
