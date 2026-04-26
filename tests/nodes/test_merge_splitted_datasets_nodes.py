"""Tests for the 2014-2016 split-source merge node."""

import pandas as pd

from cartola.pipelines.merge_splitted_datasets.nodes import merge_datasets


def _make_inputs(*, with_posicao: bool):
    df_scouts = pd.DataFrame(
        {
            "AtletaID": [1, 2],
            "ClubeID": [10, 20],
            "rodada": [1, 1],
            "G": [0, 1],
            **({"Posicao": ["gol", "ata"]} if with_posicao else {}),
        },
    )
    df_players = pd.DataFrame(
        {
            "ID": [1, 2],
            "ClubeID": [99, 99],  # ClubeID on players is dropped before the join.
            "Nome": ["Alice", "Bob"],
        },
    )
    df_teams = pd.DataFrame(
        {
            "ID": [10, 20],
            "Abreviacao": ["FLA", "PAL"],
            "Slug": ["flamengo", "palmeiras"],
            "Nome": ["Flamengo", "Palmeiras"],
        },
    )
    return df_scouts, df_players, df_teams


def test_merge_datasets_returns_concat_key_with_dataframe():
    """The node returns a single-key dict so the Kedro PartitionedDataset
    writer recognises it as one partition named 'concat'."""
    df_scouts, df_players, df_teams = _make_inputs(with_posicao=False)
    out = merge_datasets(df_scouts, df_players, df_teams)
    assert set(out.keys()) == {"concat"}
    assert isinstance(out["concat"], pd.DataFrame)


def test_merge_datasets_drops_helper_id_and_slug_columns():
    """ID_x/ID_y arise from the two left-merges colliding on 'ID'; Slug
    is teams-only metadata not needed downstream. All three are dropped."""
    df_scouts, df_players, df_teams = _make_inputs(with_posicao=False)
    out = merge_datasets(df_scouts, df_players, df_teams)["concat"]
    assert "ID_x" not in out.columns
    assert "ID_y" not in out.columns
    assert "Slug" not in out.columns
    assert "Abreviacao" not in out.columns


def test_merge_datasets_joins_player_and_team_metadata():
    df_scouts, df_players, df_teams = _make_inputs(with_posicao=False)
    out = merge_datasets(df_scouts, df_players, df_teams)["concat"]
    assert len(out) == 2
    assert "Nome_x" in out.columns or "Nome" in out.columns
    by_atleta = out.set_index("AtletaID")
    nome_col = "Nome_x" if "Nome_x" in out.columns else "Nome"
    assert by_atleta.loc[1, nome_col] == "Alice"
    assert by_atleta.loc[2, nome_col] == "Bob"


def test_merge_datasets_drops_posicao_from_scouts_when_present():
    """In some 2014-2016 splits, scouts already carry 'Posicao' (and the
    canonical source is the players file). Drop the scouts copy to avoid
    a Posicao_x/Posicao_y suffix collision after the merge."""
    df_scouts, df_players, df_teams = _make_inputs(with_posicao=True)
    out = merge_datasets(df_scouts, df_players, df_teams)["concat"]
    assert "Posicao" not in out.columns
    assert "Posicao_x" not in out.columns
    assert "Posicao_y" not in out.columns


def test_merge_datasets_keeps_scouts_unchanged_when_no_posicao_column():
    df_scouts, df_players, df_teams = _make_inputs(with_posicao=False)
    out = merge_datasets(df_scouts, df_players, df_teams)["concat"]
    assert "G" in out.columns
    assert out["G"].tolist() == [0, 1]
