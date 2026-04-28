"""Player-entity transformations: position/status normalization and slug fill."""

import logging

import pandas as pd
from unidecode import unidecode

from cartola.aggregation.schema import POSITION_MAP, SCOUTS, STATUS_MAP

logger = logging.getLogger(__name__)

_POSITION_LABELS = set(POSITION_MAP.values())
_STATUS_LABELS = set(STATUS_MAP.values())


def compute_slug(nickname: str) -> str:
    """Compute a URL-friendly slug from a player nickname.

    Args:
        nickname: Raw player nickname (e.g. ``"Yago Pikachu"``).

    Returns:
        Lowercased, accent-stripped, hyphenated slug (e.g. ``"yago-pikachu"``).
    """
    return unidecode(nickname.lower().replace(" ", "-"))


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
    """Normalize the ``posicao`` column to canonical position labels.

    Accepts either int Cartola ids (legacy 2014-2016, 2023+) or pre-mapped label
    strings (2017-2022). Unknown values become NaN.

    Args:
        df: Per-(player, round) DataFrame that may or may not contain ``posicao``.

    Returns:
        A copy of ``df`` with ``posicao`` cast to ``string`` and values restricted
        to the label set ``{gol, lat, zag, mei, ata, tec}``. If ``posicao`` is
        missing from the input, it is added as an all-NaN ``string`` column.
    """
    df = df.copy()
    if "posicao" not in df.columns:
        df["posicao"] = pd.array([pd.NA] * len(df), dtype="string")
        return df
    df["posicao"] = df["posicao"].map(lambda v: _coerce_with_map(v, POSITION_MAP, _POSITION_LABELS)).astype("string")
    return df


def map_status(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the ``status`` column to canonical status labels.

    Accepts either int ids (2023+) or label strings (2017-2022). Pre-2017 there
    is no status data, so the column is created as all-NaN.

    Args:
        df: Per-(player, round) DataFrame that may or may not contain ``status``.

    Returns:
        A copy of ``df`` with ``status`` cast to ``string`` and values restricted
        to the label set ``{Provável, Dúvida, Suspenso, Contundido, Nulo}``.
    """
    df = df.copy()
    if "status" not in df.columns:
        df["status"] = pd.array([pd.NA] * len(df), dtype="string")
        return df
    df["status"] = df["status"].map(lambda v: _coerce_with_map(v, STATUS_MAP, _STATUS_LABELS)).astype("string")
    return df


def fill_missing_slug(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing ``slug`` values from ``apelido`` via :func:`compute_slug`.

    Args:
        df: Per-(player, round) DataFrame.

    Returns:
        A copy of ``df`` where rows with NaN ``slug`` have it computed from
        ``apelido``. If ``slug`` is absent it is created; if ``apelido`` is
        absent the slug stays NaN.
    """
    df = df.copy()
    if "slug" not in df.columns:
        df["slug"] = pd.NA
    needs_fill = df["slug"].isna()
    if "apelido" in df.columns:
        df.loc[needs_fill, "slug"] = df.loc[needs_fill, "apelido"].map(
            lambda x: compute_slug(x) if isinstance(x, str) and x else pd.NA
        )
    return df


def dedupe_per_rodada(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate ``(rodada, id_atleta)`` rows, keeping the richest copy.

    Upstream raw files occasionally list the same atleta twice in the same
    snapshot — once with NaN scouts and once with the actual values
    (observed in 2020 round 10). We keep whichever copy carries the most
    non-NA scout columns, breaking ties by ``num_jogos`` and ``pontuacao``.
    Rows that are unique already pass through untouched.

    Args:
        df: Per-(player, round) DataFrame.

    Returns:
        A copy of ``df`` with duplicate ``(rodada, id_atleta)`` rows collapsed.
        If either key column is missing, the input is returned unchanged.
    """
    if "rodada" not in df.columns or "id_atleta" not in df.columns:
        return df

    dup_mask = df.duplicated(subset=["rodada", "id_atleta"], keep=False)
    if not dup_mask.any():
        return df

    scout_cols = [c for c in SCOUTS if c in df.columns]
    df = df.copy()
    if scout_cols:
        df["_dedupe_scout_filled"] = df[scout_cols].notna().sum(axis=1)
    else:
        df["_dedupe_scout_filled"] = 0

    sort_cols = ["_dedupe_scout_filled"]
    if "num_jogos" in df.columns:
        sort_cols.append("num_jogos")
    if "pontuacao" in df.columns:
        sort_cols.append("pontuacao")

    before = len(df)
    df = (
        df.sort_values(sort_cols, ascending=False, kind="stable", na_position="last")
        .drop_duplicates(subset=["rodada", "id_atleta"], keep="first")
        .sort_index()
        .drop(columns=["_dedupe_scout_filled"])
    )
    dropped = before - len(df)
    if dropped:
        logger.info("dedupe_per_rodada dropped %d duplicate (rodada, id_atleta) row(s)", dropped)
    return df.reset_index(drop=True)
