"""
This is a boilerplate pipeline 'preprocessing'
generated using Kedro 0.18.2
"""

from typing import Dict

import pandas as pd

from cartola.commons.features import compute_slug
from cartola.commons.scouts import get_disaccumulated_scouts_for_round


def fill_scouts_with_zeros(df: pd.DataFrame, dict_scouts: Dict[str, float]) -> pd.DataFrame:
    scouts_cols = dict_scouts.keys()
    df.loc[:, scouts_cols] = df.loc[:, scouts_cols].fillna(0)
    return df


def fill_empty_slugs(df: pd.DataFrame) -> pd.DataFrame:
    if "slug" not in df.columns:
        df["slug"] = None

    empty_slugs = df["slug"].isna()
    df.loc[empty_slugs, "slug"] = df.loc[empty_slugs, "apelido"].apply(compute_slug)
    return df


def map_status_id_to_string(df: pd.DataFrame, dict_status_to_str: Dict[int, str]) -> pd.DataFrame:
    if "status" not in df.columns:
        return df

    df.status.replace(dict_status_to_str, inplace=True)
    return df


def map_posicao_to_string(df: pd.DataFrame, dict_posicao_to_str: Dict[str, str]) -> pd.DataFrame:
    df.posicao = df.posicao.astype(str)
    df.posicao.replace(dict_posicao_to_str, inplace=True)
    return df


def add_year_column(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df["ano"] = year
    return df


def fix_accumulated_scouts(df: pd.DataFrame, dict_scouts: Dict[str, float]) -> pd.DataFrame:
    if ~df.ano.isin([2015, 2017, 2018, 2019, 2020, 2021, 2022]).all():
        return df

    cols_scouts = list(dict_scouts.keys())
    df_result = pd.DataFrame([])
    for round_ in range(1, 39):
        df_round = get_disaccumulated_scouts_for_round(df, round_, cols_scouts)
        df_result = pd.concat([df_result, df_round], ignore_index=True)

    return df_result
