import pandera as pa

from cartola.schemas.scouts import Scouts


class AggregatedSchema(Scouts):
    rodada: int = pa.Field(ge=0, le=38)
    participou: float = pa.Field(isin=[0, 1], nullable=True)  # nullable=False, type=int/bool
    media: float = pa.Field()
    preco: float = pa.Field(gt=0)
    variacao: float = pa.Field()
    num_jogos: float = pa.Field(ge=0, nullable=True)
    pontuacao: float = pa.Field()
