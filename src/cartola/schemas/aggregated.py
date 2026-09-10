"""Pandera schema for the aggregated multi-year Cartola dataset."""

import pandera.pandas as pa

from cartola.schemas.scouts import Scouts


class AggregatedSchema(Scouts):
    """Canonical schema for data/04_feature/aggregated.csv."""

    id_atleta: float = pa.Field(nullable=True)
    slug: str = pa.Field(nullable=False)
    apelido: str = pa.Field(nullable=False)
    nome: str = pa.Field(nullable=True)
    posicao: str = pa.Field(
        nullable=False,
        isin=["gol", "lat", "zag", "mei", "ata", "tec"],
    )
    status: str = pa.Field(
        nullable=True,
        isin=["Provável", "Dúvida", "Suspenso", "Contundido", "Nulo"],
    )
    id_clube: float = pa.Field(nullable=True)
    nome_clube: str = pa.Field(nullable=True)
    ano: int = pa.Field(ge=2014, le=2026, nullable=False)
    rodada: int = pa.Field(ge=1, le=38, nullable=False)
    participou: float = pa.Field(isin=[0, 1], nullable=True)
    num_jogos: float = pa.Field(ge=0, nullable=True)
    pontuacao: float = pa.Field(nullable=False)
    media: float = pa.Field(nullable=True)
    preco: float = pa.Field(gt=0, nullable=True)
    variacao: float = pa.Field(nullable=False)
