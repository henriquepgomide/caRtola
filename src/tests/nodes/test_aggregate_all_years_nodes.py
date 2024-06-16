import pandas as pd
import pandas.api.types as ptypes

from cartola.pipelines.aggregate_all_years.nodes import convert_types


def test_convert_types():
    df = pd.DataFrame(dict(col_str=["1", "2"], col_int=[1, 2], col_float=[1.1, 2.2]))

    dict_map_types = dict(col_str=int, col_int=str, col_float=int)
    df_res = convert_types(df, dict_map_types)
    assert ptypes.is_integer_dtype(df_res.col_str)
    assert ptypes.is_integer_dtype(df_res.col_float)
    assert ptypes.is_string_dtype(df_res.col_int)
