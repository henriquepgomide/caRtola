"""Tests for the Hamilton driver wrapper."""

import pandas as pd
import pytest

from cartola.aggregation import driver
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS


def test_build_driver_default():
    drv = driver.build_driver()
    assert {n.name for n in drv.list_available_variables()} >= {f"year_{y}" for y in YEAR_REGISTRY}


def _stub_drv(
    per_year_frames: dict[str, pd.DataFrame],
    aggregated_df: pd.DataFrame | None = None,
    execute_calls: list[list[str]] | None = None,
):
    """Build a stub driver that returns the supplied per-year frames.

    On a full run, ``driver.run`` requests ``[*per_year, "aggregated"]`` in a
    single ``execute`` call (no separate aggregated-only call). On a partial
    run, only per-year names are requested. The stub handles both shapes.
    """

    class _Stub:
        def execute(self, names):
            if execute_calls is not None:
                execute_calls.append(list(names))
            return {n: (aggregated_df if n == "aggregated" else per_year_frames[n]) for n in names}

    return _Stub()


def _build_valid_aggregated_df():
    """Single-row aggregated DataFrame matching :class:`AggregatedSchema`."""
    from cartola.aggregation.schema import CANONICAL_COLUMNS, SCOUTS

    row = dict.fromkeys(CANONICAL_COLUMNS, pd.NA)
    row.update(
        {
            "ano": 2024,
            "rodada": 1,
            "id_clube": 262,
            "nome_clube": "Flamengo",
            "id_atleta": 1,
            "apelido": "Foo",
            "slug": "foo",
            "posicao": "mei",
            "pontuacao": 5.0,
            "media": 5.0,
            "preco": 8.0,
            "variacao": 0.0,
        }
    )
    for col in SCOUTS:
        row[col] = 0.0
    df = pd.DataFrame([row], columns=CANONICAL_COLUMNS)
    df["ano"] = df["ano"].astype("int64")
    df["rodada"] = df["rodada"].astype("int64")
    df["id_clube"] = df["id_clube"].astype("Int32")
    df["id_atleta"] = df["id_atleta"].astype("int64")
    df["num_jogos"] = df["num_jogos"].astype("Int16")
    for col in ("nome_clube", "nome", "apelido", "apelido_abreviado", "slug", "foto", "posicao", "status"):
        df[col] = df[col].astype("string")
    for col in ("pontuacao", "media", "preco", "variacao", *SCOUTS):
        df[col] = df[col].astype("float64")
    return df


def test_run_full_writes_per_year_and_aggregated(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")

    per_year = {f"year_{y}": pd.DataFrame({"ano": [y]}) for y in YEAR_REGISTRY}
    aggregated_df = _build_valid_aggregated_df()
    monkeypatch.setattr(driver, "build_driver", lambda: _stub_drv(per_year, aggregated_df))

    out = driver.run(years=None)
    assert len(out) == 1
    for y in YEAR_REGISTRY:
        assert (tmp_path / "primary" / f"cartola_{y}.csv").exists()
    available = sorted(YEAR_REGISTRY)
    assert (tmp_path / "aggregated" / f"cartola_{available[0]}_{available[-1]}.csv").exists()


def test_run_full_executes_dag_once(monkeypatch, tmp_path):
    """Thread 6: full run must call drv.execute exactly once with both
    per-year outputs and ``aggregated`` in the same request."""
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")

    per_year = {f"year_{y}": pd.DataFrame({"ano": [y]}) for y in YEAR_REGISTRY}
    aggregated_df = _build_valid_aggregated_df()
    calls: list[list[str]] = []
    monkeypatch.setattr(driver, "build_driver", lambda: _stub_drv(per_year, aggregated_df, calls))

    driver.run(years=None)

    assert len(calls) == 1
    expected = [f"year_{y}" for y in sorted(YEAR_REGISTRY)] + ["aggregated"]
    assert calls[0] == expected


def test_run_aborts_on_schema_violation(monkeypatch, tmp_path):
    """Thread 2: if the aggregated DataFrame violates AggregatedSchema, the
    aggregated CSV is not written and the SchemaError propagates."""
    import pandera.pandas as pa

    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")

    per_year = {f"year_{y}": pd.DataFrame({"ano": [y]}) for y in YEAR_REGISTRY}
    bad_df = _build_valid_aggregated_df()
    bad_df.loc[0, "rodada"] = 99
    monkeypatch.setattr(driver, "build_driver", lambda: _stub_drv(per_year, bad_df))

    with pytest.raises(pa.errors.SchemaError):
        driver.run(years=None)

    available = sorted(YEAR_REGISTRY)
    assert not (tmp_path / "aggregated" / f"cartola_{available[0]}_{available[-1]}.csv").exists()


def test_run_partial_skips_aggregated(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")

    selected = [2018, 2019]
    per_year = {f"year_{y}": pd.DataFrame({"ano": [y]}) for y in selected}
    monkeypatch.setattr(driver, "build_driver", lambda: _stub_drv(per_year))

    out = driver.run(years=selected)
    assert sorted(out["ano"].unique()) == selected
    assert (tmp_path / "primary" / "cartola_2018.csv").exists()
    assert not (tmp_path / "aggregated").exists()


def test_run_rejects_unknown_years(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    with pytest.raises(ValueError, match="Years not in YEAR_REGISTRY"):
        driver.run(years=[1990])


def test_run_full_writes_canonical_columns(monkeypatch, tmp_path):
    """Sanity-check the round-trip schema of the aggregated CSV."""
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")
    per_year = {f"year_{y}": pd.DataFrame(columns=CANONICAL_COLUMNS) for y in YEAR_REGISTRY}
    aggregated_df = pd.DataFrame(columns=CANONICAL_COLUMNS)
    monkeypatch.setattr(driver, "build_driver", lambda: _stub_drv(per_year, aggregated_df))
    driver.run(years=None)
    available = sorted(YEAR_REGISTRY)
    out = pd.read_csv(tmp_path / "aggregated" / f"cartola_{available[0]}_{available[-1]}.csv")
    assert list(out.columns) == CANONICAL_COLUMNS
