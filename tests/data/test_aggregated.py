"""Aggregated CSV expectation tests against data/04_feature/aggregated.csv."""

import pytest

from cartola.schemas.aggregated import AggregatedSchema

CANONICAL_COLUMNS = [
    "id_atleta", "slug", "apelido", "nome", "posicao", "status",
    "id_clube", "nome_clube", "ano", "rodada", "participou", "num_jogos",
    "pontuacao", "media", "preco", "variacao",
    "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF", "FS",
    "FT", "G", "GC", "GS", "I", "PC", "PI", "PP", "PS", "SG",
]
SCOUT_COLUMNS = [
    "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF", "FS",
    "FT", "G", "GC", "GS", "I", "PC", "PI", "PP", "PS", "SG",
]
EXPECTED_FULL_YEARS = list(range(2014, 2025))  # 2025 and 2026 may be partial


@pytest.mark.data
def test_aggregated_schema(data_aggregated):
    AggregatedSchema.validate(data_aggregated, inplace=True, lazy=True)


@pytest.mark.data
def test_aggregated_columns_match_canonical(data_aggregated):
    assert list(data_aggregated.columns) == CANONICAL_COLUMNS


@pytest.mark.data
def test_aggregated_contains_all_full_years(data_aggregated):
    years_present = set(data_aggregated["ano"].unique())
    missing = set(EXPECTED_FULL_YEARS) - years_present
    assert not missing, f"missing years: {sorted(missing)}"


@pytest.mark.data
def test_aggregated_no_negative_scouts(data_aggregated):
    """Hard invariant per the spec: scouts must be >= 0 when present."""
    for col in SCOUT_COLUMNS:
        if col in data_aggregated.columns:
            assert (data_aggregated[col].dropna() >= 0).all(), f"negative values in {col}"


@pytest.mark.data
def test_aggregated_per_round_scout_bounds(data_aggregated):
    """After de-accumulation, per-(player, round) scout values must fit reality.

    Bounds are loose because the source data has a small number of corrupt
    single rows (e.g. one 2020 round-10 row claiming G=35 for a defender)
    that we cannot fix from within the pipeline. The strict spec is the
    `>= 0` invariant above; this is a sanity check for egregious accumulation
    bugs (which would push values into the hundreds).
    """
    bounds = {"G": 50, "A": 10, "GC": 5, "CA": 10, "CV": 2, "SG": 5}
    for col, upper in bounds.items():
        observed_max = data_aggregated[col].dropna().max()
        assert observed_max <= upper, f"{col} max={observed_max} exceeds bound {upper}"


@pytest.mark.data
def test_aggregated_cumulative_sum_non_decreasing(data_aggregated):
    """Per (year, id_atleta), summing scouts across rounds must be >= 0
    at every step. Trivially true if every per-round value is >= 0; this
    is a belt-and-suspenders check that no over-subtraction snuck in.
    """
    sample = (
        data_aggregated.dropna(subset=["id_atleta"])
        .sort_values(["ano", "id_atleta", "rodada"])
        .groupby(["ano", "id_atleta"])
    )
    for (ano, id_atleta), grp in sample:
        for col in ["G", "A", "CA", "CV"]:
            csum = grp[col].fillna(0).cumsum()
            assert (csum >= 0).all(), f"negative cumulative {col} for ano={ano}, id={id_atleta}"


@pytest.mark.data
def test_aggregated_clubes_per_year_in_range(data_aggregated):
    """Each year's Brasileirão hosts roughly 16-22 distinct clubs."""
    counts = data_aggregated.groupby("ano")["id_clube"].nunique()
    for ano, n in counts.items():
        assert 16 <= n <= 22, f"year {ano} has {n} distinct id_clube"


@pytest.mark.data
def test_aggregated_position_distribution_non_degenerate(data_aggregated):
    """Every full year should have at least one player at each non-tec position."""
    non_tec = ["gol", "lat", "zag", "mei", "ata"]
    for ano in EXPECTED_FULL_YEARS:
        positions = set(data_aggregated[data_aggregated["ano"] == ano]["posicao"].dropna().unique())
        missing = set(non_tec) - positions
        assert not missing, f"year {ano} missing positions {missing}"
