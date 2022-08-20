"""
This is a boilerplate pipeline 'merge_splitted_datasets'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import merge_datasets


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(merge_datasets, inputs=["scouts", "players", "teams", "params:map_col_names"], outputs="concat"),
        ],
        namespace="merge",
        tags=["merge"],
    )
