import pandera as pa


class Scouts(pa.DataFrameModel):
    A: int = pa.Field(ge=0)
    CA: int = pa.Field(ge=0)
    CV: int = pa.Field(ge=0)
    DE: int = pa.Field(ge=0)
    DP: int = pa.Field(ge=0)
    DS: int = pa.Field(ge=0)
    FC: int = pa.Field(ge=0)
    FD: int = pa.Field(ge=0)
    FF: int = pa.Field(ge=0)
    FS: int = pa.Field(ge=0)
    FT: int = pa.Field(ge=0)
    G: int = pa.Field(ge=0)
    GC: int = pa.Field(ge=0)
    GS: int = pa.Field(ge=0)
    I: int = pa.Field(ge=0)  # noqa: E741
    PI: int = pa.Field(ge=0)
    PP: int = pa.Field(ge=0)
    SG: int = pa.Field(ge=0)
