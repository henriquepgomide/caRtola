"""Tests for the Hamilton driver wrapper."""

import logging
import sys
import types

import pandas as pd
import pytest

from cartola.aggregation import driver
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS


def test_build_driver_default_no_tracker():
    drv = driver.build_driver(track=False)
    assert {n.name for n in drv.list_available_variables()} >= {f"year_{y}" for y in YEAR_REGISTRY}


def test_build_driver_track_logs_warning_when_ui_missing(monkeypatch, caplog):
    """Without ``sf-hamilton-ui`` installed, ``track=True`` falls back gracefully."""
    monkeypatch.setitem(sys.modules, "hamilton_sdk", None)
    with caplog.at_level(logging.WARNING):
        drv = driver.build_driver(track=True)
    assert drv is not None
    assert any("Hamilton UI not installed" in record.message for record in caplog.records)


def test_build_driver_track_attaches_tracker_when_ui_available(monkeypatch):
    """Stub a fake ``hamilton_sdk.adapters`` and verify the tracker is wired in."""
    fake_module = types.ModuleType("hamilton_sdk")
    fake_adapters = types.ModuleType("hamilton_sdk.adapters")

    class _FakeTracker:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def pre_graph_construct(self, *args, **kwargs):
            return None

        def post_graph_construct(self, *args, **kwargs):
            return None

        def pre_graph_execute(self, *args, **kwargs):
            return None

        def post_graph_execute(self, *args, **kwargs):
            return None

        def pre_node_execute(self, *args, **kwargs):
            return None

        def post_node_execute(self, *args, **kwargs):
            return None

        def run_after_graph_construction(self, *args, **kwargs):
            return None

        def run_before_node_execution(self, *args, **kwargs):
            return None

        def run_after_node_execution(self, *args, **kwargs):
            return None

        def run_before_graph_execution(self, *args, **kwargs):
            return None

        def run_after_graph_execution(self, *args, **kwargs):
            return None

    fake_adapters.HamiltonTracker = _FakeTracker
    fake_module.adapters = fake_adapters
    monkeypatch.setitem(sys.modules, "hamilton_sdk", fake_module)
    monkeypatch.setitem(sys.modules, "hamilton_sdk.adapters", fake_adapters)

    drv = driver.build_driver(track=True)
    assert drv is not None


def _stub_drv(per_year_frames: dict[str, pd.DataFrame], aggregated_df: pd.DataFrame | None = None):
    """Build a stub driver that returns the supplied per-year frames."""

    class _Stub:
        def execute(self, names):
            if names == ["aggregated"]:
                return {"aggregated": aggregated_df}
            return {n: per_year_frames[n] for n in names}

    return _Stub()


def test_run_full_writes_per_year_and_aggregated(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")

    per_year = {f"year_{y}": pd.DataFrame({"ano": [y]}) for y in YEAR_REGISTRY}
    aggregated_df = pd.concat(per_year.values(), ignore_index=True)
    monkeypatch.setattr(driver, "build_driver", lambda track=False: _stub_drv(per_year, aggregated_df))

    out = driver.run(years=None, track=False)
    assert out is aggregated_df
    for y in YEAR_REGISTRY:
        assert (tmp_path / "primary" / f"cartola_{y}.csv").exists()
    available = sorted(YEAR_REGISTRY)
    assert (tmp_path / "aggregated" / f"cartola_{available[0]}_{available[-1]}.csv").exists()


def test_run_partial_skips_aggregated(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")

    selected = [2018, 2019]
    per_year = {f"year_{y}": pd.DataFrame({"ano": [y]}) for y in selected}
    monkeypatch.setattr(driver, "build_driver", lambda track=False: _stub_drv(per_year))

    out = driver.run(years=selected)
    assert sorted(out["ano"].unique()) == selected
    assert (tmp_path / "primary" / "cartola_2018.csv").exists()
    assert not (tmp_path / "aggregated").exists()


def test_run_rejects_unknown_years(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    with pytest.raises(ValueError, match="Years not in YEAR_REGISTRY"):
        driver.run(years=[1990])


def test_launch_ui_raises_when_hamilton_ui_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "hamilton_ui", None)
    with pytest.raises(SystemExit, match="Hamilton UI is not installed"):
        driver.launch_ui()


def test_launch_ui_invokes_commands_run_with_defaults(monkeypatch, tmp_path):
    """Stub ``hamilton_ui.commands`` and verify the wrapper forwards args."""
    captured: dict = {}

    def fake_run(*, port, base_dir, no_migration, no_open, settings_file, config_file):
        captured.update(
            port=port,
            base_dir=base_dir,
            no_migration=no_migration,
            no_open=no_open,
            settings_file=settings_file,
            config_file=config_file,
        )

    fake_module = types.ModuleType("hamilton_ui")
    fake_module.commands = types.SimpleNamespace(run=fake_run)
    monkeypatch.setitem(sys.modules, "hamilton_ui", fake_module)

    fake_dir = tmp_path / "h"
    driver.launch_ui(port=9999, base_dir=fake_dir, no_migration=True, no_open=True)

    assert captured["port"] == 9999
    assert captured["base_dir"] == str(fake_dir)
    assert captured["no_migration"] is True
    assert captured["no_open"] is True
    assert captured["settings_file"] == "mini"
    assert captured["config_file"] is None


def test_run_full_writes_canonical_columns(monkeypatch, tmp_path):
    """Sanity-check the round-trip schema of the aggregated CSV."""
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "primary")
    monkeypatch.setattr(driver, "AGGREGATED_DIR", tmp_path / "aggregated")
    per_year = {f"year_{y}": pd.DataFrame(columns=CANONICAL_COLUMNS) for y in YEAR_REGISTRY}
    aggregated_df = pd.DataFrame(columns=CANONICAL_COLUMNS)
    monkeypatch.setattr(driver, "build_driver", lambda track=False: _stub_drv(per_year, aggregated_df))
    driver.run(years=None)
    available = sorted(YEAR_REGISTRY)
    out = pd.read_csv(tmp_path / "aggregated" / f"cartola_{available[0]}_{available[-1]}.csv")
    assert list(out.columns) == CANONICAL_COLUMNS
