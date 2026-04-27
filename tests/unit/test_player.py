"""Tests for player-entity transformations."""

import pandas as pd

from cartola.aggregation import player


def test_map_position_int_id_to_label():
    df = pd.DataFrame({"posicao": [1, 5]})
    out = player.map_position(df)
    assert out["posicao"].tolist() == ["gol", "ata"]


def test_map_position_passes_through_existing_labels():
    # 2017–2022 already store the label string.
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
