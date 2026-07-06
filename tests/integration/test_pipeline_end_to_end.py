"""Integration test: exercise the full per-year pipeline against synthetic fixtures.

Calls the same chain as nodes.year_dataframe directly (without going through
Hamilton) so we can pass fixture paths instead of the production raw dirs.
"""

from pathlib import Path

import pandas as pd
import pytest

from cartola.aggregation import columns, driver, player, scouts, team
from cartola.aggregation.catalog import YearConfig
from cartola.aggregation.readers import (
    read_monolithic,
    read_round_files,
    read_season_files,
)
from cartola.aggregation.schema import CANONICAL_COLUMNS, SCOUTS, apply_canonical_dtypes


def _process_year(cfg: YearConfig, year: int) -> pd.DataFrame:
    """Replicates nodes.year_dataframe with an injected YearConfig."""
    raw = cfg.reader(cfg.raw_dir, year)
    df = columns.rename_columns(raw)
    df = team.resolve_id_clube(df)
    df = player.map_position(df)
    df = player.map_status(df)
    df = player.fill_missing_slug(df)
    df = scouts.process(df, accumulated=cfg.accumulated)
    df["ano"] = year
    return apply_canonical_dtypes(df.reindex(columns=CANONICAL_COLUMNS))


@pytest.fixture
def fixture_configs(fixtures_dir: Path) -> dict[int, YearConfig]:
    return {
        2014: YearConfig(2014, str(fixtures_dir / "2014"), read_season_files),
        2017: YearConfig(2017, str(fixtures_dir / "2017"), read_monolithic, accumulated=True),
        2018: YearConfig(2018, str(fixtures_dir / "2018"), read_round_files, accumulated=True),
    }


def test_year_2014_pipeline_against_fixture(fixture_configs):
    df = _process_year(fixture_configs[2014], 2014)
    assert list(df.columns) == CANONICAL_COLUMNS
    assert len(df) == 4
    # Flamengo + Santos resolved from times.csv merge.
    assert set(df["id_clube"].dropna().tolist()) == {262, 277}
    # 2014 has no status data — column should be all NaN.
    assert df["status"].isna().all()


def test_year_2018_resolves_atl_to_atletico_mg(fixture_configs):
    df = _process_year(fixture_configs[2018], 2018)
    # nome_clube="Atlético-MG" → id_clube=282 (not the buggy "ATL" abbreviation).
    assert (df["id_clube"] == 282).all()
    # 2018 is accumulated → per-round FC delta from round 1 (cumulative=1) to round 2 (cumulative=2) is 1.
    fc_round_2 = df.loc[df["rodada"] == 2, "FC"].iloc[0]
    assert fc_round_2 == 1.0


def test_year_2017_pipeline_against_fixture(fixture_configs):
    df = _process_year(fixture_configs[2017], 2017)
    assert list(df.columns) == CANONICAL_COLUMNS
    assert len(df) == 2
    # Status was already a string label ("Provável") — should pass through.
    assert (df["status"] == "Provável").all()


def test_per_year_write_round_trip(tmp_path, fixture_configs, monkeypatch):
    """Write a per-year DataFrame to CSV and re-read it; columns AND values
    must round-trip, not just shape.

    A plain `assert len(reread) == len(df)` would pass even if every scout
    column got silently mangled by the CSV round-trip (e.g. an int column
    written with a `.0` suffix and re-read as float, or a `pd.NA` written
    as the literal string ``"<NA>"`` instead of an empty field) — this
    compares actual cell values, with dtype drift allowed but only for the
    columns already known to be dtype-unstable across a CSV round-trip
    (nullable Int/string columns lose their pandas-specific dtype and come
    back as float64/object; see `schema.apply_canonical_dtypes`).
    """
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "03_primary")
    driver.PRIMARY_DIR.mkdir(parents=True, exist_ok=True)

    df = _process_year(fixture_configs[2014], 2014)
    out = driver.PRIMARY_DIR / "cartola_2014.csv"
    df.to_csv(out, index=False)

    reread = pd.read_csv(out)
    assert list(reread.columns) == CANONICAL_COLUMNS
    assert len(reread) == len(df)

    # Numeric scout/context columns must match exactly (as float, to absorb
    # the int64->float64 CSV round-trip noise on nullable columns without
    # masking a genuine value mismatch).
    numeric_cols = ["ano", "rodada", "id_clube", "id_atleta", "pontuacao", "preco", *SCOUTS]
    for col in numeric_cols:
        pd.testing.assert_series_equal(
            df[col].astype("float64").reset_index(drop=True),
            reread[col].astype("float64").reset_index(drop=True),
            check_names=False,
            obj=col,
        )

    # String columns must match exactly, treating pandas NA and CSV-empty as equal.
    string_cols = ["nome_clube", "apelido", "posicao", "status", "slug"]
    for col in string_cols:
        original = df[col].astype("string").fillna("")
        roundtripped = reread[col].astype("string").fillna("")
        pd.testing.assert_series_equal(
            original.reset_index(drop=True),
            roundtripped.reset_index(drop=True),
            check_names=False,
            obj=col,
        )
