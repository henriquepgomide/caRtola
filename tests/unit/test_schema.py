"""Tests for the canonical schema constants and helpers."""

import numpy as np
import pandas as pd

from cartola.aggregation import schema
from cartola.aggregation.schema import CANONICAL_COLUMNS, DTYPES, SCOUTS, apply_canonical_dtypes


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


def test_apply_canonical_dtypes_casts_present_columns():
    df = pd.DataFrame(
        {
            "ano": [2024],
            "rodada": [1],
            "pontuacao": [5.0],
            "apelido": ["Foo"],
        }
    )
    out = apply_canonical_dtypes(df)
    assert str(out["ano"].dtype) == "int16"
    assert str(out["rodada"].dtype) == "int8"
    assert str(out["pontuacao"].dtype) == "float64"
    assert str(out["apelido"].dtype) == "string"


def test_apply_canonical_dtypes_skips_absent_columns():
    df = pd.DataFrame({"ano": [2024]})
    out = apply_canonical_dtypes(df)
    assert list(out.columns) == ["ano"]
    assert str(out["ano"].dtype) == "int16"


def test_apply_canonical_dtypes_handles_pd_na_in_float_column():
    """Regression: ``scouts.process`` writes ``pd.NA`` to scout columns when
    ``has_scouts=False``; those columns must coerce to ``float64`` cleanly,
    not raise ``TypeError`` on ``astype``."""
    df = pd.DataFrame({c: pd.Series([pd.NA, pd.NA], dtype="object") for c in SCOUTS})
    out = apply_canonical_dtypes(df)
    for col in SCOUTS:
        assert str(out[col].dtype) == "float64"
        assert out[col].isna().all()


def test_apply_canonical_dtypes_handles_reindexed_empty_columns():
    """After ``df.reindex(columns=CANONICAL_COLUMNS)`` missing cols are
    float64-NaN; the helper must turn them into the declared dtype without
    raising even when no values are present."""
    df = pd.DataFrame().reindex(columns=CANONICAL_COLUMNS)
    out = apply_canonical_dtypes(df)
    for col, dtype in DTYPES.items():
        assert str(out[col].dtype) == dtype, f"{col}: got {out[col].dtype}, want {dtype}"


def test_apply_canonical_dtypes_returns_a_copy():
    df = pd.DataFrame({"ano": [2024]})
    out = apply_canonical_dtypes(df)
    assert out is not df
    assert str(df["ano"].dtype) == "int64"
    assert str(out["ano"].dtype) == "int16"


def test_apply_canonical_dtypes_coerces_unparseable_floats_to_nan():
    """``pd.to_numeric(errors="coerce")`` is used for non-nullable numerics:
    junk strings become NaN rather than raising."""
    df = pd.DataFrame({"pontuacao": ["abc", "5.5"]})
    out = apply_canonical_dtypes(df)
    assert str(out["pontuacao"].dtype) == "float64"
    assert np.isnan(out["pontuacao"].iloc[0])
    assert out["pontuacao"].iloc[1] == 5.5
