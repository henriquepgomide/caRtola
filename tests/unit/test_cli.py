"""Tests for the Typer CLI."""

import pandas as pd
from typer.testing import CliRunner

from cartola import cli

runner = CliRunner()


def test_parse_years_returns_none_when_input_is_none():
    assert cli._parse_years(None) is None


def test_parse_years_strips_and_skips_empty_entries():
    assert cli._parse_years("2018, 2019, ,2020") == [2018, 2019, 2020]


def test_parse_years_single_year():
    assert cli._parse_years("2024") == [2024]


def test_aggregate_invokes_driver_run_with_parsed_years(mocker):
    fake = mocker.patch.object(cli.driver, "run", return_value=pd.DataFrame({"x": [1, 2, 3]}))
    result = runner.invoke(cli.app, ["aggregate", "--years", "2018,2019"])
    assert result.exit_code == 0
    fake.assert_called_once_with(years=[2018, 2019])
    assert "3 rows total" in result.stdout


def test_aggregate_without_years_passes_none(mocker):
    fake = mocker.patch.object(cli.driver, "run", return_value=pd.DataFrame())
    result = runner.invoke(cli.app, ["aggregate"])
    assert result.exit_code == 0
    fake.assert_called_once_with(years=None)


def test_app_no_args_shows_help():
    result = runner.invoke(cli.app, [])
    assert "aggregate" in result.stdout.lower()
