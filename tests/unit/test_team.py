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


def test_resolve_id_clube_treats_empty_string_name_as_unresolved():
    """Hit ``_normalize_name`` empty-string branch (line 104)."""
    df = pd.DataFrame({"nome_clube": ["", "  "], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].isna().all()


def test_maybe_numeric_clube_id_returns_none_for_nan():
    """Direct check of the NaN-guard in ``_maybe_numeric_clube_id`` (line 125)."""
    assert team._maybe_numeric_clube_id(None) is None
    assert team._maybe_numeric_clube_id(float("nan")) is None
    assert team._maybe_numeric_clube_id("") is None
    assert team._maybe_numeric_clube_id("not-a-digit") is None


def test_resolve_id_clube_handles_missing_nome_clube_column():
    """Hit the ``if 'nome_clube' not in df.columns`` branch (lines 159-160)."""
    df = pd.DataFrame({"id_atleta": [1, 2, 3]})
    out = team.resolve_id_clube(df)
    assert "id_clube" in out.columns
    assert out["id_clube"].isna().all()
    assert str(out["id_clube"].dtype) == "Int32"


def test_resolve_id_clube_falls_back_to_raw_abbreviation_when_name_missing():
    # 2017 ships ~114 rows (mostly coaches) with NaN nome_clube but a known
    # string abbreviation in the raw id_clube column. Recover the
    # unambiguous ones; refuse to guess truly ambiguous codes like "ATL"
    # (could mean Atlético-MG or Atlético-PR).
    df = pd.DataFrame(
        {
            "nome_clube": [None, None, None, None],
            "id_clube": ["SAO", "FLU", "ATL", "ZZZ"],
        }
    )
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 276  # São Paulo
    assert out["id_clube"].iloc[1] == 266  # Fluminense
    assert pd.isna(out["id_clube"].iloc[2])  # ATL is ambiguous → stays NaN
    assert pd.isna(out["id_clube"].iloc[3])  # unknown abbreviation stays NaN
