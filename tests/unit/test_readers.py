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


def test_read_csv_robust_recovers_from_oserror(tmp_path, mocker):
    """If the rb-sample probe raises OSError, fall back to a plain read_csv."""
    csv = tmp_path / "x.csv"
    csv.write_text("a,b\n1,2\n", encoding="utf-8")

    real_open = csv.open

    def fake_open(self, *args, **kwargs):
        if args and args[0] == "rb":
            raise OSError("simulated probe failure")
        return real_open(*args, **kwargs)

    mocker.patch.object(type(csv), "open", autospec=True, side_effect=fake_open)
    df = readers._read_csv_robust(csv)
    assert df["a"].iloc[0] == 1


def test_read_csv_robust_repairs_double_encoded_utf8(tmp_path):
    """Synthesize a mojibake file (legit UTF-8 → encoded as latin-1 → encoded as UTF-8)."""
    csv = tmp_path / "mojibake.csv"
    correct = "nome\nSão Paulo\n"
    mojibake_bytes = correct.encode("utf-8").decode("latin-1").encode("utf-8")
    csv.write_bytes(mojibake_bytes)
    df = readers._read_csv_robust(csv)
    assert df["nome"].iloc[0] == "São Paulo"


def test_read_csv_robust_unrepairable_mojibake_falls_through(tmp_path, caplog, mocker):
    """If the repair step itself errors, log a warning and read the file as-is."""
    csv = tmp_path / "x.csv"
    csv.write_bytes(b"a\n1\n")
    mocker.patch.object(readers, "_MOJIBAKE_SIGNATURE", b"a")
    mocker.patch.object(readers.Path, "read_bytes", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "x"))
    with caplog.at_level("WARNING"):
        df = readers._read_csv_robust(csv)
    assert df["a"].iloc[0] == 1
    assert any("Mojibake repair failed" in record.message for record in caplog.records)


def test_read_csv_robust_falls_back_to_latin1(tmp_path, caplog):
    """Genuine latin-1 file → first read raises UnicodeDecodeError; second succeeds."""
    csv = tmp_path / "latin1.csv"
    csv.write_bytes("nome\ncoração\n".encode("latin-1"))
    with caplog.at_level("WARNING"):
        df = readers._read_csv_robust(csv)
    assert df["nome"].iloc[0] == "coração"
    assert any("falling back to latin-1" in record.message for record in caplog.records)


def test_read_round_files_warns_when_dir_missing(tmp_path, caplog):
    missing = tmp_path / "does-not-exist"
    with caplog.at_level("WARNING"):
        df = readers.read_round_files(str(missing), year=2099)
    assert df.empty
    assert any("Raw dir does not exist" in record.message for record in caplog.records)


def test_read_round_files_returns_empty_when_only_rodada_zero(tmp_path):
    """Only file is ``rodada-0.csv`` (preseason) → skipped → empty DataFrame."""
    cols = ["atletas.atleta_id", "atletas.rodada_id", "G"]
    (tmp_path / "rodada-0.csv").write_text("\n".join([",".join(cols), "100,1,0"]))
    df = readers.read_round_files(str(tmp_path), year=2099)
    assert df.empty


def test_read_mercado_json_warns_when_dir_missing(tmp_path, caplog):
    missing = tmp_path / "does-not-exist"
    with caplog.at_level("WARNING"):
        df = readers.read_mercado_json(str(missing), year=2021)
    assert df.empty
    assert any("Raw dir does not exist" in record.message for record in caplog.records)


def test_read_mercado_json_returns_empty_when_only_preseason_present(tmp_path):
    """Only file is ``Mercado_1.txt`` (preseason; idx<2) → skipped → empty DataFrame."""
    payload = '{"atletas": [], "clubes": {}}'
    (tmp_path / "Mercado_1.txt").write_text(payload, encoding="utf-8")
    df = readers.read_mercado_json(str(tmp_path), year=2021)
    assert df.empty


def test_read_mercado_json_falls_back_to_latin1(tmp_path):
    """A latin-1 encoded ``Mercado_*.txt`` → utf-8 decode raises → retry as latin-1."""
    payload = {
        "atletas": [
            {"atleta_id": 1, "clube_id": 262, "rodada_id": 5, "scout": {"G": 1}},
        ],
        "clubes": {"262": {"id": 262, "nome": "São Paulo"}},
    }
    import json as _json

    text = _json.dumps(payload, ensure_ascii=False)
    (tmp_path / "Mercado_2.txt").write_bytes(text.encode("latin-1"))
    df = readers.read_mercado_json(str(tmp_path), year=2021)
    assert len(df) == 1
    assert df["G"].iloc[0] == 1
