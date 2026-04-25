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


def normalize_partitions(
    partitions: Dict[str, Callable[[], pd.DataFrame]],
    canonical_columns: List[str],
    scout_columns: List[str],
    accumulated_years: List[int],
) -> Dict[int, pd.DataFrame]:
    """Normalize each per-year partition to the canonical column set.

    For each partition:
      * extracts the year from the partition key,
      * asserts the `ano` column matches the filename year,
      * selects + reorders to `canonical_columns`, filling missing scout
        columns with NaN and missing meta columns with NaN,
      * applies `disaccumulate_scouts` if the year is in `accumulated_years`.

    Args:
        partitions: Kedro PartitionedDataset payload (dict of partition_id -> load_func).
        canonical_columns: ordered list of columns the output should contain.
        scout_columns: subset of canonical_columns that are scouts (filled with NaN if missing).
        accumulated_years: years whose source data is cumulative-per-round.

    Returns:
        Dict keyed by year, each value a DataFrame with exactly the canonical columns.
    """
    normalized: Dict[int, pd.DataFrame] = {}
    for partition_key, load_partition in partitions.items():
        year = _year_from_partition_key(partition_key)
        df = load_partition()

        if "ano" in df.columns and len(df):
            unique_years = df["ano"].dropna().unique().tolist()
            if unique_years and set(unique_years) != {year}:
                raise ValueError(
                    f"Partition {partition_key!r} year mismatch: filename={year}, "
                    f"ano column has {unique_years}",
                )

        for col in canonical_columns:
            if col not in df.columns:
                df[col] = pd.NA if col not in scout_columns else float("nan")

        df = df.loc[:, canonical_columns].copy()

        if year in accumulated_years:
            df = disaccumulate_scouts(df, scout_columns)
            df = df.loc[:, canonical_columns]

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
