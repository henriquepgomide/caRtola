"""
This is a boilerplate pipeline 'preprocessing'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.commons.dataframes import (
    concat_partitioned_datasets,
    drop_columns,
    drop_duplicated_rows,
    rename_cols,
)
from cartola.pipelines.preprocessing.nodes import (
    add_year_column,
    fill_empty_slugs,
    fill_scouts_with_zeros,
    fix_accumulated_scouts,
    map_posicao_to_string,
    map_status_id_to_string,
)


def create_pipeline() -> Pipeline:
    return pipeline(
        [
            node(concat_partitioned_datasets, inputs="raw", outputs="concat"),
            node(add_year_column, inputs=["concat", "params:year"], outputs="df_year"),
            node(rename_cols, inputs=["df_year", "params:map_col_names"], outputs="df_renamed"),
            node(drop_columns, inputs=["df_renamed", "params:drop_columns"], outputs="df_dropped"),
            node(drop_duplicated_rows, inputs="df_dropped", outputs="df_not_duplicated"),
            node(
                map_posicao_to_string,
                inputs=["df_not_duplicated", "params:map_posicao_to_str"],
                outputs="df_posicao",
            ),
            node(map_status_id_to_string, inputs=["df_posicao", "params:map_status_id_to_str"], outputs="df_status"),
            node(fill_scouts_with_zeros, inputs=["df_status", "params:scouts"], outputs="df_filled_scouts"),
            node(fill_empty_slugs, inputs="df_filled_scouts", outputs="df_filled_slugs"),
            node(fix_accumulated_scouts, inputs=["df_filled_slugs", "params:scouts"], outputs="preprocessed"),
        ],
        namespace="preprocessing",
        tags=["preprocessing"],
    )
