"""Pandera schema for the Cartola scout columns."""

import pandera.pandas as pa


class Scouts(pa.DataFrameModel):
    """Per-round scout values. All scouts are nullable; non-null must be >= 0."""

    A: float = pa.Field(ge=0, nullable=True)
    CA: float = pa.Field(ge=0, nullable=True)
    CV: float = pa.Field(ge=0, nullable=True)
    DE: float = pa.Field(ge=0, nullable=True)
    DP: float = pa.Field(ge=0, nullable=True)
    DS: float = pa.Field(ge=0, nullable=True)
    FC: float = pa.Field(ge=0, nullable=True)
    FD: float = pa.Field(ge=0, nullable=True)
    FF: float = pa.Field(ge=0, nullable=True)
    FS: float = pa.Field(ge=0, nullable=True)
    FT: float = pa.Field(ge=0, nullable=True)
    G: float = pa.Field(ge=0, nullable=True)
    GC: float = pa.Field(ge=0, nullable=True)
    GS: float = pa.Field(ge=0, nullable=True)
    I: float = pa.Field(ge=0, nullable=True)  # noqa: E741
    PC: float = pa.Field(ge=0, nullable=True)
    PI: float = pa.Field(ge=0, nullable=True)
    PP: float = pa.Field(ge=0, nullable=True)
    PS: float = pa.Field(ge=0, nullable=True)
    SG: float = pa.Field(ge=0, le=1, nullable=True)
