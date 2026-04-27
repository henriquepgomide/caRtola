"""Tests for the three raw-shape readers."""

from cartola.aggregation import readers


def test_read_season_files_2014_merges_jogadores_scouts_times(fixtures_dir):
    df = readers.read_season_files(str(fixtures_dir / "2014"), year=2014)
    # 4 rows in 2014_scouts_raw.csv → 4 rows after merge
    assert len(df) == 4
    # nome_clube comes from the times-file merge ("Nome" column)
    assert "nome_clube" in df.columns or "Nome" in df.columns
    # Apelido from jogadores merge
    assert "Apelido" in df.columns or "apelido" in df.columns


def test_read_season_files_2014_brings_scout_columns(fixtures_dir):
    df = readers.read_season_files(str(fixtures_dir / "2014"), year=2014)
    # legacy scout names should be present pre-rename
    assert {"FS", "PE", "G", "RB", "DD", "SG"}.issubset(df.columns)


def test_read_monolithic_2017(fixtures_dir):
    df = readers.read_monolithic(str(fixtures_dir / "2017"), year=2017)
    assert len(df) == 2
    assert "atletas.atleta_id" in df.columns
    assert "Rodada" in df.columns


def test_read_round_files_2018_concats_all_rounds(fixtures_dir):
    df = readers.read_round_files(str(fixtures_dir / "2018"), year=2018)
    # rodada-1 + rodada-2 → 2 rows
    assert len(df) == 2
    assert set(df["atletas.rodada_id"].unique()) == {1, 2}


def test_read_round_files_handles_missing_dir(tmp_path):
    """Empty year directory → empty DataFrame, not an error."""
    empty = tmp_path / "empty_year"
    empty.mkdir()
    df = readers.read_round_files(str(empty), year=2099)
    assert df.empty
