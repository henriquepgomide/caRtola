"""Pandera schema validation tests."""

import pandas as pd
import pandera.pandas as pa
import pytest

from cartola.aggregation.schema import CANONICAL_COLUMNS, SCOUTS, AggregatedSchema


def _good_row(**overrides):
    base = {col: pd.NA for col in CANONICAL_COLUMNS}
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
