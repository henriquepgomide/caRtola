"""Canonical schema for the aggregated Cartola DataFrame.

This module is the single source of truth for:

* column names and order in the final aggregated CSV
  (:data:`CANONICAL_COLUMNS`, :data:`DTYPES`)
* the canonical scout list (:data:`SCOUTS`)
* categorical label maps (:data:`POSITION_MAP`, :data:`STATUS_MAP`)
* the Pandera DataFrame model (:class:`AggregatedSchema`) used as the
  data-quality contract.
"""

from typing import ClassVar

import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

SCOUTS: list[str] = [
    "A",
    "CA",
    "CV",
    "DE",
    "DP",
    "DS",
    "FC",
    "FD",
    "FF",
    "FS",
    "FT",
    "G",
    "GC",
    "GS",
    "I",
    "PC",
    "PI",
    "PP",
    "PS",
    "SG",
    "V",
]

CANONICAL_COLUMNS: list[str] = [
    "ano",
    "rodada",
    "id_clube",
    "nome_clube",
    "id_atleta",
    "nome",
    "apelido",
    "apelido_abreviado",
    "slug",
    "foto",
    "posicao",
    "status",
    "pontuacao",
    "media",
    "preco",
    "variacao",
    "num_jogos",
    *SCOUTS,
]

DTYPES: dict[str, str] = {
    "ano": "int16",
    "rodada": "int8",
    "id_clube": "Int32",
    "nome_clube": "string",
    "id_atleta": "int64",
    "nome": "string",
    "apelido": "string",
    "apelido_abreviado": "string",
    "slug": "string",
    "foto": "string",
    "posicao": "string",
    "status": "string",
    "pontuacao": "float64",
    "media": "float64",
    "preco": "float64",
    "variacao": "float64",
    "num_jogos": "Int16",
    **dict.fromkeys(SCOUTS, "float64"),
}
"""Per-column pandas dtypes used after harmonization.

Nullable types (``Int*``) are required for columns that may legitimately be NaN.
Floats are ``float64`` to match :class:`AggregatedSchema` (``Series[float]``)
and avoid precision artifacts when Pandera ``coerce=True`` upcasts on
validation — round-tripping ``float32`` through ``float64`` and back to a
text CSV produces visible noise like ``4.49 → 4.489999771118164``.
"""

_NON_NULLABLE_NUMERIC: frozenset[str] = frozenset(
    {"float32", "float64", "int8", "int16", "int32", "int64"},
)


def apply_canonical_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns present in ``df`` to the dtype declared in :data:`DTYPES`.

    For non-nullable numeric targets, cells holding ``pd.NA`` are first
    coerced to ``np.nan`` via :func:`pandas.to_numeric` because pandas
    refuses to ``astype("float32")`` an object column containing ``pd.NA``
    (raises ``TypeError: float() argument ... not 'NAType'``).

    Columns absent from ``df`` are skipped silently — callers that need
    canonical column presence should reindex against
    :data:`CANONICAL_COLUMNS` first.

    Args:
        df: Frame whose columns will be coerced in-place on a copy.

    Returns:
        A copy of ``df`` with applicable columns cast to canonical dtypes.
    """
    out = df.copy()
    for col, dtype in DTYPES.items():
        if col not in out.columns:
            continue
        if dtype in _NON_NULLABLE_NUMERIC:
            out[col] = pd.to_numeric(out[col], errors="coerce")
        out[col] = out[col].astype(dtype)
    return out


POSITION_MAP: dict[int, str] = {
    1: "gol",
    2: "lat",
    3: "zag",
    4: "mei",
    5: "ata",
    6: "tec",
}

STATUS_MAP: dict[int, str] = {
    2: "Dúvida",
    3: "Suspenso",
    5: "Contundido",
    6: "Nulo",
    7: "Provável",
}
"""Status id → label, sourced from the legacy Kedro ``conf/base/parameters.yml``."""


class AggregatedSchema(pa.DataFrameModel):
    """Pandera contract for the final aggregated DataFrame.

    All per-round scout columns must be ``>= 0``: scouts represent counts
    of in-game events (goals, assists, fouls suffered/committed, etc.) and
    a player cannot perform a negative number of actions in a single
    round. When the source data ships season-cumulative scouts,
    :func:`~cartola.aggregation.scouts.disaccumulate_scouts` is responsible
    for producing per-round deltas that respect this invariant — a
    retroactive Cartola correction lowering a cumulative count is treated
    as ``0`` for the current round (the past round's count was wrong, but
    the player did not perform a negative action this round).
    """

    ano: Series[int] = pa.Field(ge=2014, le=2030)
    rodada: Series[int] = pa.Field(ge=0, le=38)
    id_clube: Series[pd.Int32Dtype] = pa.Field(nullable=True)
    nome_clube: Series[str] = pa.Field(nullable=True)
    id_atleta: Series[int]

    nome: Series[str] = pa.Field(nullable=True)
    apelido: Series[str] = pa.Field(nullable=True)
    apelido_abreviado: Series[str] = pa.Field(nullable=True)
    slug: Series[str] = pa.Field(nullable=True)
    foto: Series[str] = pa.Field(nullable=True)
    posicao: Series[str] = pa.Field(nullable=True)
    status: Series[str] = pa.Field(nullable=True)

    pontuacao: Series[float] = pa.Field(nullable=True)
    media: Series[float] = pa.Field(nullable=True)
    preco: Series[float] = pa.Field(nullable=True)

    variacao: Series[float] = pa.Field(nullable=True)
    num_jogos: Series[pd.Int16Dtype] = pa.Field(nullable=True)

    A: Series[float] = pa.Field(nullable=True, ge=0)
    CA: Series[float] = pa.Field(nullable=True, ge=0)
    CV: Series[float] = pa.Field(nullable=True, ge=0)
    DE: Series[float] = pa.Field(nullable=True, ge=0)
    DP: Series[float] = pa.Field(nullable=True, ge=0)
    DS: Series[float] = pa.Field(nullable=True, ge=0)
    FC: Series[float] = pa.Field(nullable=True, ge=0)
    FD: Series[float] = pa.Field(nullable=True, ge=0)
    FF: Series[float] = pa.Field(nullable=True, ge=0)
    FS: Series[float] = pa.Field(nullable=True, ge=0)
    FT: Series[float] = pa.Field(nullable=True, ge=0)
    G: Series[float] = pa.Field(nullable=True, ge=0)
    GC: Series[float] = pa.Field(nullable=True, ge=0)
    GS: Series[float] = pa.Field(nullable=True, ge=0)
    I: Series[float] = pa.Field(nullable=True, ge=0)  # noqa: E741
    PC: Series[float] = pa.Field(nullable=True, ge=0)
    PI: Series[float] = pa.Field(nullable=True, ge=0)
    PP: Series[float] = pa.Field(nullable=True, ge=0)
    PS: Series[float] = pa.Field(nullable=True, ge=0)
    SG: Series[float] = pa.Field(nullable=True, ge=0)
    V: Series[float] = pa.Field(nullable=True, ge=0)

    class Config:
        """Pandera schema configuration: strict columns, coerced dtypes, unique key."""

        strict = True
        coerce = True
        unique: ClassVar[list[str]] = ["ano", "rodada", "id_atleta"]
