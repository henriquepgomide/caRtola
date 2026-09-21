"""Aggregate-all-years pipeline nodes."""

from collections.abc import Callable
from typing import Dict, List

import pandas as pd

from cartola.commons.scouts import disaccumulate_scouts


def _year_from_partition_key(key: str) -> int:
    """Parse the trailing 4-digit year from a partition key like 'preprocessed_2018'."""
    digits = "".join(c for c in key.split("_")[-1] if c.isdigit())
    if len(digits) != 4:
        raise ValueError(f"Cannot extract year from partition key {key!r}")
    return int(digits)


def _assert_year_matches(df: pd.DataFrame, year: int, partition_key: str) -> None:
    """Raise if `df['ano']` carries a year other than `year`."""
    if "ano" not in df.columns or not len(df):
        return
    unique_years = df["ano"].dropna().unique().tolist()
    if unique_years and set(unique_years) != {year}:
        raise ValueError(
            f"Partition {partition_key!r} year mismatch: filename={year}, "
            f"ano column has {unique_years}",
        )


def _project_to_canonical(
    df: pd.DataFrame, canonical_columns: List[str], scout_columns: List[str]
) -> pd.DataFrame:
    """Add any missing canonical columns (NaN-filled) and project to that order."""
    for col in canonical_columns:
        if col not in df.columns:
            df[col] = pd.NA if col not in scout_columns else float("nan")
    return df.loc[:, canonical_columns].copy()


def _coerce_id_clube_and_participou(
    df: pd.DataFrame, clube_id_map: Dict[str, int] | None
) -> pd.DataFrame:
    """Normalize mixed-type id_clube and participou columns to numeric dtypes.

    Across years `id_clube` shows up as int, '262.0' string, float, or even
    a club abbreviation (e.g. 2017's 'FLA'). `participou` similarly mixes
    1/0, True/False, and 'True'/'False'. Both are coerced to numeric so the
    downstream schema validates and downstream consumers see consistent types.
    """
    if "id_clube" in df.columns:
        id_clube = df["id_clube"].astype("object")
        if clube_id_map:
            id_clube = id_clube.map(
                lambda v: clube_id_map.get(v, v) if isinstance(v, str) else v
            )
        df["id_clube"] = pd.to_numeric(id_clube, errors="coerce")
    if "participou" in df.columns:
        participou = df["participou"].astype("object").replace(
            {"True": 1, "False": 0, "true": 1, "false": 0, True: 1, False: 0}
        )
        df["participou"] = pd.to_numeric(participou, errors="coerce")
    return df


def _drop_invalid_rodadas(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out rodada < 1 (pre-season placeholder rows in some years' raw data)."""
    if "rodada" not in df.columns:
        return df
    return df[df["rodada"].fillna(0).astype(int) >= 1]


def _dedupe_player_round(df: pd.DataFrame, scout_columns: List[str]) -> pd.DataFrame:
    """Collapse duplicate (id_atleta, rodada) rows, preferring the lowest scout sum.

    Re-scraped source rows are typically inflated (e.g. a 2020 round-10 row
    with G=113 next to another row with G=0). Keeping the lower-sum row gives
    disaccumulation a well-defined cumulative sequence.
    """
    if not {"id_atleta", "rodada"}.issubset(df.columns):
        return df
    present_scouts = [c for c in scout_columns if c in df.columns]
    if not present_scouts:
        return df.drop_duplicates(subset=["id_atleta", "rodada"], keep="first")
    return (
        df.assign(_scout_sum=df[present_scouts].fillna(0).sum(axis=1))
        .sort_values("_scout_sum", kind="stable")
        .drop_duplicates(subset=["id_atleta", "rodada"], keep="first")
        .drop(columns="_scout_sum")
    )


def normalize_partitions(
    partitions: Dict[str, Callable[[], pd.DataFrame]],
    canonical_columns: List[str],
    scout_columns: List[str],
    accumulated_years: List[int],
    clube_id_map: Dict[str, int] | None = None,
) -> Dict[int, pd.DataFrame]:
    """Normalize each per-year partition to the canonical column set.

    For each partition this:
      * extracts the year from the partition key,
      * asserts the `ano` column matches the filename year,
      * projects to `canonical_columns` (NaN-filling missing ones),
      * coerces mixed-dtype columns (id_clube, participou) to numeric,
      * drops invalid rodadas and de-duplicates (id_atleta, rodada),
      * applies `disaccumulate_scouts` if the year is in `accumulated_years`.

    Args:
        partitions: Kedro PartitionedDataset payload (dict of partition_id -> load_func).
        canonical_columns: ordered list of columns the output should contain.
        scout_columns: subset of canonical_columns that are scouts (NaN-filled if missing).
        accumulated_years: years whose source data is cumulative-per-round.
        clube_id_map: optional mapping of club abbreviation -> numeric id.

    Returns:
        Dict keyed by year, each value a DataFrame with exactly the canonical columns.
    """
    normalized: Dict[int, pd.DataFrame] = {}
    for partition_key, load_partition in partitions.items():
        year = _year_from_partition_key(partition_key)
        df = load_partition()
        _assert_year_matches(df, year, partition_key)
        df = _project_to_canonical(df, canonical_columns, scout_columns)
        df = _coerce_id_clube_and_participou(df, clube_id_map)
        df = _drop_invalid_rodadas(df)
        df = _dedupe_player_round(df, scout_columns)
        if year in accumulated_years:
            df = disaccumulate_scouts(df, scout_columns).loc[:, canonical_columns]
        normalized[year] = df.reset_index(drop=True)
    return normalized


def concat_normalized_partitions(normalized: Dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate normalized per-year DataFrames in ascending year order."""
    years = sorted(normalized.keys())
    return pd.concat([normalized[y] for y in years], ignore_index=True)


def finalize_aggregated(df: pd.DataFrame, dtype_map: Dict[str, type]) -> pd.DataFrame:
    """Apply final dtype map and sort rows for a stable, diff-friendly CSV."""
    df = df.astype({k: v for k, v in dtype_map.items() if k in df.columns})
    sort_cols = [c for c in ("ano", "rodada", "id_clube", "slug") if c in df.columns]
    return df.sort_values(sort_cols).reset_index(drop=True)
