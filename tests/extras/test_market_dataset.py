"""Tests for the custom 2021 market JSON Kedro dataset."""

import json
from pathlib import PurePosixPath

import pandas as pd
import pytest

from cartola.extras.datasets.market_dataset import MarketDataset


SAMPLE_PAYLOAD = {
    "atletas": [
        {
            "id": 1,
            "apelido": "Alpha",
            "scout": {"G": 1, "A": 0, "CA": 0},
        },
        {
            "id": 2,
            "apelido": "Beta",
            "scout": {"G": 0, "A": 2, "CA": 1},
        },
    ],
}


@pytest.fixture
def market_json(tmp_path):
    """Write the sample market JSON in latin-1 (Cartola's wire encoding)."""
    path = tmp_path / "market.json"
    path.write_text(json.dumps(SAMPLE_PAYLOAD), encoding="latin-1")
    return path


def test_init_extracts_local_protocol_and_path(tmp_path):
    """A bare local path should resolve to the 'file' protocol with the
    same path stripped of the protocol prefix."""
    fp = str(tmp_path / "x.json")
    ds = MarketDataset(fp)
    assert ds._protocol == "file"
    assert isinstance(ds._filepath, PurePosixPath)
    assert ds._filepath.name == "x.json"


def test_load_flattens_scout_dict_into_columns(market_json):
    """The raw payload nests scouts under 'scout'; load() must promote each
    scout key (G, A, CA, ...) to a top-level column and drop 'scout'."""
    ds = MarketDataset(str(market_json))
    df = ds.load()
    assert "scout" not in df.columns
    for col in ("id", "apelido", "G", "A", "CA"):
        assert col in df.columns


def test_load_preserves_atleta_rows(market_json):
    ds = MarketDataset(str(market_json))
    df = ds.load()
    assert len(df) == 2
    by_id = df.set_index("id").sort_index()
    assert by_id.loc[1, "apelido"] == "Alpha"
    assert by_id.loc[2, "apelido"] == "Beta"
    assert by_id.loc[1, "G"] == 1
    assert by_id.loc[2, "A"] == 2


def test_load_uses_latin_1_encoding_for_accented_text(tmp_path):
    """Cartola's market dumps are latin-1 encoded; UTF-8 decoding would
    crash on bytes like 0xE3 (ã). Ensure load() reads them correctly."""
    payload = {
        "atletas": [
            {"id": 1, "apelido": "João", "scout": {"G": 0}},
        ],
    }
    path = tmp_path / "accented.json"
    path.write_bytes(json.dumps(payload, ensure_ascii=False).encode("latin-1"))
    df = MarketDataset(str(path)).load()
    assert df.iloc[0]["apelido"] == "João"


def test_save_writes_dataframe_as_csv(tmp_path):
    save_path = tmp_path / "out.csv"
    ds = MarketDataset(str(save_path))
    df = pd.DataFrame({"id": [1, 2], "apelido": ["A", "B"], "G": [0, 1]})
    ds.save(df)
    assert save_path.exists()
    loaded = pd.read_csv(save_path)
    assert list(loaded.columns) == ["id", "apelido", "G"]
    assert len(loaded) == 2


def test_save_omits_pandas_index(tmp_path):
    """Index column would otherwise leak into the CSV as 'Unnamed: 0' on
    re-read; the dataset writes index=False to avoid it."""
    save_path = tmp_path / "out.csv"
    ds = MarketDataset(str(save_path))
    df = pd.DataFrame({"a": [1, 2]}, index=[100, 200])
    ds.save(df)
    loaded = pd.read_csv(save_path)
    assert list(loaded.columns) == ["a"]


def test_describe_returns_filepath_and_protocol(tmp_path):
    fp = str(tmp_path / "x.json")
    ds = MarketDataset(fp)
    d = ds._describe()
    assert set(d.keys()) == {"filepath", "protocol"}
    assert d["protocol"] == "file"
    assert isinstance(d["filepath"], PurePosixPath)


def test_load_then_save_roundtrip(market_json, tmp_path):
    """The flattened load() output should be CSV-roundtrippable through
    save(), preserving the scout columns the pipeline depends on."""
    loaded = MarketDataset(str(market_json)).load()
    out_path = tmp_path / "roundtrip.csv"
    MarketDataset(str(out_path)).save(loaded)
    reread = pd.read_csv(out_path)
    assert set(reread.columns) >= {"id", "apelido", "G", "A", "CA"}
    assert len(reread) == len(loaded)
