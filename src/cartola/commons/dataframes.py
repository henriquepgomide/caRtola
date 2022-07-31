from typing import Dict
import pandas as pd


def concat_partitioned_datasets(partitioned_dataset: Dict[str, pd.DataFrame]):
    df_concat = pd.DataFrame()
    for _, partition_load_func in partitioned_dataset.items():
        partition_data = partition_load_func()
        df_concat = pd.concat([df_concat, partition_data], ignore_index=True)

    return df_concat.reset_index(drop=True)
