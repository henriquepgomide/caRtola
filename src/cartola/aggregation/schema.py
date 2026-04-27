"""Canonical schema for the aggregated Cartola DataFrame.

This module is the single source of truth for:
- column names and order in the final aggregated CSV (CANONICAL_COLUMNS, DTYPES)
- the canonical scout list (SCOUTS)
- categorical label maps (POSITION_MAP, STATUS_MAP)

The Pandera DataFrame model (AggregatedSchema) is added in a later task.
"""

from __future__ import annotations

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
