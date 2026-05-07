"""Team-entity transformations.

Always rebuilds ``id_clube`` from the normalized ``nome_clube``. This bypasses
the buggy raw ``clube_id`` in 2018 (string abbreviations, sometimes ambiguous
like ``"ATL"`` for both Atlético-MG and Atlético-PR).
"""

import logging

import pandas as pd
from unidecode import unidecode

logger = logging.getLogger(__name__)


TEAM_NAME_TO_ID: dict[str, int] = {
    "AME": 327,
    "AMÉRICA-MG": 327,
    "ATHLÉTICO-PR": 293,
    "ATLÉTICO-PR": 293,
    "CAP": 293,
    "ATLÉTICO-GO": 373,
    "CAM": 282,
    "ATLÉTICO-MG": 282,
    "AVA": 314,
    "AVAÍ": 314,
    "BAH": 265,
    "BAHIA": 265,
    "BOT": 263,
    "BOTAFOGO": 263,
    "BRAGANTINO": 280,
    "CEA": 354,
    "CEARÁ": 354,
    "CFC": 294,
    "CORITIBA": 294,
    "CHA": 315,
    "CHAPECOENSE": 315,
    "COR": 264,
    "CORINTHIANS": 264,
    "CRI": 288,
    "CRU": 283,
    "CRUZEIRO": 283,
    "CSA": 341,
    "CUIABÁ": 1371,
    "FIG": 316,
    "FIGUEIRENSE": 316,
    "FLA": 262,
    "FLAMENGO": 262,
    "FLU": 266,
    "FLUMINENSE": 266,
    "FOR": 356,
    "FORTALEZA": 356,
    "GOI": 290,
    "GOIÁS": 290,
    "GRE": 284,
    "GRÊMIO": 284,
    "INT": 285,
    "INTERNACIONAL": 285,
    "JEC": 317,
    "JOINVILLE": 317,
    "JUV": 286,
    "JUVENTUDE": 286,
    "MIR": 2305,
    "MIRASSOL": 2305,
    "RBB": 280,
    "RB BRAGANTINO": 280,
    "RED BULL BRAGANTINO": 280,
    "REM": 364,
    "REMO": 364,
    "CRICIÚMA": 288,
    "PAL": 275,
    "PALMEIRAS": 275,
    "PAR": 270,
    "PARANÁ": 270,
    "PON": 303,
    "PONTE PRETA": 303,
    "SAN": 277,
    "SANTOS": 277,
    "SAO": 276,
    "SÃO PAULO": 276,
    "SCZ": 344,
    "SANTA CRUZ": 344,
    "SPO": 292,
    "SPORT": 292,
    "SPT": 292,
    "VAS": 267,
    "VASCO": 267,
    "VIT": 287,
    "VITÓRIA": 287,
}
"""Full names and common abbreviations mapped to canonical Cartola team ids."""


_NAME_TO_ID_NORMALIZED: dict[str, int] = {
    unidecode(name.strip().upper()): team_id for name, team_id in TEAM_NAME_TO_ID.items()
}


def _normalize_name(name: object) -> str | None:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return None
    text = str(name).strip()
    if not text:
        return None
    return unidecode(text.upper())


_KNOWN_CLUBE_IDS: frozenset[int] = frozenset(TEAM_NAME_TO_ID.values())


def _maybe_numeric_clube_id(value: object) -> int | None:
    """Return ``int(value)`` when it matches a known Cartola clube id.

    Some 2020 rounds store the numeric id directly in the ``nome_clube``
    column (``"285"`` instead of ``"Internacional"``).

    Args:
        value: Raw cell from ``nome_clube``.

    Returns:
        The integer clube id if ``value`` is a digit-string in
        :data:`_KNOWN_CLUBE_IDS`; otherwise ``None``.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or not text.isdigit():
        return None
    candidate = int(text)
    return candidate if candidate in _KNOWN_CLUBE_IDS else None


def resolve_id_clube(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild ``id_clube`` from ``nome_clube`` using :data:`TEAM_NAME_TO_ID`.

    Rows whose ``nome_clube`` cannot be resolved get ``NaN`` ``id_clube`` and a
    single aggregated ``WARN`` log per ``(ano, nome_clube)`` group is emitted.

    Fallbacks (in order):

    1. If ``nome_clube`` is a numeric string matching a known Cartola clube id
       (some 2020 rounds store ``"285"`` instead of ``"Internacional"`` in
       the name column), resolve to that id directly.
    2. If ``nome_clube`` is missing entirely but the raw ``id_clube`` column
       holds a known unambiguous abbreviation (``"SAO"`` → 276 for the 2017
       coaches with NaN ``nome_clube``), resolve via :data:`TEAM_NAME_TO_ID`.
       Genuinely ambiguous codes like ``"ATL"`` (Atlético-MG vs -PR) are
       intentionally absent from the map and stay NaN.

    Args:
        df: Per-(player, round) DataFrame; may or may not have ``id_clube``.

    Returns:
        A copy of ``df`` with ``id_clube`` cast to ``Int32`` (nullable).
    """
    df = df.copy()

    if "nome_clube" not in df.columns:
        df["id_clube"] = pd.array([pd.NA] * len(df), dtype="Int32")
        return df

    raw_id_clube = df["id_clube"].copy() if "id_clube" in df.columns else None
    normalized = df["nome_clube"].map(_normalize_name)
    resolved = normalized.map(_NAME_TO_ID_NORMALIZED)

    df["id_clube"] = resolved.astype("Int32")

    unresolved_mask = (
        df["id_clube"].isna() & df["nome_clube"].notna() & (df["nome_clube"].astype(str).str.strip() != "")
    )
    if unresolved_mask.any():
        numeric_fallback = df.loc[unresolved_mask, "nome_clube"].map(_maybe_numeric_clube_id)
        df.loc[unresolved_mask, "id_clube"] = numeric_fallback.astype("Int32")

    if raw_id_clube is not None:
        missing_name_mask = df["id_clube"].isna() & df["nome_clube"].isna()
        if missing_name_mask.any():
            abbrev_fallback = raw_id_clube.loc[missing_name_mask].map(_normalize_name).map(_NAME_TO_ID_NORMALIZED)
            df.loc[missing_name_mask, "id_clube"] = abbrev_fallback.astype("Int32")

    unresolved_mask = (
        df["id_clube"].isna() & df["nome_clube"].notna() & (df["nome_clube"].astype(str).str.strip() != "")
    )
    if unresolved_mask.any():
        group_cols = [c for c in ("ano", "nome_clube") if c in df.columns]
        groups = (
            df.loc[unresolved_mask, group_cols].groupby(group_cols, dropna=False).size().sort_values(ascending=False)
        )
        for key, count in groups.items():
            logger.warning("Unresolved nome_clube=%r (%d row(s))", key, count)

    return df
