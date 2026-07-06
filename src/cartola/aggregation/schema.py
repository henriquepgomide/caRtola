"""Canonical schema for the aggregated Cartola DataFrame.

This module is the single source of truth for:

* column names and order in the final aggregated CSV
  (:data:`CANONICAL_COLUMNS`, :data:`DTYPES`)
* the canonical scout list (:data:`SCOUTS`)
* categorical label maps (:data:`POSITION_MAP`, :data:`STATUS_MAP`)
* the Pandera DataFrame model (:class:`AggregatedSchema`) used as the
  data-quality contract.
* per-scout plausibility ceilings enforced as ``le`` bounds in
  :class:`AggregatedSchema` for every scout except ``G``/``CA``
  (:data:`SCOUT_ROUND_CEILINGS`); the analogous ``ge``/``le`` bounds for
  the five context columns are inlined directly on their fields in
  :class:`AggregatedSchema` (see the class docstring for their
  calibration).
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

SCOUT_ROUND_CEILINGS: dict[str, float] = {
    "A": 6,
    "CA": 3,
    "CV": 2,
    "DE": 20,
    "DP": 3,
    "DS": 18,
    "FC": 15,
    "FD": 10,
    "FF": 10,
    "FS": 18,
    "FT": 5,
    "G": 6,
    "GC": 3,
    "GS": 12,
    "I": 10,
    "PC": 3,
    "PI": 60,
    "PP": 3,
    "PS": 3,
    "SG": 3,
    "V": 3,
}
"""Plausible per-round ceiling for each scout.

Enforced as the ``le`` bound in :class:`AggregatedSchema` for every scout
**except** ``G`` and ``CA`` (see the class docstring for why those two are
excluded), and reused verbatim by
``tests/data_quality/test_scout_and_club_consistency.py`` to check ``G``/
``CA`` too, via a documented-exception list instead of a hard schema bound
(so a *real* future anomaly in either column still fails loudly).

Calibrated from the real 2014-2026 corpus: for every scout below, the
historical maximum *excluding* the one known-corrupted snapshot
(``ano=2020, rodada=10`` — the raw ``rodada-10.csv`` ships ``G``/``CA``
values that spike and then revert on the very next round, e.g. player
69345 goes ``G: NaN -> 35 -> NaN`` across rounds 9/10/11 — a genuine
upstream data glitch, not a computation bug) is well under the ceiling
here, with headroom for legitimate outliers (a busy goalkeeper with 14
saves, a foul-fest with 12 ``FS``, etc.).
"""

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

    The five per-round context columns (``pontuacao``, ``media``, ``preco``,
    ``variacao``, ``num_jogos``) each have a plausible ``ge``/``le`` range
    inlined on their field below, with no exceptions — unlike
    :data:`SCOUT_ROUND_CEILINGS`, there is no known real-data anomaly
    affecting any of these columns: the ``ano=2020, rodada=10`` upstream
    glitch that forces ``G``/``CA`` to go unbounded does not affect them,
    so all five are safe to enforce with no carve-out. Calibrated from the
    real 2014-2026 corpus (per-year extremes, not just the aggregate)
    with headroom above/below the observed range: ``pontuacao``
    -12.0..37.7, ``media`` -12.0..25.8, ``preco`` 0.63..35.18, ``variacao``
    -10.07..14.8, ``num_jogos`` 0..38 (bounded naturally by the 38-round
    season; ``NaN`` in years that never published this field, e.g.
    2014-2016/2018/2019).

    Every scout except ``G`` and ``CA`` also has an upper bound from
    :data:`SCOUT_ROUND_CEILINGS`. ``G``/``CA`` are deliberately excluded:
    the real 2014-2026 corpus contains a known upstream data glitch
    (``ano=2020, rodada=10``) with physically-implausible values for
    exactly those two columns (e.g. 35 goals) that this schema does not
    attempt to filter out or correct — see
    ``tests/data_quality/test_scout_and_club_consistency.py`` for a test
    that documents/tracks that specific exception instead. Adding a
    ``le`` bound for ``G``/``CA`` here would make
    :func:`~cartola.aggregation.driver.run` raise on real, already-known
    data instead of producing an actionable, documented test failure.
    """

    ano: Series[int] = pa.Field(ge=2014, le=2030)
    rodada: Series[int] = pa.Field(ge=1, le=38)
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

    pontuacao: Series[float] = pa.Field(nullable=True, ge=-20.0, le=50.0)
    media: Series[float] = pa.Field(nullable=True, ge=-20.0, le=35.0)
    preco: Series[float] = pa.Field(nullable=True, ge=0.0, le=45.0)

    variacao: Series[float] = pa.Field(nullable=True, ge=-15.0, le=20.0)
    num_jogos: Series[pd.Int16Dtype] = pa.Field(nullable=True, ge=0.0, le=38.0)

    # G/CA intentionally have no `le`: see the known-anomaly note in the
    # class docstring above.
    A: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["A"])
    CA: Series[float] = pa.Field(nullable=True, ge=0)
    CV: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["CV"])
    DE: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["DE"])
    DP: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["DP"])
    DS: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["DS"])
    FC: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["FC"])
    FD: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["FD"])
    FF: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["FF"])
    FS: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["FS"])
    FT: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["FT"])
    G: Series[float] = pa.Field(nullable=True, ge=0)
    GC: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["GC"])
    GS: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["GS"])
    I: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["I"])  # noqa: E741
    PC: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["PC"])
    PI: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["PI"])
    PP: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["PP"])
    PS: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["PS"])
    SG: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["SG"])
    V: Series[float] = pa.Field(nullable=True, ge=0, le=SCOUT_ROUND_CEILINGS["V"])

    class Config:
        """Pandera schema configuration: strict columns, coerced dtypes, unique key."""

        strict = True
        coerce = True
        unique: ClassVar[list[str]] = ["ano", "rodada", "id_atleta"]
