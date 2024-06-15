import pandera as pa


class AttackScouts(pa.DataFrameModel):
    G: float = pa.Field(ge=0)
    FS: float = pa.Field(ge=0)
    PE: float = pa.Field(ge=0, nullable=True)
    A: float = pa.Field(ge=0)
    FT: float = pa.Field(ge=0)
    FD: float = pa.Field(ge=0)
    FF: float = pa.Field(ge=0)
    I: float = pa.Field(ge=0)  # noqa: E741
    PP: float = pa.Field(ge=0)


class DefenseScouts(pa.DataFrameModel):
    SG: float = pa.Field(ge=0)
    CV: float = pa.Field(ge=0)
    CA: float = pa.Field(ge=0)
    GS: float = pa.Field(ge=0)
    FC: float = pa.Field(ge=0)
    GC: float = pa.Field(ge=0)
    DP: float = pa.Field(ge=0)
    RB: float = pa.Field(ge=0, nullable=True)
    DD: float = pa.Field(ge=0, nullable=True)
