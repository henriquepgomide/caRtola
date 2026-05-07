"""Per-year data expectation tests against data/03_primary/preprocessed_{year}.csv."""

import math

import pytest

YEARS = list(range(2014, 2027))
ACCUMULATED_YEARS = {2015, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026}
VALID_POSICOES = {"gol", "lat", "zag", "mei", "ata", "tec"}


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_year_column_matches_filename(data_per_year):
    year, df = data_per_year
    if "ano" not in df.columns:
        pytest.skip("ano column not yet added at this stage")
    assert (df["ano"].dropna().astype(int) == year).all()


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_rodada_in_valid_range(data_per_year):
    _, df = data_per_year
    rodada = df["rodada"].dropna().astype(int)
    # Some years' raw data carries rodada=0 placeholders; the aggregate
    # pipeline filters those out, but the per-year primary keeps them.
    assert (rodada >= 0).all()
    assert (rodada <= 38).all()


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_pontuacao_is_finite(data_per_year):
    _, df = data_per_year
    pontuacao = df["pontuacao"].dropna()
    assert pontuacao.apply(lambda x: math.isfinite(x)).all()


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_posicao_in_canonical_set(data_per_year):
    _, df = data_per_year
    posicao = df["posicao"].dropna().unique()
    extras = set(posicao) - VALID_POSICOES
    assert not extras, f"unexpected posicao values: {extras}"


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_every_row_has_slug(data_per_year):
    _, df = data_per_year
    assert df["slug"].notna().all()
    assert (df["slug"].astype(str).str.len() > 0).all()


@pytest.mark.data
@pytest.mark.parametrize(
    "data_per_year",
    [y for y in YEARS if y not in ACCUMULATED_YEARS],
    indirect=True,
    ids=[str(y) for y in YEARS if y not in ACCUMULATED_YEARS],
)
def test_non_accumulated_years_have_per_round_scout_bounds(data_per_year):
    """For non-cumulative years the primary CSV is already per-round.

    Bounds are intentionally loose (G<=10, CA<=3, CV<=2): they catch broken
    accumulation (which would push values into the dozens) while tolerating
    the occasional source-data quirk (e.g. CA=2 rows in 2014).
    """
    _, df = data_per_year
    if "G" in df.columns:
        assert df["G"].dropna().max() <= 10
    if "CA" in df.columns:
        assert df["CA"].dropna().max() <= 3
    if "CV" in df.columns:
        assert df["CV"].dropna().max() <= 2
