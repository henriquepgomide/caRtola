"""Tests for player-entity transformations."""

import pandas as pd

from cartola.aggregation import player


def test_map_position_int_id_to_label():
    df = pd.DataFrame({"posicao": [1, 5]})
    out = player.map_position(df)
    assert out["posicao"].tolist() == ["gol", "ata"]


def test_map_position_passes_through_existing_labels():
    # 2017-2022 already store the label string.
    df = pd.DataFrame({"posicao": ["zag", "mei"]})
    out = player.map_position(df)
    assert out["posicao"].tolist() == ["zag", "mei"]


def test_map_position_unknown_value_becomes_nan():
    df = pd.DataFrame({"posicao": [99, "alien"]})
    out = player.map_position(df)
    assert out["posicao"].isna().all()


def test_map_position_handles_missing_column():
    df = pd.DataFrame({"id_atleta": [1, 2]})
    out = player.map_position(df)
    assert "posicao" in out.columns
    assert out["posicao"].isna().all()


def test_map_status_int_id_to_label():
    df = pd.DataFrame({"status": [7, 5, 6]})
    out = player.map_status(df)
    assert out["status"].tolist() == ["Provável", "Contundido", "Nulo"]


def test_map_status_passes_through_existing_labels():
    df = pd.DataFrame({"status": ["Provável", "Suspenso"]})
    out = player.map_status(df)
    assert out["status"].tolist() == ["Provável", "Suspenso"]


def test_map_status_handles_missing_column():
    df = pd.DataFrame({"id_atleta": [1]})
    out = player.map_status(df)
    assert "status" in out.columns
    assert out["status"].isna().all()


def test_fill_missing_slug_uses_compute_slug():
    df = pd.DataFrame({"apelido": ["Yago Pikachu", "Foo"], "slug": [None, "foo-existing"]})
    out = player.fill_missing_slug(df)
    assert out["slug"].tolist() == ["yago-pikachu", "foo-existing"]


def test_fill_missing_slug_creates_column_if_missing():
    df = pd.DataFrame({"apelido": ["Foo Bar"]})
    out = player.fill_missing_slug(df)
    assert out["slug"].iloc[0] == "foo-bar"


def test_dedupe_per_rodada_keeps_richest_scout_row():
    """2020 round 10 ships ~47 atletas twice in the SAME file: one row
    with NaN scouts and one with the actual values. Keep the populated
    one so disaccumulation downstream stays correct."""
    df = pd.DataFrame(
        {
            "rodada": [10, 10, 11],
            "id_atleta": [38133, 38133, 38133],
            "G": [pd.NA, 17, 0],
            "DS": [pd.NA, 0, 1],
            "num_jogos": [1, 1, 2],
        }
    )
    out = player.dedupe_per_rodada(df)
    keep = out[out["rodada"] == 10].iloc[0]
    assert int(keep["G"]) == 17
    assert len(out) == 2


def test_dedupe_per_rodada_no_duplicates_passes_through():
    df = pd.DataFrame({"rodada": [1, 2], "id_atleta": [10, 20], "G": [0, 1]})
    out = player.dedupe_per_rodada(df)
    assert len(out) == 2


def test_dedupe_per_rodada_handles_missing_columns_gracefully():
    df = pd.DataFrame({"foo": [1, 2]})
    out = player.dedupe_per_rodada(df)
    assert len(out) == 2


def test_compute_slug_strips_accents_and_lowercases():
    assert player.compute_slug("Éverton Ribeiro") == "everton-ribeiro"


def test_coerce_with_map_returns_na_for_none_value():
    """Direct check of the helper's None branch (player.py line 30)."""
    out = player._coerce_with_map(None, {1: "x"}, {"x"})
    assert out is pd.NA


def test_coerce_with_map_returns_na_for_non_castable_string():
    """Numeric cast failure path: a non-numeric string that is not a known label."""
    out = player._coerce_with_map("not-a-number", {1: "x"}, {"x"})
    assert out is pd.NA


def test_coerce_with_map_returns_na_for_non_int_castable_object():
    """Hit the outer try/except (lines 41-42): non-string, non-None value
    whose ``int()`` cast raises (e.g. ``pd.NA``, an arbitrary object)."""
    assert player._coerce_with_map(pd.NA, {1: "x"}, {"x"}) is pd.NA
    assert player._coerce_with_map([1, 2], {1: "x"}, {"x"}) is pd.NA


def test_map_position_handles_none_cell():
    df = pd.DataFrame({"posicao": [None, 1]})
    out = player.map_position(df)
    assert pd.isna(out["posicao"].iloc[0])
    assert out["posicao"].iloc[1] == "gol"


def test_dedupe_per_rodada_with_no_scout_columns_uses_zero_filled_marker():
    """Hit the ``else: df['_dedupe_scout_filled'] = 0`` branch (line 138)."""
    df = pd.DataFrame(
        {
            "rodada": [1, 1],
            "id_atleta": [10, 10],
            "num_jogos": [1, 2],
        }
    )
    out = player.dedupe_per_rodada(df)
    assert len(out) == 1
    assert out["num_jogos"].iloc[0] == 2


def test_dedupe_per_rodada_uses_pontuacao_as_tiebreaker():
    """Hit the ``if 'pontuacao' in df.columns`` branch (line 144)."""
    df = pd.DataFrame(
        {
            "rodada": [1, 1],
            "id_atleta": [10, 10],
            "pontuacao": [1.0, 9.0],
        }
    )
    out = player.dedupe_per_rodada(df)
    assert len(out) == 1
    assert out["pontuacao"].iloc[0] == 9.0
