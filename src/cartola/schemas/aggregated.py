import pandera as pa

from cartola.schemas.scouts import Scouts


class AggregatedSchema(Scouts):
    rodada: int = pa.Field(ge=0, le=38, nullable=False)
    participou: float = pa.Field(isin=[0, 1], nullable=True)  # nullable=False, type=int/bool
    media: float = pa.Field(nullable=False)
    preco: float = pa.Field(gt=0, nullable=False)
    variacao: float = pa.Field(nullable=False)
    num_jogos: float = pa.Field(ge=0, nullable=True)
    pontuacao: float = pa.Field(nullable=False)
    posicao: str = pa.Field(nullable=False, isin=["gol", "lat", "zag", "mei", "ata", "tec"])
