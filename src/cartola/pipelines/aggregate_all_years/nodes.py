"""
This is a boilerplate pipeline 'aggregate_all_years'
generated using Kedro 0.18.2
"""

from typing import Dict


import pandas as pd


def convert_types(df: pd.DataFrame, map_types: Dict[str, type]) -> pd.DataFrame:
    return df.astype(map_types)
