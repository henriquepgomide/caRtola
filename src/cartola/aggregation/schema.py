"""Canonical schema for the aggregated Cartola DataFrame.

This module is the single source of truth for:
- column names and order in the final aggregated CSV (CANONICAL_COLUMNS, DTYPES)
- the canonical scout list (SCOUTS)
- categorical label maps (POSITION_MAP, STATUS_MAP)
- the Pandera DataFrame model (AggregatedSchema) used as the data-quality contract
"""

from __future__ import annotations

import pandas as pd

SCOUTS: list[str] = [
    "A",
    "CA",
    "CV",
    "DE",
    "DP",
    "DS",
    "FC",
    "FD",
    "FF",
    "FS",
    "FT",
    "G",
    "GC",
    "GS",
    "I",
    "PC",
    "PI",
    "PP",
    "PS",
    "SG",
    "V",
]

CANONICAL_COLUMNS: list[str] = [
    # contexto
    "ano",
    "rodada",
    "id_clube",
    "nome_clube",
    "id_atleta",
    # info do jogador
    "nome",
    "apelido",
    "apelido_abreviado",
    "slug",
    "foto",
    "posicao",
    "status",
    "pontuacao",
    "media",
    "preco",
    # game state
    "variacao",
    "num_jogos",
    # scouts
    *SCOUTS,
]

# Per-column pandas dtypes used after harmonization.
# Nullable types (Int*) are required for columns that may legitimately be NaN.
DTYPES: dict[str, str] = {
    "ano": "int16",
    "rodada": "int8",
    "id_clube": "Int32",
    "nome_clube": "string",
    "id_atleta": "int64",
    "nome": "string",
    "apelido": "string",
    "apelido_abreviado": "string",
    "slug": "string",
    "foto": "string",
    "posicao": "string",
    "status": "string",
    "pontuacao": "float32",
    "media": "float32",
    "preco": "float32",
    "variacao": "float32",
    "num_jogos": "Int16",
    **{col: "float32" for col in SCOUTS},
}

POSITION_MAP: dict[int, str] = {
    1: "gol",
    2: "lat",
    3: "zag",
    4: "mei",
    5: "ata",
    6: "tec",
}

# Source: Kedro legacy conf/base/parameters.yml.
STATUS_MAP: dict[int, str] = {
    2: "Dúvida",
    3: "Suspenso",
    5: "Contundido",
    6: "Nulo",
    7: "Provável",
}


# ---------------------------------------------------------------------------
# Pandera schema (data-quality contract)
# ---------------------------------------------------------------------------
import pandera.pandas as pa  # noqa: E402  (kept here to keep the constants section clean)
from pandera.typing import Series  # noqa: E402


class AggregatedSchema(pa.DataFrameModel):
    """Pandera contract for the final aggregated DataFrame."""

    ano: Series[int] = pa.Field(ge=2014, le=2030)
    rodada: Series[int] = pa.Field(ge=0, le=38)
    id_clube: Series[pd.Int32Dtype] = pa.Field(nullable=True)
    nome_clube: Series[str] = pa.Field(nullable=True)
    id_atleta: Series[int]

    nome: Series[str] = pa.Field(nullable=True)
    apelido: Series[str] = pa.Field(nullable=True)
    apelido_abreviado: Series[str] = pa.Field(nullable=True)
    slug: Series[str] = pa.Field(nullable=True)
    foto: Series[str] = pa.Field(nullable=True)
    posicao: Series[str] = pa.Field(nullable=True)
    status: Series[str] = pa.Field(nullable=True)

    pontuacao: Series[float] = pa.Field(nullable=True)
    media: Series[float] = pa.Field(nullable=True)
    preco: Series[float] = pa.Field(nullable=True)

    variacao: Series[float] = pa.Field(nullable=True)
    num_jogos: Series[pd.Int16Dtype] = pa.Field(nullable=True)

    A: Series[float] = pa.Field(nullable=True, ge=0)
    CA: Series[float] = pa.Field(nullable=True, ge=0)
    CV: Series[float] = pa.Field(nullable=True, ge=0)
    DE: Series[float] = pa.Field(nullable=True, ge=0)
    DP: Series[float] = pa.Field(nullable=True, ge=0)
    DS: Series[float] = pa.Field(nullable=True, ge=0)
    FC: Series[float] = pa.Field(nullable=True, ge=0)
    FD: Series[float] = pa.Field(nullable=True, ge=0)
    FF: Series[float] = pa.Field(nullable=True, ge=0)
    FS: Series[float] = pa.Field(nullable=True, ge=0)
    FT: Series[float] = pa.Field(nullable=True, ge=0)
    G: Series[float] = pa.Field(nullable=True, ge=0)
    GC: Series[float] = pa.Field(nullable=True, ge=0)
    GS: Series[float] = pa.Field(nullable=True, ge=0)
    I: Series[float] = pa.Field(nullable=True, ge=0)  # noqa: E741  (Cartola scout name)
    PC: Series[float] = pa.Field(nullable=True, ge=0)
    # PI/DS can be negative after disaccumulation if Cartola corrected backwards.
    PI: Series[float] = pa.Field(nullable=True)
    PP: Series[float] = pa.Field(nullable=True, ge=0)
    PS: Series[float] = pa.Field(nullable=True, ge=0)
    SG: Series[float] = pa.Field(nullable=True, ge=0)
    V: Series[float] = pa.Field(nullable=True, ge=0)

    class Config:
        strict = True
        coerce = True
        unique = ["ano", "rodada", "id_atleta"]
