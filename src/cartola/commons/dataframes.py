from typing import Dict
import pandas as pd


def drop_duplicated_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(ignore_index=True)


def concat_partitioned_datasets(partitioned_dataset: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_concat = pd.DataFrame()
    for _, partition_load_func in partitioned_dataset.items():
        partition_data = partition_load_func()
        df_concat = pd.concat([df_concat, partition_data], ignore_index=True)

    return df_concat.reset_index(drop=True)


def rename_cols(df: pd.DataFrame, map_col_names: Dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=map_col_names)
