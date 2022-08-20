"""
This is a boilerplate pipeline 'preprocessing'
generated using Kedro 0.18.2
"""
from typing import Dict

import pandas as pd
from unidecode import unidecode


def fill_scouts_with_zeros(df: pd.DataFrame, dict_scouts: Dict[str, float]) -> pd.DataFrame:
    scouts_cols = dict_scouts.keys()
    df.loc[:, scouts_cols] = df.loc[:, scouts_cols].fillna(0.0)
    return df


def fill_empty_slugs(df: pd.DataFrame) -> pd.DataFrame:
    if "slug" not in df.columns:
        df["slug"] = None

    slug_norm = lambda apelido: unidecode(apelido.lower().replace(" ", "-"))
    empty_slugs = df["slug"].isna()
    df.loc[empty_slugs, "slug"] = df.loc[empty_slugs, "apelido"].apply(slug_norm)
    return df


def map_status_id_to_string(df: pd.DataFrame, dict_status_to_str: Dict[int, str]) -> pd.DataFrame:
    if "status" not in df.columns:
        return df

    df.status.replace(dict_status_to_str, inplace=True)
    return df
