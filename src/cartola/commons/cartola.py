from typing import Dict
from unidecode import unidecode
import pandas as pd


def fill_scouts_with_zeros(df: pd.DataFrame, scouts: Dict[str, float]):
    scouts_cols = scouts.keys()
    df.loc[:, scouts_cols] = df.loc[:, scouts_cols].fillna(0.0)
    return df


def fill_empty_slugs(df: pd.DataFrame):
    slug_norm = lambda apelido: unidecode(apelido.lower().replace(" ", "-"))
    empty_slugs = df["slug"].isna()
    df.loc[empty_slugs, "slug"] = df.loc[empty_slugs, "apelido"].apply(slug_norm)
    return df
