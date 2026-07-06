"""Pandera schema validation tests."""

import pandas as pd
import pandera.pandas as pa
import pytest

from cartola.aggregation.schema import CANONICAL_COLUMNS, SCOUT_ROUND_CEILINGS, SCOUTS, AggregatedSchema

# G/CA are intentionally excluded from the schema's `le` bound — see the
# known ano=2020/rodada=10 anomaly documented in AggregatedSchema's docstring
# and in tests/data_quality/test_scout_and_club_consistency.py.
SCOUTS_WITH_CEILING = [c for c in SCOUTS if c not in {"G", "CA"}]

# Mirrors the literal `ge`/`le` values inlined on AggregatedSchema's context
# fields (`pontuacao`, `media`, `preco`, `variacao`, `num_jogos`) — keep in
# sync with `src/cartola/aggregation/schema.py` if those bounds ever change.
CONTEXT_COLUMN_BOUNDS: dict[str, tuple[float, float]] = {
    "pontuacao": (-20.0, 50.0),
    "media": (-20.0, 35.0),
    "preco": (0.0, 45.0),
    "variacao": (-15.0, 20.0),
    "num_jogos": (0.0, 38.0),
}


def _good_row(**overrides):
    base = dict.fromkeys(CANONICAL_COLUMNS, pd.NA)
    base.update(
        {
            "ano": 2024,
            "rodada": 1,
            "id_clube": 262,
            "nome_clube": "Flamengo",
            "id_atleta": 1,
            "apelido": "Foo",
            "slug": "foo",
            "posicao": "mei",
            "pontuacao": 5.0,
            "media": 5.0,
            "preco": 8.0,
            "variacao": 0.0,
        }
    )
    for col in SCOUTS:
        base[col] = 0.0
    base.update(overrides)
    return base


def _build_df(rows):
    """Build a small DataFrame with dtypes that mirror what the real pipeline produces.

    `coerce=True` on the schema lets Pandera handle minor numeric upcasts.
    """
    df = pd.DataFrame(rows, columns=CANONICAL_COLUMNS)
    df["ano"] = df["ano"].astype("int64")
    df["rodada"] = df["rodada"].astype("int64")
    df["id_clube"] = df["id_clube"].astype("Int32")
    df["id_atleta"] = df["id_atleta"].astype("int64")
    df["num_jogos"] = df["num_jogos"].astype("Int16")
    for col in (
        "nome_clube",
        "nome",
        "apelido",
        "apelido_abreviado",
        "slug",
        "foto",
        "posicao",
        "status",
    ):
        df[col] = df[col].astype("string")
    for col in ("pontuacao", "media", "preco", "variacao", *SCOUTS):
        df[col] = df[col].astype("float64")
    return df


def test_valid_minimal_row_passes():
    df = _build_df([_good_row()])
    AggregatedSchema.validate(df)


def test_id_clube_nullable_passes():
    df = _build_df([_good_row(id_clube=pd.NA, nome_clube="Time XYZ")])
    AggregatedSchema.validate(df)


def test_rodada_out_of_range_fails():
    df = _build_df([_good_row(rodada=99)])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


def test_ano_out_of_range_fails():
    df = _build_df([_good_row(ano=1990)])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


def test_unique_ano_rodada_id_atleta_violation_fails():
    rows = [_good_row(id_atleta=1), _good_row(id_atleta=1)]
    df = _build_df(rows)
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


@pytest.mark.parametrize("scout", SCOUTS_WITH_CEILING)
def test_scout_value_at_ceiling_passes(scout):
    """`le` is inclusive: a value exactly at the documented ceiling (e.g. a
    goalkeeper with 20 saves) is a legitimate outlier, not a violation."""
    df = _build_df([_good_row(**{scout: SCOUT_ROUND_CEILINGS[scout]})])
    AggregatedSchema.validate(df)


@pytest.mark.parametrize("scout", SCOUTS_WITH_CEILING)
def test_scout_value_above_ceiling_fails(scout):
    """Regression guard: every scout except G/CA must reject a per-round
    value above its `SCOUT_ROUND_CEILINGS` bound (e.g. 21 saves, 4 red
    cards) — physically implausible for a single match."""
    df = _build_df([_good_row(**{scout: SCOUT_ROUND_CEILINGS[scout] + 1})])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


@pytest.mark.parametrize("scout", ["G", "CA"])
def test_g_and_ca_have_no_ceiling_enforced(scout):
    """G/CA are the two columns affected by the known ano=2020/rodada=10
    upstream corruption (see AggregatedSchema's docstring); a value far
    above their reference ceiling must still pass schema validation so a
    full pipeline run over real data does not start raising on data we
    already know about and have chosen not to alter."""
    df = _build_df([_good_row(**{scout: SCOUT_ROUND_CEILINGS[scout] + 100})])
    AggregatedSchema.validate(df)


@pytest.mark.parametrize("col", CONTEXT_COLUMN_BOUNDS)
def test_context_column_at_bounds_passes(col):
    """`ge`/`le` are inclusive: a value exactly at either edge of the
    field's bound (e.g. a 38-game season) is legitimate, not a
    violation."""
    lo, hi = CONTEXT_COLUMN_BOUNDS[col]
    df = _build_df([_good_row(**{col: lo}), _good_row(id_atleta=2, **{col: hi})])
    AggregatedSchema.validate(df)


@pytest.mark.parametrize("col", CONTEXT_COLUMN_BOUNDS)
def test_context_column_below_lower_bound_fails(col):
    """Regression guard: every context column must reject a value just
    below its `ge` lower bound."""
    lo, _hi = CONTEXT_COLUMN_BOUNDS[col]
    df = _build_df([_good_row(**{col: lo - 1})])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


@pytest.mark.parametrize("col", CONTEXT_COLUMN_BOUNDS)
def test_context_column_above_upper_bound_fails(col):
    """Regression guard: every context column must reject a value just
    above its `le` upper bound."""
    _lo, hi = CONTEXT_COLUMN_BOUNDS[col]
    df = _build_df([_good_row(**{col: hi + 1})])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)
