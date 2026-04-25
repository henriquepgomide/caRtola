import numpy as np
import pandas as pd
import pytest

from cartola.commons.scouts import disaccumulate_scouts
from cartola.pipelines.aggregate_all_years.nodes import (
    concat_normalized_partitions,
    finalize_aggregated,
    normalize_partitions,
)


CANONICAL = [
    "id_atleta", "slug", "apelido", "nome", "posicao", "status",
    "id_clube", "nome_clube", "ano", "rodada",
    "participou", "num_jogos", "pontuacao", "media", "preco", "variacao",
    "G", "A", "CA", "SG",
]
SCOUTS = ["G", "A", "CA", "SG"]


def _partition(df: pd.DataFrame):
    return lambda: df


def test_disaccumulate_scouts_simple_player():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            CA=[0, 1, 1],
            DE=[0, 1, 3],
        )
    )
    result = disaccumulate_scouts(df, ["CA", "DE"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert list(result["CA"]) == [0, 1, 0]
    assert list(result["DE"]) == [0, 1, 2]


def test_disaccumulate_scouts_sg_clipping():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            SG=[1, 0, 1],  # cumulative max should be 1, 1, 1 -> deltas would be 1, 0, 0
        )
    )
    result = disaccumulate_scouts(df, ["SG"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert (result["SG"] >= 0).all()
    assert (result["SG"] <= 1).all()


def test_disaccumulate_scouts_caps_sg_when_player_misses_rounds():
    """SG (clean sheet) is binary per round. If a goalkeeper plays round 2
    but misses round 3 and plays round 4, the cumulative SG can jump from
    1 -> 3 between rounds 2 and 4. The naive delta is 2 but SG is bounded
    above by 1 per round.
    """
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[2, 4, 5],
            SG=[1, 3, 4],
        )
    )
    result = disaccumulate_scouts(df, ["SG"])
    assert (result["SG"] <= 1).all()


def test_disaccumulate_scouts_player_appears_mid_season():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 2, 2],
            rodada=[1, 2, 2, 3],
            G=[0, 1, 0, 2],
        )
    )
    result = disaccumulate_scouts(df, ["G"])
    result = result.sort_values(["id_atleta", "rodada"]).reset_index(drop=True)
    assert list(result["G"]) == [0, 1, 0, 2]


def test_disaccumulate_scouts_passes_through_non_scout_columns():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1],
            rodada=[1, 2],
            apelido=["X", "X"],
            G=[0, 1],
        )
    )
    result = disaccumulate_scouts(df, ["G"])
    assert "apelido" in result.columns
    assert (result["apelido"] == "X").all()


def test_disaccumulate_scouts_clips_negative_deltas_to_zero():
    """Source-data noise (e.g. Cartola correcting a mis-scored event or a round
    reset to 0 mid-season) can produce negative deltas. Per the spec, scouts
    must be >= 0 when present, so deltas are clipped at zero.
    """
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            G=[0, 5, 0],
            CA=[0, 3, 1],
        )
    )
    result = disaccumulate_scouts(df, ["G", "CA"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert list(result["G"]) == [0, 5, 0]
    assert list(result["CA"]) == [0, 3, 0]
    assert (result["G"] >= 0).all()
    assert (result["CA"] >= 0).all()


def test_disaccumulate_scouts_handles_nan_scouts():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            G=[0.0, np.nan, 2.0],
        )
    )
    result = disaccumulate_scouts(df, ["G"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert (result["G"].fillna(0) >= 0).all()


def test_normalize_partitions_selects_canonical_columns_only():
    df = pd.DataFrame(
        dict(
            id_atleta=[1], slug=["x"], apelido=["X"], nome=["X Full"],
            posicao=["gol"], status=[None], id_clube=[10], nome_clube=["Club"],
            ano=[2014], rodada=[1], participou=[1], num_jogos=[1],
            pontuacao=[1.0], media=[1.0], preco=[5.0], variacao=[0.1],
            G=[0], A=[0], CA=[0], SG=[1],
            extra_garbage=["drop me"],
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    assert set(result[2014].columns) == set(CANONICAL)


def test_normalize_partitions_fills_missing_scouts_with_nan():
    df = pd.DataFrame(
        dict(
            id_atleta=[1], slug=["x"], apelido=["X"], nome=["X"],
            posicao=["gol"], status=[None], id_clube=[10], nome_clube=["C"],
            ano=[2014], rodada=[1], participou=[1], num_jogos=[1],
            pontuacao=[1.0], media=[1.0], preco=[5.0], variacao=[0.1],
            G=[0], A=[0],
            # CA and SG missing on purpose
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    out = result[2014]
    assert "CA" in out.columns and "SG" in out.columns
    assert out["CA"].isna().all()
    assert out["SG"].isna().all()


def test_normalize_partitions_year_mismatch_raises():
    df = pd.DataFrame(
        dict(
            id_atleta=[1], slug=["x"], apelido=["X"], nome=["X"],
            posicao=["gol"], status=[None], id_clube=[10], nome_clube=["C"],
            ano=[2019], rodada=[1], participou=[1], num_jogos=[1],
            pontuacao=[1.0], media=[1.0], preco=[5.0], variacao=[0.1],
            G=[0], A=[0], CA=[0], SG=[1],
        )
    )
    with pytest.raises(ValueError, match="2018"):
        normalize_partitions(
            {"preprocessed_2018": _partition(df)},
            canonical_columns=CANONICAL,
            scout_columns=SCOUTS,
            accumulated_years=[],
        )


def _accumulated_two_round_df(year: int) -> pd.DataFrame:
    return pd.DataFrame(
        dict(
            id_atleta=[1, 1], slug=["x", "x"], apelido=["X", "X"], nome=["X", "X"],
            posicao=["gol", "gol"], status=[None, None],
            id_clube=[10, 10], nome_clube=["C", "C"],
            ano=[year, year], rodada=[1, 2],
            participou=[1, 1], num_jogos=[1, 2],
            pontuacao=[1.0, 1.0], media=[1.0, 1.0], preco=[5.0, 5.0], variacao=[0.0, 0.0],
            G=[0, 2], A=[0, 0], CA=[0, 1], SG=[1, 1],
        )
    )


def test_normalize_partitions_applies_disaccumulation_only_to_accumulated_years():
    df_2018 = _accumulated_two_round_df(2018)
    df_2014 = _accumulated_two_round_df(2014)
    result = normalize_partitions(
        {"preprocessed_2018": _partition(df_2018), "preprocessed_2014": _partition(df_2014)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[2018],
    )
    out_2018 = result[2018].sort_values("rodada").reset_index(drop=True)
    out_2014 = result[2014].sort_values("rodada").reset_index(drop=True)
    # 2018 was disaccumulated: round-2 G should be 2 (delta from 0 -> 2), CA should be 1.
    assert list(out_2018["G"]) == [0, 2]
    assert list(out_2018["CA"]) == [0, 1]
    # 2014 was NOT disaccumulated: round-2 G stays at the cumulative 2.
    assert list(out_2014["G"]) == [0, 2]


def test_normalize_partitions_drops_invalid_rodadas():
    """rodada < 1 is invalid (pre-season placeholders); filter them out."""
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1], slug=["x", "x", "x"], apelido=["X", "X", "X"], nome=["X", "X", "X"],
            posicao=["gol"] * 3, status=[None] * 3, id_clube=[10] * 3, nome_clube=["C"] * 3,
            ano=[2014] * 3, rodada=[0, 1, 2],
            participou=[1] * 3, num_jogos=[1] * 3, pontuacao=[1.0] * 3, media=[1.0] * 3,
            preco=[5.0] * 3, variacao=[0.0] * 3,
            G=[0, 0, 1], A=[0, 0, 0], CA=[0, 0, 0], SG=[1, 1, 1],
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    assert (result[2014]["rodada"] >= 1).all()
    assert len(result[2014]) == 2


def test_normalize_partitions_dedupes_by_player_round_keeps_low_scout_sum():
    """Source data carries duplicate (id_atleta, rodada) rows from re-scrapes,
    where the noisy scrape is consistently inflated. Keep the row whose scout
    sum is smaller (the cleaner reading) so disaccumulation has a well-defined
    cumulative sequence.
    """
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1], slug=["x", "x", "x"], apelido=["X", "X", "X"], nome=["X", "X", "X"],
            posicao=["gol"] * 3, status=[None] * 3, id_clube=[10] * 3, nome_clube=["C"] * 3,
            ano=[2014] * 3, rodada=[1, 1, 2],
            participou=[1] * 3, num_jogos=[1] * 3, pontuacao=[1.0] * 3, media=[1.0] * 3,
            preco=[5.0] * 3, variacao=[0.0] * 3,
            # Two rows for rodada=1; the noisy one (G=99) appears first, the
            # clean one (G=0) appears second. Order-based "keep=first" would
            # pick the noisy row, so we keep the lower scout-sum instead.
            G=[99, 0, 1], A=[0, 0, 0], CA=[0, 0, 0], SG=[1, 1, 1],
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    out = result[2014].sort_values("rodada").reset_index(drop=True)
    assert len(out) == 2
    grouped = out.groupby(["id_atleta", "rodada"]).size()
    assert (grouped == 1).all()
    assert out.iloc[0]["G"] == 0


def test_normalize_partitions_coerces_id_clube_and_participou_to_numeric():
    """Across years the raw data carries id_clube as int, '262.0' string, or
    float, and participou as 1/0, True/False, or 'True'/'False'. Normalize
    them to numeric so the schema validates and downstream consumers see a
    consistent type.
    """
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 2], slug=["a", "b"], apelido=["A", "B"], nome=["A", "B"],
            posicao=["gol", "ata"], status=[None, None],
            id_clube=["262.0", "263.0"],
            nome_clube=["X", "Y"],
            ano=[2014, 2014], rodada=[1, 1],
            participou=["True", "False"],
            num_jogos=[1, 1], pontuacao=[1.0, 1.0], media=[1.0, 1.0],
            preco=[5.0, 5.0], variacao=[0.0, 0.0],
            G=[0, 0], A=[0, 0], CA=[0, 0], SG=[1, 0],
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    out = result[2014]
    assert pd.api.types.is_numeric_dtype(out["id_clube"])
    assert sorted(out["id_clube"]) == [262.0, 263.0]
    assert pd.api.types.is_numeric_dtype(out["participou"])
    assert set(out["participou"].dropna().unique()) <= {0, 1, 0.0, 1.0}


def test_concat_normalized_partitions_orders_by_year():
    df_2018 = pd.DataFrame(dict(ano=[2018], rodada=[1], slug=["x"], id_clube=[1]))
    df_2014 = pd.DataFrame(dict(ano=[2014], rodada=[1], slug=["x"], id_clube=[1]))
    df_2020 = pd.DataFrame(dict(ano=[2020], rodada=[1], slug=["x"], id_clube=[1]))
    out = concat_normalized_partitions({2018: df_2018, 2014: df_2014, 2020: df_2020})
    assert list(out["ano"]) == [2014, 2018, 2020]


def test_finalize_aggregated_sorts_and_casts():
    df = pd.DataFrame(
        dict(
            ano=["2014", "2014"], rodada=["2", "1"],
            id_clube=[1, 1], slug=["b", "a"],
            G=[0.0, 1.0],
        )
    )
    out = finalize_aggregated(df, dtype_map={"ano": int, "rodada": int})
    assert list(out["ano"]) == [2014, 2014]
    assert list(out["rodada"]) == [1, 2]
    assert out.iloc[0]["slug"] == "a"
