"""Preprocessing nodes for per-year Cartola pipelines."""

from typing import Dict

import pandas as pd

from cartola.commons.features import compute_slug


def fill_scouts_with_zeros(df: pd.DataFrame, dict_scouts: Dict[str, float]) -> pd.DataFrame:
    """Fill NaN scout values with zero.

    Note: this only runs at the per-year preprocessing stage. The aggregate
    pipeline reverts missing-by-absence scouts back to NaN (NaN means "this
    scout was not tracked in this year").
    """
    scouts_cols = [c for c in dict_scouts.keys() if c in df.columns]
    if not scouts_cols:
        return df
    df = df.copy()
    df[scouts_cols] = df[scouts_cols].fillna(0)
    return df


def fill_empty_slugs(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a slug from the player's nickname when the slug column is missing/empty."""
    if "slug" not in df.columns:
        df = df.copy()
        df["slug"] = None

    empty_slugs = df["slug"].isna()
    if empty_slugs.any():
        df = df.copy()
        df.loc[empty_slugs, "slug"] = df.loc[empty_slugs, "apelido"].apply(compute_slug)
    return df


def map_status_id_to_string(df: pd.DataFrame, dict_status_to_str: Dict[int, str]) -> pd.DataFrame:
    """Map integer status ids to human-readable Portuguese labels."""
    if "status" not in df.columns:
        return df
    df = df.copy()
    df["status"] = df["status"].replace(dict_status_to_str)
    return df


def map_posicao_to_string(df: pd.DataFrame, dict_posicao_to_str: Dict[str, str]) -> pd.DataFrame:
    """Map integer position ids (as strings) to lowercase position labels."""
    df = df.copy()
    df["posicao"] = df["posicao"].astype(str).replace(dict_posicao_to_str)
    return df


def add_year_column(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Append an `ano` column equal to `year` for every row."""
    df = df.copy()
    df["ano"] = year
    return df
