from typing import Dict
import pandas as pd


def merge_partitioned_datasets(partitioned_dataset: Dict[str, pd.DataFrame]):
    df_combined = pd.DataFrame()
    for _, partition_load_func in partitioned_dataset.items():
        partition_data = partition_load_func()
        df_combined = pd.concat([df_combined, partition_data], ignore_index=True)

    return df_combined.reset_index(drop=True)
