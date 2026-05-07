"""
This is a boilerplate pipeline 'preprocessing'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.commons.dataframes import concat_partitioned_datasets, drop_duplicated_rows, rename_cols
from cartola.pipelines.preprocessing.nodes import fill_empty_slugs, fill_scouts_with_zeros, map_status_id_to_string


def create_pipeline() -> Pipeline:
    return pipeline(
        [
            node(
                concat_partitioned_datasets,
                inputs="raw",
                outputs="concat",
            ),
            node(rename_cols, inputs=["concat", "params:map_col_names"], outputs="df_renamed"),
            node(
                drop_duplicated_rows,
                inputs="df_renamed",
                outputs="df_not_duplicated",
            ),
            node(
                map_status_id_to_string,
                inputs=["df_not_duplicated", "params:map_status_id_to_str"],
                outputs="df_status",
            ),
            node(
                fill_scouts_with_zeros,
                inputs=["df_status", "params:scouts"],
                outputs="df_filled_scouts",
            ),
            node(
                fill_empty_slugs,
                inputs=["df_filled_scouts"],
                outputs="preprocessed",
            ),
        ],
        namespace="preprocessing",
        tags=["preprocessing"],
    )
