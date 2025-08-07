import pandera as pa


class Scouts(pa.DataFrameModel):
    A: int = pa.Field(ge=0, nullable=False)
    CA: int = pa.Field(ge=0, nullable=False)
    CV: int = pa.Field(ge=0, nullable=False)
    DE: int = pa.Field(ge=0, nullable=False)
    DP: int = pa.Field(ge=0, nullable=False)
    DS: int = pa.Field(ge=0, nullable=False)
    FC: int = pa.Field(ge=0, nullable=False)
    FD: int = pa.Field(ge=0, nullable=False)
    FF: int = pa.Field(ge=0, nullable=False)
    FS: int = pa.Field(ge=0, nullable=False)
    FT: int = pa.Field(ge=0, nullable=False)
    G: int = pa.Field(ge=0, nullable=False)
    GC: int = pa.Field(ge=0, nullable=False)
    GS: int = pa.Field(ge=0, nullable=False)
    I: int = pa.Field(ge=0, nullable=False)  # noqa: E741
    PC: float = pa.Field(ge=0, nullable=True)  # introduced in 2021
    PI: int = pa.Field(ge=0, nullable=False)
    PP: int = pa.Field(ge=0, nullable=False)
    PS: float = pa.Field(ge=0, nullable=True)  # introduced in 2021
    SG: int = pa.Field(ge=0, nullable=False)
