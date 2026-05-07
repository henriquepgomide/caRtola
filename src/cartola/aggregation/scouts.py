"""Scout-entity transformations: rename, disaccumulate, NaN policy."""

import pandas as pd

from cartola.aggregation.schema import SCOUTS

SCOUT_RENAME_MAP: dict[str, str] = {
    "PE": "PI",
    "RB": "DS",
    "DD": "DE",
}
"""Legacy scout column names mapped to canonical names."""


def harmonize_scout_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename legacy scout columns to canonical names.

    Args:
        df: Per-(player, round) DataFrame with raw scout columns.

    Returns:
        A copy of ``df`` with ``PE → PI``, ``RB → DS`` and ``DD → DE``.
    """
    return df.rename(columns=SCOUT_RENAME_MAP)


def disaccumulate_scouts(df: pd.DataFrame, scout_cols: list[str]) -> pd.DataFrame:
    """Convert season-cumulative scouts to per-round values.

    The Cartola API returns scouts as season-cumulative for some years
    (2015, 2017-2022). The per-round delta for a ``(player, round, scout)``
    is computed against the player's running cumulative maximum across
    previous appearances:

    .. code-block:: text

        delta_N = max(cum_N - cummax(cum_1..N-1), 0)

    This is more robust than a naive ``cum_N - cum_(N-1)`` ``.diff()``
    because Cartola occasionally lowers a season-cumulative value
    retroactively (e.g. an assist credit reviewed and removed). With the
    running-cummax baseline:

    * If ``cum_N`` drops below the previous high, ``delta_N = 0`` — a
      player cannot perform a negative number of actions in a single
      round, so the correction is attributed to a past round we cannot
      identify forward-only.
    * The next round whose cumulative exceeds the previous high resumes
      producing positive deltas correctly relative to that high
      (a naive ``.diff()`` against the corrected lower value would
      double-count those events).

    Edge cases:
        * Player skipped a round → ``delta = 0`` for the next appearance
          if the cumulative did not change.
        * First appearance of a player → previous cummax is treated as
          ``0``, so ``delta = cum_N`` (the cumulative at first appearance
          is taken as the per-round value).

    Args:
        df: Per-(player, round) DataFrame with cumulative scout columns.
        scout_cols: Names of the scout columns to disaccumulate.

    Returns:
        A copy of ``df`` (sorted by ``id_atleta``, ``rodada``) with
        ``scout_cols`` replaced by per-round values, all ``>= 0``.
    """
    df = df.sort_values(["id_atleta", "rodada"], kind="mergesort").reset_index(drop=True).copy()
    df[scout_cols] = df[scout_cols].fillna(0.0)

    cummax = df.groupby("id_atleta", sort=False)[scout_cols].cummax()
    prev_cummax = cummax.groupby(df["id_atleta"], sort=False).shift(1).fillna(0.0)
    df[scout_cols] = (df[scout_cols] - prev_cummax).clip(lower=0).values
    return df


def process(df: pd.DataFrame, *, accumulated: bool, has_scouts: bool) -> pd.DataFrame:
    """Apply the canonical scout pipeline.

    Behavior:
        * ``has_scouts=False`` → all 21 :data:`~cartola.aggregation.schema.SCOUTS`
          become NaN columns (e.g. 2025).
        * ``has_scouts=True`` → rename ``PE``/``RB``/``DD``; missing scout values
          within a year fill with ``0.0``; if ``accumulated``, run
          :func:`disaccumulate_scouts` on present scouts.

    Scout columns absent from the input remain absent — they will be NaN after
    the final reindex against ``CANONICAL_COLUMNS`` in
    :func:`cartola.aggregation.nodes.year_dataframe`.

    Args:
        df: Per-(player, round) DataFrame.
        accumulated: ``True`` when the source year ships season-cumulative scouts.
        has_scouts: ``True`` when the source year publishes scout columns at all.

    Returns:
        A copy of ``df`` with the scout columns harmonized for that year.
    """
    df = df.copy()

    if not has_scouts:
        for col in SCOUTS:
            df[col] = pd.NA
        return df

    df = harmonize_scout_names(df)
    present = [c for c in SCOUTS if c in df.columns]
    if not present:
        return df
    df[present] = df[present].fillna(0.0)
    if accumulated:
        df = disaccumulate_scouts(df, scout_cols=present)
    return df
