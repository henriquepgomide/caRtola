"""Player-entity transformations: position/status normalization and slug fill."""

from __future__ import annotations

import pandas as pd

from cartola.aggregation.schema import POSITION_MAP, STATUS_MAP
from cartola.commons.features import compute_slug

_POSITION_LABELS = set(POSITION_MAP.values())
_STATUS_LABELS = set(STATUS_MAP.values())


def _coerce_with_map(value: object, id_to_label: dict[int, str], known_labels: set[str]) -> object:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NA
    if isinstance(value, str):
        text = value.strip()
        if text in known_labels:
            return text
        try:
            value = int(text)
        except (TypeError, ValueError):
            return pd.NA
    try:
        return id_to_label.get(int(value), pd.NA)
    except (TypeError, ValueError):
        return pd.NA


def map_position(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the `posicao` column to the label set {gol, lat, zag, mei, ata, tec}.

    Accepts either int Cartola ids (legacy 2014–2016, 2023+) or pre-mapped label
    strings (2017–2022). Unknown values become NaN.
    """
    df = df.copy()
    if "posicao" not in df.columns:
        df["posicao"] = pd.array([pd.NA] * len(df), dtype="string")
        return df
    df["posicao"] = df["posicao"].map(lambda v: _coerce_with_map(v, POSITION_MAP, _POSITION_LABELS)).astype("string")
    return df


def map_status(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the `status` column to the label set {Provável, Dúvida, Suspenso, Contundido, Nulo}.

    Accepts either int ids (2023+) or label strings (2017–2022). Pre-2017 there
    is no status data → column is created as all-NaN.
    """
    df = df.copy()
    if "status" not in df.columns:
        df["status"] = pd.array([pd.NA] * len(df), dtype="string")
        return df
    df["status"] = df["status"].map(lambda v: _coerce_with_map(v, STATUS_MAP, _STATUS_LABELS)).astype("string")
    return df


def fill_missing_slug(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing `slug` values from `apelido` via compute_slug()."""
    df = df.copy()
    if "slug" not in df.columns:
        df["slug"] = pd.NA
    needs_fill = df["slug"].isna()
    if "apelido" in df.columns:
        df.loc[needs_fill, "slug"] = df.loc[needs_fill, "apelido"].map(
            lambda x: compute_slug(x) if isinstance(x, str) and x else pd.NA
        )
    return df
