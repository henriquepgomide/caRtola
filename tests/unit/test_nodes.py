"""Tests for the Hamilton nodes module."""

import inspect

import pandas as pd
from hamilton import driver

from cartola.aggregation import nodes
from cartola.aggregation.catalog import YEAR_REGISTRY
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
