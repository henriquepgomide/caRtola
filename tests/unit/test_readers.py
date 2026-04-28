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


def test_read_mercado_json_2021_skips_preseason_and_assigns_rodada(fixtures_dir):
    """Mercado_1 is the preseason snapshot; Mercado_N (N>=2) carries cumulative
    stats for round N-1. The reader must skip Mercado_1 and label every row
    with `rodada = N - 1`."""
    df = readers.read_mercado_json(str(fixtures_dir / "2021"), year=2021)
    # Mercado_2 (rodada=1) → 2 atletas; Mercado_3 (rodada=2) → 2 atletas; preseason skipped.
    assert len(df) == 4
    assert sorted(df["rodada_id"].unique()) == [1, 2]


def test_read_mercado_json_2021_flattens_scouts_and_resolves_team_name(fixtures_dir):
    df = readers.read_mercado_json(str(fixtures_dir / "2021"), year=2021)
    hulk = df[df["atleta_id"] == 2002].sort_values("rodada_id")
    # nested `scout: {"G": ...}` is flattened into top-level columns
    assert list(hulk["G"]) == [1, 2]
    assert list(hulk["FF"]) == [2, 3]
    # nome_clube is hydrated from the `clubes` lookup so resolve_id_clube works
    assert (hulk["atletas.clube.id.full.name"] == "Atlético-MG").all()


def test_read_mercado_json_handles_empty_dir(tmp_path):
    df = readers.read_mercado_json(str(tmp_path), year=2021)
    assert df.empty


def test_read_round_files_overwrites_rodada_from_filename(tmp_path):
    """2023's `rodada-1.csv` and `rodada-2.csv` BOTH carry an internal
    `atletas.rodada_id=2` (the upstream snapshot field is stale) — the
    file name is the source of truth for "which round did we just see"."""
    cols = ["atletas.atleta_id", "atletas.rodada_id", "G"]
    (tmp_path / "rodada-1.csv").write_text("\n".join([",".join(cols), "100,2,0", "200,2,0"]))
    (tmp_path / "rodada-2.csv").write_text("\n".join([",".join(cols), "100,2,1", "200,2,2"]))
    df = readers.read_round_files(str(tmp_path), year=2099)
    assert sorted(df["atletas.rodada_id"].unique()) == [1, 2]


def test_read_round_files_skips_rodada_zero(tmp_path):
    """2022 ships a `rodada-0.csv` preseason snapshot whose internal
    rodada_id is 1, duplicating every player in `rodada-1.csv`. Drop it."""
    cols = ["atletas.atleta_id", "atletas.rodada_id", "G"]
    (tmp_path / "rodada-0.csv").write_text("\n".join([",".join(cols), "100,1,0"]))
    (tmp_path / "rodada-1.csv").write_text("\n".join([",".join(cols), "100,1,5"]))
    df = readers.read_round_files(str(tmp_path), year=2099)
    assert len(df) == 1
    assert df["atletas.rodada_id"].iloc[0] == 1
    assert df["G"].iloc[0] == 5
