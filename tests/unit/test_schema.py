"""Tests for the canonical schema constants."""

from cartola.aggregation import schema


def test_canonical_columns_count_is_38():
    assert len(schema.CANONICAL_COLUMNS) == 38


def test_canonical_columns_start_with_context_block():
    assert schema.CANONICAL_COLUMNS[:5] == [
        "ano",
        "rodada",
        "id_clube",
        "nome_clube",
        "id_atleta",
    ]


def test_scouts_count_is_21():
    assert len(schema.SCOUTS) == 21


def test_scouts_set_matches_expected():
    expected = {
        "A",
        "CA",
        "CV",
        "DE",
        "DP",
        "DS",
        "FC",
        "FD",
        "FF",
        "FS",
        "FT",
        "G",
        "GC",
        "GS",
        "I",
        "PC",
        "PI",
        "PP",
        "PS",
        "SG",
        "V",
    }
    assert set(schema.SCOUTS) == expected


def test_position_map_includes_all_six_labels():
    assert set(schema.POSITION_MAP.values()) == {"gol", "lat", "zag", "mei", "ata", "tec"}


def test_status_map_matches_kedro_legacy():
    assert schema.STATUS_MAP[7] == "Provável"
    assert schema.STATUS_MAP[5] == "Contundido"
    assert schema.STATUS_MAP[6] == "Nulo"


def test_dtypes_includes_all_canonical_columns():
    missing = set(schema.CANONICAL_COLUMNS) - set(schema.DTYPES)
    assert missing == set(), f"DTYPES missing: {missing}"
