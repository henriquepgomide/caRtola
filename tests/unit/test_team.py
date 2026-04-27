"""Tests for team-entity transformations."""

import logging

import pandas as pd

from cartola.aggregation import team


def test_resolve_id_clube_full_name():
    df = pd.DataFrame({"nome_clube": ["Flamengo"], "id_clube": [pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 262


def test_resolve_id_clube_abbreviation():
    df = pd.DataFrame({"nome_clube": ["FLA"], "id_clube": [pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 262


def test_resolve_id_clube_with_accents():
    df = pd.DataFrame({"nome_clube": ["São Paulo", "SAO PAULO"], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert (out["id_clube"] == 276).all()


def test_resolve_id_clube_unknown_name_stays_nan(caplog):
    df = pd.DataFrame(
        {
            "ano": [2024, 2024],
            "nome_clube": ["Time XYZ", "Time XYZ"],
            "id_clube": [pd.NA, pd.NA],
        }
    )
    with caplog.at_level(logging.WARNING):
        out = team.resolve_id_clube(df)
    assert out["id_clube"].isna().all()
    assert any("Time XYZ" in record.message for record in caplog.records)


def test_resolve_id_clube_overrides_raw_2018_atl_ambiguity():
    # 2018 raw has id_clube="ATL" (string abbreviation, ambiguous between MG and PR).
    # We always rebuild from the full name → id 282.
    df = pd.DataFrame({"nome_clube": ["Atlético-MG"], "id_clube": ["ATL"]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 282


def test_resolve_id_clube_parana():
    df = pd.DataFrame({"nome_clube": ["Paraná"], "id_clube": [pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 270


def test_resolve_id_clube_returns_int32_nullable_dtype():
    df = pd.DataFrame({"nome_clube": ["Flamengo", "Time XYZ"], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert str(out["id_clube"].dtype) == "Int32"


def test_resolve_id_clube_handles_nan_name():
    df = pd.DataFrame({"nome_clube": [None, "Flamengo"], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert pd.isna(out["id_clube"].iloc[0])
    assert out["id_clube"].iloc[1] == 262


def test_resolve_id_clube_numeric_string_falls_back_to_known_id():
    # 2020 from rodada-12 onwards stores the numeric clube_id (e.g. "285")
    # directly in the nome_clube column. We resolve to that id when it's a
    # known Cartola team id.
    df = pd.DataFrame(
        {"nome_clube": ["285", "262", "999999"], "id_clube": [pd.NA, pd.NA, pd.NA]},
    )
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 285  # Internacional
    assert out["id_clube"].iloc[1] == 262  # Flamengo
    assert pd.isna(out["id_clube"].iloc[2])  # unknown id stays NaN
