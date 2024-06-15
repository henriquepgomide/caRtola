import pandera as pa

from cartola.schemas.scouts import AttackScouts, DefenseScouts


class AggregatedSchema(AttackScouts, DefenseScouts):
    rodada: int = pa.Field(ge=0, le=38)
    participou: float = pa.Field(isin=[0, 1], nullable=True)  # nullable=False, type=int/bool
    media: float = pa.Field()
    preco: float = pa.Field(gt=0)
    variacao: float = pa.Field()
