"""Smoke test: run the full pipeline on real raw data and assert sanity bounds.

Marked `slow` so contributors can skip it locally with `pytest -m "not slow"`.
The CI / manual full run executes it.

Known data-quality limitations (tracked as follow-up work):

* 2014 is missing `id_clube` for ~half the rows because the legacy raw scout
  files have empty `ClubeID`. Tolerated by per-year `id_clube` checks.
* 2026 is an in-progress season; row / round / goal bounds are widened.

Bounds below are calibrated tightly against the real 2018-2025 corpus
(row counts 28,499-30,955; total goals 759-931/season) with modest headroom,
not against a generic a-priori estimate — the goal is for a real regression
(e.g. a merge that silently drops or duplicates a chunk of rows) to actually
fail these tests instead of sliding through a band wide enough to hide it.
"""

import pytest

from cartola.aggregation.catalog import YEAR_REGISTRY

pytestmark = pytest.mark.slow

# Years with a full-shape season we can sanity-bound. Excludes 2026
# (in-progress, partial season).
FULL_SEASON_YEARS = sorted(y for y in YEAR_REGISTRY if 2018 <= y <= 2025)


def test_all_registered_years_present(aggregated_df):
    expected = set(YEAR_REGISTRY)
    got = set(aggregated_df["ano"].astype(int).unique())
    assert expected == got


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_full_season_row_count_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    # Real 2018-2025 range is 28,499-30,955 rows; ~10% headroom on each side.
    assert 25_000 <= len(sub) <= 33_000, f"Unreasonable row count for {year}: {len(sub)}"


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_full_season_round_count_is_38(aggregated_df, year):
    """Every year in FULL_SEASON_YEARS is a genuine 38-round Brasileirão with
    no known gaps (unlike e.g. 2015, which is missing rounds 26 and 38 —
    see test_round_continuity.py). A wide `30 <= n <= 38` band would let a
    pipeline regression that drops a fifth of the season through silently."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    n_rounds = sub["rodada"].nunique()
    assert n_rounds == 38, f"Expected exactly 38 rounds for {year}, got {n_rounds}"


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_full_season_total_goals_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    total_g = sub["G"].sum(skipna=True)
    # Real 2018-2025 range is 759-931; headroom stops well short of the 2x
    # a duplicate-counting bug would produce (~1,500-1,900).
    assert 650 <= total_g <= 1_100, f"Unreasonable total goals for {year}: {total_g}"


def test_in_progress_2026_bounds(aggregated_df):
    sub = aggregated_df[aggregated_df["ano"] == 2026]
    n_rounds = sub["rodada"].nunique()
    assert 1 <= n_rounds <= 38, f"2026 round count out of bounds: {n_rounds}"
    assert len(sub) > 0, "2026 should have at least some rows once the season has started"

    # Scale the full-season bounds (see test_full_season_row_count_in_bounds
    # / test_full_season_total_goals_in_bounds) down to the rounds played so
    # far, instead of just capping at the full-season ceiling — a pipeline
    # bug that zeroed out `G` entirely (0 goals with 18 rounds played) would
    # otherwise still pass `0 <= total_g <= 2_000`.
    rows_per_round = len(sub) / n_rounds
    assert 600 <= rows_per_round <= 900, f"2026 rows/round out of bounds: {rows_per_round:.1f}"

    total_g = sub["G"].sum(skipna=True)
    goals_per_round = total_g / n_rounds
    assert 15 <= goals_per_round <= 32, f"2026 goals/round out of bounds: {goals_per_round:.1f}"


def test_no_duplicate_player_round_rows(aggregated_df):
    """Strict uniqueness: ``read_round_files`` derives `rodada` from the file
    name and ``player.dedupe_per_rodada`` collapses any within-file dups, so
    every (ano, rodada, id_atleta) tuple must appear exactly once."""
    dups = aggregated_df.duplicated(subset=["ano", "rodada", "id_atleta"]).sum()
    assert dups == 0, f"{dups} duplicate (ano, rodada, id_atleta) tuples found"


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_no_preseason_round_zero_rows(aggregated_df, year):
    """Regression for the 2014-2017 `Rodada=0` leak (see
    ``readers.read_season_files``/``read_monolithic``): every reader must
    drop the preseason placeholder snapshot, not just ``read_round_files``
    and ``read_mercado_json``."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    assert not (sub["rodada"] == 0).any(), f"{year}: preseason rodada=0 rows leaked into output"


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_unique_rodada_id_atleta_per_year(aggregated_df, year):
    """Same invariant as `test_no_duplicate_player_round_rows`, but checked
    per year: pinpoints which year's reader/dedupe logic regressed instead
    of only detecting *some* duplicate exists somewhere in 13 years of data."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    dups = sub.duplicated(subset=["rodada", "id_atleta"]).sum()
    assert dups == 0, f"{year}: {dups} duplicate (rodada, id_atleta) tuples found"
