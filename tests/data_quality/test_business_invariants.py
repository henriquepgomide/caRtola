"""Business-invariant checks against the real aggregated data.

Marked `slow` because it depends on the real, fully-aggregated pipeline
output (see the session-scoped `aggregated_df` fixture in `tests/conftest.py`).
"""

import pytest

from cartola.aggregation import columns, player, scouts
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import POSITION_MAP, SCOUTS, STATUS_MAP

pytestmark = pytest.mark.slow

FULL_SEASON_YEARS = sorted(y for y in YEAR_REGISTRY if 2018 <= y <= 2025)
"""Years with a full 38-round Brasileirão season we can sanity-bound.
Mirrors the set used in `test_real_data_smoke.py`."""

ACCUMULATED_YEARS = sorted(y for y, cfg in YEAR_REGISTRY.items() if cfg.accumulated)


SEASON_SCOUT_CEILINGS: dict[str, float] = {
    "A": 25,
    "CV": 8,
    "DE": 200,
    "DP": 10,
    "DS": 170,
    "FC": 160,
    "FD": 55,
    "FF": 70,
    "FS": 200,
    "FT": 15,
    "GC": 6,
    "GS": 80,
    "I": 55,
    "PC": 10,
    "PI": 550,
    "PP": 10,
    "PS": 10,
    "SG": 30,
    "V": 35,
}
"""Plausible per-season ceiling for each scout, calibrated from the real
2014-2026 corpus (season totals per ``(ano, id_atleta)``) with ~30-40%
headroom above the observed historical maximum. ``G``/``CA`` are
intentionally excluded: the real corpus's season-max for ``G`` (35,
ano=2020) comes from the same documented upstream data glitch as
``KNOWN_SCOUT_ANOMALIES`` in ``test_scout_and_club_consistency.py``
(``ano=2020, rodada=10, id_atleta=69345``), mirroring the ``G``/``CA``
exclusion already in
:class:`~cartola.aggregation.schema.AggregatedSchema`.
"""


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_season_scout_totals_within_plausible_ceiling(aggregated_df, year):
    """A season total far above the real historical max usually signals a
    duplication bug (e.g. a row double-counted across a merge) rather than
    a genuinely prolific player — individual per-round values can each be
    within ``SCOUT_ROUND_CEILINGS`` while their sum across 38 rounds is not."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    cols = [c for c in SEASON_SCOUT_CEILINGS if c in sub.columns]
    season_totals = sub.groupby("id_atleta")[cols].sum(min_count=1)
    violations = {}
    for col in cols:
        ceiling = SEASON_SCOUT_CEILINGS[col]
        exceeding = season_totals[col] > ceiling
        if exceeding.any():
            violations[col] = float(season_totals.loc[exceeding, col].max())
    assert not violations, f"{year}: season scout totals above plausibility ceiling: {violations}"


KNOWN_NUM_JOGOS_REGRESSIONS: set[tuple[int, int]] = {
    (2017, 70222),
    (2022, 99815),
    (2022, 104276),
}
"""Documented, investigated exceptions where ``num_jogos`` genuinely
decreases at some point within a single season for a given player — a
real quirk already present in the raw corpus, not a pipeline bug. Anything
NOT in this set that violates monotonicity is treated as a regression."""


def test_num_jogos_non_decreasing_within_season(aggregated_df):
    """``num_jogos`` is a running count of games played in the season; it
    must never decrease from one round to the next for the same player."""
    sub = aggregated_df.dropna(subset=["num_jogos"]).sort_values(["ano", "id_atleta", "rodada"])
    is_monotonic = sub.groupby(["ano", "id_atleta"])["num_jogos"].apply(lambda s: s.is_monotonic_increasing)
    violations = {key for key, ok in is_monotonic.items() if not ok} - KNOWN_NUM_JOGOS_REGRESSIONS
    assert not violations, f"num_jogos decreased within season for (ano, id_atleta): {violations}"


def test_known_num_jogos_regressions_are_still_accurate(aggregated_df):
    """Guards ``KNOWN_NUM_JOGOS_REGRESSIONS`` itself: if a documented dip is
    no longer present (e.g. a raw data correction), a human should notice
    and prune the now-stale entry rather than the monotonicity test just
    staying green for the wrong reason."""
    sub = aggregated_df.dropna(subset=["num_jogos"]).sort_values(["ano", "id_atleta", "rodada"])
    for ano, id_atleta in KNOWN_NUM_JOGOS_REGRESSIONS:
        s = sub[(sub["ano"] == ano) & (sub["id_atleta"] == id_atleta)]["num_jogos"]
        assert not s.is_monotonic_increasing, (
            f"({ano}, {id_atleta}): num_jogos is monotonic again — "
            "remove the now-stale entry from KNOWN_NUM_JOGOS_REGRESSIONS"
        )


def test_status_only_known_labels(aggregated_df):
    """Non-null ``status`` must always be one of ``STATUS_MAP``'s labels —
    2014-2016 legitimately have no status data at all (see
    `player.map_status`), so NaN is expected and not checked here; this
    only guards against an unrecognized raw id/label silently slipping
    through instead of mapping to a known status or NaN."""
    known = set(STATUS_MAP.values())
    unexpected = set(aggregated_df["status"].dropna().unique()) - known
    assert not unexpected, f"status has unexpected labels: {unexpected}"


def test_posicao_only_known_labels(aggregated_df):
    """Same guard as `test_status_only_known_labels`, for ``posicao``."""
    known = set(POSITION_MAP.values())
    unexpected = set(aggregated_df["posicao"].dropna().unique()) - known
    assert not unexpected, f"posicao has unexpected labels: {unexpected}"


@pytest.mark.parametrize("year", FULL_SEASON_YEARS)
def test_rows_per_round_within_plausible_band(aggregated_df, year):
    """Complements the club-count checks below: a club could still show up
    with only a handful of players in a round (partial scrape) without
    tripping `test_at_least_nineteen_clubs_present_per_round`. Real
    2018-2025 rows/round range is 619-870; headroom stops well short of a
    duplication or truncation bug halving/doubling a round's rows."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    rows_per_round = sub.groupby("rodada").size()
    out_of_band = rows_per_round[(rows_per_round < 550) | (rows_per_round > 950)]
    assert out_of_band.empty, f"{year}: rounds with implausible row counts: {out_of_band.to_dict()}"


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_at_most_twenty_distinct_clubs_per_year(aggregated_df, year):
    """Complements `test_at_least_nineteen_clubs_present_per_round`: the
    Brasileirão Série A has run with exactly 20 clubs in every season in
    this corpus (2014 included) — promotion/relegation only happens
    between seasons, never mid-season."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    distinct_clubs = sub["id_clube"].nunique()
    assert distinct_clubs <= 20, f"{year}: {distinct_clubs} distinct id_clube values (expected <= 20)"


VARIACAO_TOLERANCE = 0.3
"""Absolute tolerance (Cartola price units) for a single round's
``variacao`` vs the actual ``preco`` delta from the previous round."""

VARIACAO_MISMATCH_BUDGET_PCT: dict[int, float] = {
    2015: 1.0,
    2022: 1.5,
    2025: 1.5,
}
"""Per-year budget for the percentage of consecutive-round rows allowed to
exceed ``VARIACAO_TOLERANCE``. Calibrated from the real corpus: most years
have 0% mismatch, but 2015/2022/2025 have a small, real amount of noise
(0.70%/1.04%/0.98% respectively) not otherwise explained. Any year not
listed here falls back to ``_DEFAULT_VARIACAO_MISMATCH_BUDGET_PCT``."""

_DEFAULT_VARIACAO_MISMATCH_BUDGET_PCT = 0.1


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_variacao_matches_consecutive_preco_delta(aggregated_df, year):
    """``variacao`` is defined as the round-over-round change in ``preco``.
    Only consecutive rounds are compared for a given player — a gap in
    appearances legitimately breaks a naive diff, since ``variacao`` only
    ever reflects the most recent round's change, not the change since the
    player's last appearance."""
    sub = aggregated_df[aggregated_df["ano"] == year].dropna(subset=["preco", "variacao"])
    sub = sub.sort_values(["id_atleta", "rodada"])
    if sub.empty:
        pytest.skip(f"{year}: no rows with both preco and variacao populated")

    preco_diff = sub.groupby("id_atleta")["preco"].diff()
    rodada_diff = sub.groupby("id_atleta")["rodada"].diff()
    comparable = preco_diff[rodada_diff == 1]
    if comparable.empty:
        pytest.skip(f"{year}: no consecutive-round pairs to compare")

    err = (comparable - sub.loc[comparable.index, "variacao"]).abs()
    mismatch_pct = 100 * (err > VARIACAO_TOLERANCE).mean()
    budget = VARIACAO_MISMATCH_BUDGET_PCT.get(year, _DEFAULT_VARIACAO_MISMATCH_BUDGET_PCT)
    assert mismatch_pct <= budget, (
        f"{year}: {mismatch_pct:.2f}% of consecutive-round rows have variacao != preco "
        f"delta beyond tolerance {VARIACAO_TOLERANCE} (budget {budget}%)"
    )


@pytest.mark.parametrize("year", ACCUMULATED_YEARS)
def test_raw_cumulative_matches_disaccumulated_season_sum(aggregated_df, repo_root, year):
    """For ``accumulated=True`` years, the sum of
    :func:`~cartola.aggregation.scouts.disaccumulate_scouts`'s per-round
    deltas across a season telescopes exactly to the running max of the
    raw season-cumulative value (a mathematical identity of the
    running-cummax algorithm, not an approximation — see that function's
    docstring). Checked with a near-zero tolerance directly against the
    real raw files, independent of the in-memory pipeline that produced
    ``aggregated_df``, so it catches a regression anywhere between reading
    and renaming, not just inside ``disaccumulate_scouts`` itself.

    Reproduces the raw-side steps in the exact order
    :func:`~cartola.aggregation.nodes.year_dataframe` uses
    (``rename_columns`` → ``dedupe_per_rodada`` → ``harmonize_scout_names``)
    — reversing the last two changes which duplicate-round row a given
    year's dedup tie-break keeps for legacy-named columns (e.g. 2020 still
    ships the legacy ``DD`` name for one scout), which would otherwise
    produce spurious mismatches unrelated to any real pipeline bug.
    """
    cfg = YEAR_REGISTRY[year]
    raw = cfg.reader(str(repo_root / cfg.raw_dir), year)
    raw = columns.rename_columns(raw)
    raw = player.dedupe_per_rodada(raw)
    raw = scouts.harmonize_scout_names(raw)

    present = [c for c in SCOUTS if c in raw.columns]
    if not present or "id_atleta" not in raw.columns:
        pytest.skip(f"{year}: no scout columns present in the raw data")

    raw[present] = raw[present].fillna(0.0)
    raw_running_max = raw.groupby("id_atleta")[present].max()

    sub = aggregated_df[aggregated_df["ano"] == year]
    season_sum = sub.groupby("id_atleta")[present].sum(min_count=1)

    common_ids = raw_running_max.index.intersection(season_sum.index)
    diff = (raw_running_max.loc[common_ids] - season_sum.loc[common_ids]).abs()
    mismatched_mask = (diff > 1e-6).any(axis=1)
    assert not mismatched_mask.any(), (
        f"{year}: raw cumulative max != disaccumulated season sum for "
        f"{int(mismatched_mask.sum())} id_atleta (max abs diff: {diff.to_numpy().max():.4f})"
    )
