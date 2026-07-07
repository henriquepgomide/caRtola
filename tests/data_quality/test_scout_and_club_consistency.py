"""Scout plausibility and club-universe checks against the real aggregated data.

Marked `slow` because it depends on the real, fully-aggregated pipeline
output (see the session-scoped `aggregated_df` fixture in `tests/conftest.py`).
"""

import pytest

from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import SCOUT_ROUND_CEILINGS, SCOUTS
from cartola.aggregation.team import TEAM_NAME_TO_ID
from tests.data_quality.expectations import EXPECTED_ALL_NULL_SCOUTS

pytestmark = pytest.mark.slow

KNOWN_SCOUT_ANOMALIES: dict[tuple[int, int], set[str]] = {
    (2020, 10): {"G", "CA"},
}
"""Documented, investigated exceptions to `SCOUT_ROUND_CEILINGS`.

The raw ``data/01_raw/2020/rodada-10.csv`` snapshot ships genuinely
corrupted ``G``/``CA`` values for dozens of players (e.g. player 69345
goes ``G: NaN -> 35 -> NaN`` across rounds 9/10/11, confirmed against the
neighboring rounds) — a real upstream data glitch, not a pipeline bug.
The pipeline intentionally does not clip or otherwise alter this value
(see :data:`~cartola.aggregation.schema.SCOUT_ROUND_CEILINGS`'s
docstring), so it is excluded here explicitly rather than widening the
ceiling itself and losing the ability to catch a *real* future anomaly
for these same columns.
"""


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_scout_values_within_plausible_ceiling(aggregated_df, year):
    """Any value above `SCOUT_ROUND_CEILINGS` outside the documented
    `KNOWN_SCOUT_ANOMALIES` exception is treated as a regression."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    violations = {}
    for col, ceiling in SCOUT_ROUND_CEILINGS.items():
        if col not in sub.columns:
            continue
        exceeding_rounds = set(sub.loc[sub[col] > ceiling, "rodada"].unique())
        known_rounds = {r for (y, r), cols in KNOWN_SCOUT_ANOMALIES.items() if y == year and col in cols}
        undocumented_rounds = exceeding_rounds - known_rounds
        if undocumented_rounds:
            offending = sub[sub["rodada"].isin(undocumented_rounds) & (sub[col] > ceiling)]
            violations[col] = float(offending[col].max())
    assert not violations, f"{year}: scouts above plausibility ceiling (undocumented): {violations}"


def test_known_scout_anomalies_are_still_accurate(aggregated_df):
    """Guards `KNOWN_SCOUT_ANOMALIES` itself: if the documented
    (year, rodada) corruption ever gets corrected upstream (e.g. a raw
    data refresh), a human should notice and prune the now-stale entry
    rather than the ceiling test just staying green for the wrong reason."""
    for (year, rodada), cols in KNOWN_SCOUT_ANOMALIES.items():
        sub = aggregated_df[(aggregated_df["ano"] == year) & (aggregated_df["rodada"] == rodada)]
        for col in cols:
            if col not in sub.columns:
                continue
            ceiling = SCOUT_ROUND_CEILINGS[col]
            assert (sub[col] > ceiling).any(), (
                f"{year}/rodada={rodada}: {col} no longer exceeds the ceiling — "
                "remove the now-stale entry from KNOWN_SCOUT_ANOMALIES"
            )


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_only_known_scouts_are_fully_null(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    scout_cols = [c for c in SCOUTS if c in sub.columns]
    actually_null = {c for c in scout_cols if sub[c].isna().all()}
    unexpected = actually_null - EXPECTED_ALL_NULL_SCOUTS.get(year, set())
    assert not unexpected, f"{year}: scouts unexpectedly 100% null: {sorted(unexpected)}"


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_expected_null_scouts_have_actually_recovered_or_stayed_null(aggregated_df, year):
    """Guards `EXPECTED_ALL_NULL_SCOUTS` itself: if a scout documented as
    "genuinely absent that year" starts showing real values, that is
    itself worth a human noticing (upstream started backfilling, or the
    exception entry is stale) rather than the test suite staying silent."""
    sub = aggregated_df[aggregated_df["ano"] == year]
    documented_null = EXPECTED_ALL_NULL_SCOUTS.get(year, set())
    unexpectedly_populated = {c for c in documented_null if c in sub.columns and sub[c].notna().any()}
    assert not unexpectedly_populated, (
        f"{year}: scouts {sorted(unexpectedly_populated)} are documented as always-null in "
        "EXPECTED_ALL_NULL_SCOUTS but now have real values — update the exception map"
    )


def test_aggregated_id_clube_in_known_universe(aggregated_df):
    """Every resolved `id_clube` must be a value `team.TEAM_NAME_TO_ID` can
    actually produce — catches a promoted club whose name isn't in the map
    yet (today that fails silently into `NaN`; this at least surfaces it)."""
    known_ids = set(TEAM_NAME_TO_ID.values())
    unknown = set(aggregated_df["id_clube"].dropna().unique()) - known_ids
    assert not unknown, f"id_clube values outside the known club universe: {unknown}"


@pytest.mark.parametrize("year", sorted(y for y in YEAR_REGISTRY if y != 2014))
def test_at_least_nineteen_clubs_present_per_round(aggregated_df, year):
    """Brasileirão Série A has run with 20 clubs every year in this corpus.
    Real data dips to 19 in a couple of rounds (e.g. a postponed/rescheduled
    match), but never lower — a bound of `>= 18` (as originally proposed)
    would let an entire club's data silently vanish from a round without
    failing. 2014 is excluded: ~47% of its rows have no resolved
    `id_clube` at all (documented limitation), which would make this check
    meaningless for that year specifically.
    """
    sub = aggregated_df[aggregated_df["ano"] == year]
    clubs_per_round = sub.groupby("rodada")["id_clube"].nunique()
    too_few = clubs_per_round[clubs_per_round < 19]
    assert too_few.empty, f"{year}: rounds with <19 distinct clubs: {too_few.to_dict()}"
