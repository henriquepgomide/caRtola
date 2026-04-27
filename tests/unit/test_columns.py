"""Tests for column renaming (raw → canonical)."""

import pandas as pd

from cartola.aggregation import columns


def test_rename_columns_legacy_2014():
    raw = pd.DataFrame(
        {
            "AtletaID": [1],
            "Apelido": ["Foo"],
            "ClubeID": [262],
            "Rodada": [1],
            "Pontos": [10.0],
        }
    )
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta", "apelido", "id_clube", "rodada", "pontuacao"]


def test_rename_columns_modern_atletas_prefix():
    raw = pd.DataFrame(
        {
            "atletas.atleta_id": [1],
            "atletas.apelido": ["Foo"],
            "atletas.clube.id.full.name": ["Flamengo"],
            "atletas.clube_id": ["FLA"],
            "atletas.rodada_id": [1],
            "atletas.pontos_num": [10.0],
            "atletas.posicao_id": ["mei"],
            "atletas.status_id": ["Provável"],
        }
    )
    out = columns.rename_columns(raw)
    expected = {
        "id_atleta",
        "apelido",
        "nome_clube",
        "id_clube",
        "rodada",
        "pontuacao",
        "posicao",
        "status",
    }
    assert set(out.columns) == expected


def test_rename_columns_drops_known_noise_columns():
    raw = pd.DataFrame(
        {
            "AtletaID": [1],
            "Participou": [1],
            "athletes.atletas.scout": ["{}"],
            "atletas.minimo_para_valorizar": [1.0],
            "atletas.entrou_em_campo": [True],
        }
    )
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta"]


def test_rename_columns_preserves_unknown_scouts():
    raw = pd.DataFrame({"AtletaID": [1], "G": [0.0], "PE": [0.0], "DD": [0.0]})
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta", "G", "PE", "DD"]


def test_rename_columns_drops_empty_index_column():
    raw = pd.DataFrame({"": [0], "AtletaID": [1]})
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta"]
