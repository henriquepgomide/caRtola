"""Tests for the YEAR_REGISTRY catalog."""

import pytest

from cartola.aggregation import catalog

# 2021 is intentionally omitted: raw is JSON (`Mercado_N.txt`), needs a dedicated reader.
EXPECTED_YEARS = [y for y in range(2014, 2027) if y != 2021]


def test_registry_covers_supported_years():
    assert sorted(catalog.YEAR_REGISTRY) == EXPECTED_YEARS


def test_2021_excluded_from_registry():
    assert 2021 not in catalog.YEAR_REGISTRY


def test_accumulated_years_match_spec():
    # Years whose scout columns are reported as season-cumulative and need disaccumulation.
    expected_accumulated = {2015, 2017, 2018, 2019, 2020, 2022, 2023, 2024, 2026}
    actual = {y for y, cfg in catalog.YEAR_REGISTRY.items() if cfg.accumulated}
    assert actual == expected_accumulated


def test_2025_has_no_scouts_flag():
    assert catalog.YEAR_REGISTRY[2025].has_scouts is False


def test_all_years_have_existing_raw_dir(repo_root):
    missing = [y for y, cfg in catalog.YEAR_REGISTRY.items() if not (repo_root / cfg.raw_dir).is_dir()]
    assert missing == [], f"Years with missing raw dirs: {missing}"


@pytest.mark.parametrize("year", EXPECTED_YEARS)
def test_each_year_has_callable_reader(year):
    cfg = catalog.YEAR_REGISTRY[year]
    assert callable(cfg.reader)
