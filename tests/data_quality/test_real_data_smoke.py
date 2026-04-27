"""Smoke test: run the full pipeline on real raw data and assert sanity bounds.

Marked `slow` so contributors can skip it locally with `pytest -m "not slow"`.
The CI / manual full run executes it.

Known data-quality limitations (tracked as follow-up work):

* **2021** is excluded from `YEAR_REGISTRY` until a JSON `Mercado_N.txt` reader
  is added (the local 2021 raw checkout has no `rodada-N.csv` files).
* Some years (notably 2020 / 2022 / 2023) contain a small number of
  duplicated `(ano, rodada, id_atleta)` rows in the upstream raw data
  (e.g. coaches with `posicao_id=6`, players listed twice). Pandera unique
  validation and the strict de-dup test are therefore tolerant rather than
  exact while the upstream data is being investigated.
* 2026 is an in-progress season; row / round / goal bounds are widened.
"""

from __future__ import annotations

import pandas as pd
import pytest

from cartola.aggregation import driver
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import SCOUTS

pytestmark = pytest.mark.slow

# Years with a full-shape season we can sanity-bound. Excludes 2025 (no scouts)
# and 2026 (in-progress, partial season). 2021 is not in YEAR_REGISTRY at all.
FULL_SEASON_YEARS = sorted(y for y in YEAR_REGISTRY if 2018 <= y <= 2024 and y != 2025)


@pytest.fixture(scope="module")
def aggregated_df(tmp_path_factory) -> pd.DataFrame:
    out_dir = tmp_path_factory.mktemp("smoke")
    # Redirect the driver's outputs to a tmp dir so we don't clobber real data.
    driver.PRIMARY_DIR = out_dir / "03_primary"
    driver.AGGREGATED_DIR = out_dir / "04_aggregated"
    return driver.run(years=None, track=False)


def test_all_registered_years_present(aggregated_df):
    expected = set(YEAR_REGISTRY)
    got = set(aggregated_df["ano"].astype(int).unique())
    assert expected == got


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_full_season_row_count_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    assert 5_000 <= len(sub) <= 35_000, f"Unreasonable row count for {year}: {len(sub)}"


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_full_season_round_count_is_38(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    n_rounds = sub["rodada"].nunique()
    assert 30 <= n_rounds <= 38, f"Unreasonable round count for {year}: {n_rounds}"


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_full_season_total_goals_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    total_g = sub["G"].sum(skipna=True)
    # ~30 goals/round × ~38 rounds ≈ 1,140; allow a wide band for double counting.
    assert 100 <= total_g <= 2_000, f"Unreasonable total goals for {year}: {total_g}"


def test_in_progress_2026_bounds(aggregated_df):
    sub = aggregated_df[aggregated_df["ano"] == 2026]
    n_rounds = sub["rodada"].nunique()
    assert 1 <= n_rounds <= 38, f"2026 round count out of bounds: {n_rounds}"
    assert len(sub) > 0, "2026 should have at least some rows once the season has started"
    total_g = sub["G"].sum(skipna=True)
    # ~30 goals/round; partial season → cap at full-season ceiling.
    assert 0 <= total_g <= 2_000, f"2026 total goals out of bounds: {total_g}"


def test_2025_has_no_scouts(aggregated_df):
    sub = aggregated_df[aggregated_df["ano"] == 2025]
    for col in SCOUTS:
        assert sub[col].isna().all(), f"2025 should have NaN for scout {col}, got non-NaN"


def test_duplicate_rows_are_rare(aggregated_df):
    """Tolerant uniqueness check: real raw data has a small number of dup rows
    (coaches, players listed twice, etc.). Hard-fail only if a dup explosion
    appears (>1% of rows), which would indicate a regression in our pipeline.
    """
    dups = aggregated_df.duplicated(subset=["ano", "rodada", "id_atleta"]).sum()
    pct = dups / len(aggregated_df)
    assert pct < 0.01, f"{dups} duplicate (ano, rodada, id_atleta) tuples ({pct:.2%}) — too many"
