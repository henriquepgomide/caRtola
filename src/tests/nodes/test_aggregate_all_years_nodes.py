import numpy as np
import pandas as pd
import pytest

from cartola.commons.scouts import disaccumulate_scouts
from cartola.pipelines.aggregate_all_years.nodes import (
    convert_types,
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


def test_convert_types():
    df = pd.DataFrame(dict(col_str=["1", "2"], col_int=[1, 2], col_float=[1.1, 2.2]))
    dict_map_types = dict(col_str=int, col_int=str, col_float=int)
    df_res = convert_types(df, dict_map_types)
    import pandas.api.types as ptypes
    assert ptypes.is_integer_dtype(df_res.col_str)
    assert ptypes.is_integer_dtype(df_res.col_float)
    assert ptypes.is_string_dtype(df_res.col_int)


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
