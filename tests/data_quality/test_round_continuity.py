"""Round-continuity checks: every season should have no unexplained gaps.

Marked `slow` because it depends on the real, fully-aggregated pipeline
output (see the session-scoped `aggregated_df` fixture in `tests/conftest.py`).
"""

import pytest

from cartola.aggregation.catalog import YEAR_REGISTRY

pytestmark = pytest.mark.slow

KNOWN_ROUND_GAPS: dict[int, set[int]] = {
    # 2015's raw `2015_scouts_raw.csv` genuinely has no rows for round 26 for
    # any player (confirmed against the raw file, not a processing bug), and
    # the season's last recorded round is 37 (round 38 never appears at
    # all, so it is a trailing boundary, not an internal gap).
    2015: {26},
}
"""Documented, investigated exceptions to round continuity.

Any gap NOT listed here is treated as a regression: either a genuine new
data-quality issue in a fresh raw drop, or a pipeline bug that dropped a
round's data (e.g. a reader silently skipping a file, an off-by-one in
`_ROUND_FILE_RE`, etc). Add to this dict only after confirming the gap
exists in the raw data itself, mirroring the investigation note above.
"""


@pytest.mark.parametrize("year", sorted(YEAR_REGISTRY))
def test_round_continuity_no_undocumented_gaps(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    rounds = set(sub["rodada"].unique())
    assert rounds, f"{year}: no rounds found at all"

    lo, hi = min(rounds), max(rounds)
    gaps = set(range(lo, hi + 1)) - rounds - KNOWN_ROUND_GAPS.get(year, set())
    assert not gaps, f"{year}: undocumented round gaps: {sorted(gaps)}"


def test_known_round_gaps_are_still_accurate(aggregated_df):
    """Guards the exception list itself: if 2015's round 26 ever starts
    showing up in the data (e.g. a raw data backfill), this test forces a
    human to notice and remove the now-stale entry from
    `KNOWN_ROUND_GAPS`, rather than the gap-detection test just silently
    staying green for the wrong reason."""
    for year, documented_gaps in KNOWN_ROUND_GAPS.items():
        sub = aggregated_df[aggregated_df["ano"] == year]
        present_rounds = set(sub["rodada"].unique())
        unexpectedly_present = documented_gaps & present_rounds
        assert not unexpectedly_present, (
            f"{year}: rounds {sorted(unexpectedly_present)} are documented as missing in "
            "KNOWN_ROUND_GAPS but are actually present now — update the exception list"
        )
