import numpy as np
import pandas as pd

from cartola.commons.scouts import disaccumulate_scouts
from cartola.pipelines.aggregate_all_years.nodes import convert_types


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
