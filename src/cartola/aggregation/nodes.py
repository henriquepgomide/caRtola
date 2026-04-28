"""Hamilton nodes for the aggregation pipeline.

One per-year node is generated dynamically from
:data:`~cartola.aggregation.catalog.YEAR_REGISTRY` via
:func:`~hamilton.function_modifiers.parameterize`, plus a final ``aggregated``
node that concatenates them.
"""

import warnings

import pandas as pd
from hamilton.function_modifiers import parameterize, value

from cartola.aggregation import columns, player, scouts, team
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS

_PARAMS = {f"year_{y}": {"year": value(y)} for y in YEAR_REGISTRY}


@parameterize(**_PARAMS)
def year_dataframe(year: int) -> pd.DataFrame:
    """Read raw data for ``year`` and apply entity-by-entity transformations.

    Args:
        year: Season year present in :data:`YEAR_REGISTRY`.

    Returns:
        One year of data in the canonical schema (``CANONICAL_COLUMNS`` order).
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
    """Concat all year DataFrames, preserving :data:`CANONICAL_COLUMNS` order.

    Parameter names must mirror keys in :data:`YEAR_REGISTRY` exactly;
    ``test_nodes.test_*`` asserts this invariant.

    Args:
        year_2014: Year-2014 DataFrame produced by :func:`year_dataframe`.
        year_2015: Year-2015 DataFrame produced by :func:`year_dataframe`.
        year_2016: Year-2016 DataFrame produced by :func:`year_dataframe`.
        year_2017: Year-2017 DataFrame produced by :func:`year_dataframe`.
        year_2018: Year-2018 DataFrame produced by :func:`year_dataframe`.
        year_2019: Year-2019 DataFrame produced by :func:`year_dataframe`.
        year_2020: Year-2020 DataFrame produced by :func:`year_dataframe`.
        year_2021: Year-2021 DataFrame produced by :func:`year_dataframe`.
        year_2022: Year-2022 DataFrame produced by :func:`year_dataframe`.
        year_2023: Year-2023 DataFrame produced by :func:`year_dataframe`.
        year_2024: Year-2024 DataFrame produced by :func:`year_dataframe`.
        year_2025: Year-2025 DataFrame produced by :func:`year_dataframe`.
        year_2026: Year-2026 DataFrame produced by :func:`year_dataframe`.

    Returns:
        Concatenated DataFrame with rows from every non-empty year, reset
        index, in :data:`CANONICAL_COLUMNS` order.
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
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, message=".*empty or all-NA.*")
        merged = pd.concat(non_empty, ignore_index=True)
    return merged.reset_index(drop=True).reindex(columns=CANONICAL_COLUMNS)
