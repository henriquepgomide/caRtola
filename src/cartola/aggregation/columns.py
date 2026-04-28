"""Cross-cutting column rename: raw CSV column names → canonical schema names.

Sourced from the legacy Kedro ``parameters.yml::preprocessing.map_col_names``
plus columns we explicitly drop because they are noise or out-of-canon.
"""

import pandas as pd

COLUMN_RENAME_MAP: dict[str, str] = {
    "Apelido": "apelido",
    "AtletaID": "id_atleta",
    "ClubeID": "id_clube",
    "ClubeNome": "nome_clube",
    "Nome": "nome_clube",
    "Rodada": "rodada",
    "Pontos": "pontuacao",
    "PontosMedia": "media",
    "Preco": "preco",
    "PrecoVariacao": "variacao",
    "PosicaoID": "posicao",
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
"""Raw column name → canonical name.

Order does not matter; pandas resolves by exact match. Keys cover three eras:

* Legacy 2014-2016 PascalCase (``Apelido``, ``AtletaID``, ``Rodada``, ...).
* 2017 monolithic ``snake_case`` API (``atleta_id``, ``clube_id``, ...).
* Modern 2017+ ``atletas.*`` prefix (``atletas.apelido``, ``atletas.atleta_id``, ...).
"""

COLUMNS_TO_DROP: frozenset[str] = frozenset(
    {
        "",
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
        "Abreviacao",
    }
)
"""Raw column names dropped unconditionally as noise, legacy-only, or out-of-canon.

The empty string entry (``""``) catches the unnamed index column written by
R/pandas with ``index=True``.
"""


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop noise columns then rename raw → canonical via :data:`COLUMN_RENAME_MAP`.

    Unknown columns are passed through unchanged so downstream entity modules
    (and the final reindex against
    :data:`~cartola.aggregation.schema.CANONICAL_COLUMNS`) can decide what to
    keep.

    Args:
        df: Raw per-(player, round) DataFrame from one of the readers.

    Returns:
        A new DataFrame with :data:`COLUMNS_TO_DROP` removed and the surviving
        columns renamed via :data:`COLUMN_RENAME_MAP`.
    """
    keep = [c for c in df.columns if c not in COLUMNS_TO_DROP]
    return df[keep].rename(columns=COLUMN_RENAME_MAP)
