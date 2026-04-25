from collections.abc import Callable
from typing import Dict, List

import pandas as pd


def drop_duplicated_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(ignore_index=True)


def drop_columns(df: pd.DataFrame, list_cols: List[str]) -> pd.DataFrame:
    """Drop the listed columns, ignoring any that are absent from the frame.

    The same per-year `drop_columns` parameter is reused across years whose
    raw schemas drift slightly; tolerating missing columns keeps the
    parameter set small without requiring a unique file per year.
    """
    return df.drop(columns=list_cols, errors="ignore")


def concat_partitioned_datasets(
    partitioned_dataset: Dict[str, Callable[[], pd.DataFrame]],
) -> pd.DataFrame:
    """Concatenate all partitions in a Kedro PartitionedDataset.

    Materializes every partition once and concatenates in a single
    `pd.concat` call (O(n) total) rather than the historical O(n^2)
    accumulator pattern.
    """
    if not partitioned_dataset:
        return pd.DataFrame()

    frames = [load() for load in partitioned_dataset.values()]
    return pd.concat(frames, ignore_index=True)


def rename_cols(df: pd.DataFrame, map_col_names: Dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=map_col_names)
