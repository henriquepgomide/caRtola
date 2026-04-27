"""Team-entity transformations.

Always rebuilds `id_clube` from the normalized `nome_clube`. This bypasses the
buggy raw `clube_id` in 2018 (string abbreviations, sometimes ambiguous like
"ATL" for both Atlético-MG and Atlético-PR).
"""

from __future__ import annotations

import logging

import pandas as pd
from unidecode import unidecode

logger = logging.getLogger(__name__)


# Full names + common abbreviations → canonical Cartola team id.
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

# Pre-computed normalized lookup (uppercased + accent-stripped) for O(1) match.
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


def resolve_id_clube(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild `id_clube` from `nome_clube` using TEAM_NAME_TO_ID.

    Returns the input DataFrame with `id_clube` cast to `Int32` (nullable).
    Rows whose `nome_clube` cannot be resolved get NaN id_clube and a single
    aggregated WARN log per (ano, nome_clube) group is emitted.
    """
    df = df.copy()

    if "nome_clube" not in df.columns:
        df["id_clube"] = pd.array([pd.NA] * len(df), dtype="Int32")
        return df

    normalized = df["nome_clube"].map(_normalize_name)
    resolved = normalized.map(_NAME_TO_ID_NORMALIZED)

    df["id_clube"] = resolved.astype("Int32")

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
