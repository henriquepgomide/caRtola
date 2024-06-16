import pandera as pa

from cartola.schemas.scouts import Scouts


class AggregatedSchema(Scouts):
    apelido: str = pa.Field(nullable=False)
    ano: int = pa.Field(nullable=False)
    media: float = pa.Field(nullable=False)
    num_jogos: float = pa.Field(ge=0, nullable=True)
    participou: float = pa.Field(isin=[0, 1], nullable=True)  # type=int/bool
    pontuacao: float = pa.Field(nullable=False)
    posicao: str = pa.Field(nullable=False, isin=["gol", "lat", "zag", "mei", "ata", "tec"])
    preco: float = pa.Field(gt=0, nullable=False)
    rodada: int = pa.Field(ge=0, le=38, nullable=False)
    slug: str = pa.Field(nullable=False)
    variacao: float = pa.Field(nullable=False)
