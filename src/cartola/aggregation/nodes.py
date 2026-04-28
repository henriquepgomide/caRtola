"""Hamilton nodes for the aggregation pipeline.

One per-year node is generated dynamically from YEAR_REGISTRY via
@parameterize, plus a final `aggregated` node that concatenates them.
"""

from __future__ import annotations

import warnings

import pandas as pd
from hamilton.function_modifiers import parameterize, value

from cartola.aggregation import columns, player, scouts, team
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS

_PARAMS = {f"year_{y}": {"year": value(y)} for y in YEAR_REGISTRY}


@parameterize(**_PARAMS)
def year_dataframe(year: int) -> pd.DataFrame:
    """Reads raw data for `year` and applies entity-by-entity transformations
    to produce one year of data in the canonical schema.
    """
    cfg = YEAR_REGISTRY[year]
    raw = cfg.reader(cfg.raw_dir, year)
    df = columns.rename_columns(raw)
    df = team.resolve_id_clube(df)
    df = player.map_position(df)
    df = player.map_status(df)
    df = player.fill_missing_slug(df)
    df = player.dedupe_per_rodada(df)
    df = scouts.process(df, accumulated=cfg.accumulated, has_scouts=cfg.has_scouts)
    df["ano"] = year
    return df.reindex(columns=CANONICAL_COLUMNS)


def aggregated(
    year_2014: pd.DataFrame,
    year_2015: pd.DataFrame,
    year_2016: pd.DataFrame,
    year_2017: pd.DataFrame,
    year_2018: pd.DataFrame,
    year_2019: pd.DataFrame,
    year_2020: pd.DataFrame,
    year_2021: pd.DataFrame,
    year_2022: pd.DataFrame,
    year_2023: pd.DataFrame,
    year_2024: pd.DataFrame,
    year_2025: pd.DataFrame,
    year_2026: pd.DataFrame,
) -> pd.DataFrame:
    """Concat all year DataFrames, preserving CANONICAL_COLUMNS order.

    Parameter names must mirror keys in YEAR_REGISTRY exactly; nodes.test_*
    asserts this invariant.
    """
    frames = [
        year_2014,
        year_2015,
        year_2016,
        year_2017,
        year_2018,
        year_2019,
        year_2020,
        year_2021,
        year_2022,
        year_2023,
        year_2024,
        year_2025,
        year_2026,
    ]
    non_empty = [f for f in frames if not f.empty]
    if not non_empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    # Older years legitimately have all-NA columns (e.g. 2014 lacks new scouts);
    # the canonical schema requires we keep those columns so suppress the
    # informational FutureWarning about all-NA dtype handling.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, message=".*empty or all-NA.*")
        merged = pd.concat(non_empty, ignore_index=True)
    return merged.reset_index(drop=True).reindex(columns=CANONICAL_COLUMNS)
