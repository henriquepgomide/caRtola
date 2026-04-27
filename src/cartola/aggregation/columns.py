"""Cross-cutting column rename: raw CSV column names → canonical schema names.

Sourced from the legacy Kedro `parameters.yml::preprocessing.map_col_names` plus
columns we explicitly drop because they are noise or out-of-canon.
"""

from __future__ import annotations

import pandas as pd

# Raw column name → canonical name. Order does not matter; pandas resolves by exact match.
COLUMN_RENAME_MAP: dict[str, str] = {
    # ---- legacy 2014–2016 ---------------------------------------------------
    "Apelido": "apelido",
    "AtletaID": "id_atleta",
    "ClubeID": "id_clube",
    "ClubeNome": "nome_clube",
    "Nome": "nome_clube",  # appears as the team name in 2014_times.csv merge
    "Rodada": "rodada",
    "Pontos": "pontuacao",
    "PontosMedia": "media",
    "Preco": "preco",
    "PrecoVariacao": "variacao",
    "PosicaoID": "posicao",
    # ---- snake_case API (2017 monolithic with mixed naming) -----------------
    "atleta_id": "id_atleta",
    "clube_id": "id_clube",
    "rodada_id": "rodada",
    "posicao_id": "posicao",
    "status_id": "status",
    "pontos_num": "pontuacao",
    "media_num": "media",
    "preco_num": "preco",
    "variacao_num": "variacao",
    "jogos_num": "num_jogos",
    # ---- modern `atletas.*` prefix (2017+) ----------------------------------
    "atletas.apelido": "apelido",
    "atletas.apelido_abreviado": "apelido_abreviado",
    "atletas.atleta_id": "id_atleta",
    "atletas.clube.id.full.name": "nome_clube",
    "atletas.clube_id": "id_clube",
    "atletas.foto": "foto",
    "atletas.jogos_num": "num_jogos",
    "atletas.media_num": "media",
    "atletas.nome": "nome",
    "atletas.pontos_num": "pontuacao",
    "atletas.posicao_id": "posicao",
    "atletas.preco_num": "preco",
    "atletas.rodada_id": "rodada",
    "atletas.slug": "slug",
    "atletas.status_id": "status",
    "atletas.variacao_num": "variacao",
}

# Columns we drop unconditionally (noise, legacy-only, or out-of-canon).
COLUMNS_TO_DROP: frozenset[str] = frozenset(
    {
        "",  # unnamed index column written by R/pandas with index=True
        "Participou",
        "participou",
        "Posicao",
        "Jogos",
        "Partida",
        "Mando",
        "Titular",
        "Substituido",
        "TempoJogado",
        "Nota",
        "athletes.atletas.scout",
        "atletas.minimo_para_valorizar",
        "atletas.entrou_em_campo",
        "atletas.temporada_id",
        "Abreviacao",  # from times.csv merge — not part of canonical schema
    }
)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop noise columns then rename raw → canonical via COLUMN_RENAME_MAP.

    Unknown columns are passed through unchanged so downstream entity modules
    (and the final reindex against CANONICAL_COLUMNS) can decide what to keep.
    """
    keep = [c for c in df.columns if c not in COLUMNS_TO_DROP]
    return df[keep].rename(columns=COLUMN_RENAME_MAP)
