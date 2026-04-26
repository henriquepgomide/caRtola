"""Fixtures for data-expectation tests."""

from pathlib import Path

import pandas as pd
import pytest

PRIMARY_DIR = Path("data/03_primary")
AGGREGATED_PATH = Path("data/04_feature/aggregated.csv")


@pytest.fixture(scope="session")
def data_aggregated() -> pd.DataFrame:
    """Load the aggregated CSV; skip if missing."""
    if not AGGREGATED_PATH.exists():
        pytest.skip(f"{AGGREGATED_PATH} not found; run `uv run kedro run` first")
    return pd.read_csv(AGGREGATED_PATH, low_memory=False)


@pytest.fixture(scope="session")
def data_per_year(request) -> tuple[int, pd.DataFrame]:
    """Load data/03_primary/preprocessed_{year}.csv; skip if missing.

    Returns (year, dataframe) so tests can reference the year without
    digging into pytest's request internals.
    """
    year = int(request.param)
    path = PRIMARY_DIR / f"preprocessed_{year}.csv"
    if not path.exists():
        pytest.skip(f"{path} not found; run `uv run kedro run --pipeline={year}` first")
    return year, pd.read_csv(path, low_memory=False)
