"""
This is a boilerplate pipeline 'preprocessing_2022'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline
from cartola.commons.dataframes import (
    concat_partitioned_datasets,
    drop_duplicated_rows,
    rename_cols,
)
from .nodes import fill_scouts_with_zeros, fill_empty_slugs


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                concat_partitioned_datasets,
                inputs="raw_2022",
                outputs="concat_2022",
                tags=["preprocessing"],
            ),
            node(
                rename_cols,
                inputs=["concat_2022", "params:map_col_names"],
                outputs="df_renamed",
                tags=["preprocessing"],
            ),
            node(
                drop_duplicated_rows,
                inputs="df_renamed",
                outputs="df_not_duplicated",
                tags=["preprocessing"],
            ),
            node(
                fill_scouts_with_zeros,
                inputs=["df_not_duplicated", "params:scouts_2022"],
                outputs="df_filled_scouts",
                tags=["preprocessing"],
            ),
            node(
                fill_empty_slugs,
                inputs=["df_filled_scouts"],
                outputs="preprocessed_2022",
                tags=["preprocessing"],
            ),
        ],
    )
