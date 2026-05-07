"""Hamilton nodes for the aggregation pipeline.

One per-year node is generated dynamically from
:data:`~cartola.aggregation.catalog.YEAR_REGISTRY` via
:func:`~hamilton.function_modifiers.parameterize`. The final ``aggregated``
node fans those years in via :func:`~hamilton.function_modifiers.inject` +
:func:`~hamilton.function_modifiers.group`, so adding year ``N+1`` is a
single-line edit in :data:`YEAR_REGISTRY` (genuine single source of truth).
"""

import pandas as pd
from hamilton.function_modifiers import group, inject, parameterize, source, value

from cartola.aggregation import columns, player, scouts, team
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS, apply_canonical_dtypes

_YEARS: list[int] = sorted(YEAR_REGISTRY)
_PARAMS: dict[str, dict[str, object]] = {f"year_{y}": {"year": value(y)} for y in _YEARS}
_YEAR_SOURCES = [source(f"year_{y}") for y in _YEARS]


@parameterize(**_PARAMS)
def year_dataframe(year: int) -> pd.DataFrame:
    """Read raw data for ``year`` and apply entity-by-entity transformations.

    Args:
        year: Season year present in :data:`YEAR_REGISTRY`.

    Returns:
        One year of data in the canonical schema (``CANONICAL_COLUMNS``
        order) with dtypes from
        :data:`~cartola.aggregation.schema.DTYPES` applied so downstream
        ``pd.concat`` does not need to reconcile mixed dtypes.
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
    return apply_canonical_dtypes(df.reindex(columns=CANONICAL_COLUMNS))


@inject(year_frames=group(*_YEAR_SOURCES))
def aggregated(year_frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Concat all year DataFrames, preserving :data:`CANONICAL_COLUMNS` order.

    Year inputs are wired automatically from :data:`YEAR_REGISTRY` via
    ``@inject(group(source(...)))``, so this function does not need to know
    how many years exist.

    Args:
        year_frames: Per-year DataFrames produced by :func:`year_dataframe`,
            collected by Hamilton from every ``year_<Y>`` node.

    Returns:
        Concatenated DataFrame with rows from every non-empty year, reset
        index, in :data:`CANONICAL_COLUMNS` order. Returns an empty
        canonical DataFrame when every input is empty.
    """
    non_empty = [f for f in year_frames if not f.empty]
    if not non_empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    merged = pd.concat(non_empty, ignore_index=True)
    return merged.reset_index(drop=True).reindex(columns=CANONICAL_COLUMNS)
