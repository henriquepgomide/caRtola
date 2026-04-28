"""Tests for the Hamilton nodes module."""

import inspect

import pandas as pd
from hamilton import driver

from cartola.aggregation import nodes
from cartola.aggregation.catalog import YEAR_REGISTRY, YearConfig
from cartola.aggregation.schema import CANONICAL_COLUMNS


def test_module_exposes_year_dataframe_and_aggregated():
    assert "year_dataframe" in dir(nodes)
    assert "aggregated" in dir(nodes)


def test_aggregated_signature_matches_registry():
    sig = inspect.signature(nodes.aggregated)
    expected = {f"year_{y}" for y in YEAR_REGISTRY}
    assert set(sig.parameters) == expected


def test_driver_dag_has_one_node_per_year_plus_aggregated():
    """@parameterize materializes year_<Y> nodes only at driver-build time."""
    drv = driver.Builder().with_modules(nodes).build()
    node_names = {n.name for n in drv.list_available_variables()}
    expected_years = {f"year_{y}" for y in YEAR_REGISTRY}
    assert expected_years.issubset(node_names)
    assert "aggregated" in node_names


def test_aggregated_concats_input_frames():
    df_a = pd.DataFrame({c: pd.Series(dtype="object") for c in CANONICAL_COLUMNS})
    kwargs = {f"year_{y}": df_a for y in YEAR_REGISTRY}
    out = nodes.aggregated(**kwargs)
    assert list(out.columns) == CANONICAL_COLUMNS
    assert len(out) == 0


def test_aggregated_returns_empty_canonical_when_all_inputs_empty():
    """When every per-year frame is empty (no columns), short-circuit to an
    empty canonical DataFrame instead of concatenating zero non-empty frames."""
    empty = pd.DataFrame()
    kwargs = {f"year_{y}": empty for y in YEAR_REGISTRY}
    out = nodes.aggregated(**kwargs)
    assert list(out.columns) == CANONICAL_COLUMNS
    assert len(out) == 0


def test_aggregated_concats_only_non_empty_frames():
    populated = pd.DataFrame(
        {c: ([2018] if c == "ano" else [pd.NA]) for c in CANONICAL_COLUMNS},
    )
    empty = pd.DataFrame()
    kwargs = {f"year_{y}": (populated if y == 2018 else empty) for y in YEAR_REGISTRY}
    out = nodes.aggregated(**kwargs)
    assert len(out) == 1
    assert int(out["ano"].iloc[0]) == 2018


def test_year_dataframe_runs_full_pipeline_through_a_fixture(monkeypatch, fixtures_dir):
    """Patch a single ``YEAR_REGISTRY`` entry to point at a fixture and call
    ``year_dataframe`` directly to exercise its body (lines 31-41)."""
    from cartola.aggregation import readers

    fixture_cfg = YearConfig(
        year=2014,
        raw_dir=str(fixtures_dir / "2014"),
        reader=readers.read_season_files,
        accumulated=False,
    )
    monkeypatch.setitem(nodes.YEAR_REGISTRY, 2014, fixture_cfg)
    out = nodes.year_dataframe(year=2014)
    assert list(out.columns) == CANONICAL_COLUMNS
    assert (out["ano"] == 2014).all()
    assert len(out) == 4
