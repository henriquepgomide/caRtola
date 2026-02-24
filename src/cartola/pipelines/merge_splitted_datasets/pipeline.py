"""This is a boilerplate pipeline 'merge_splitted_datasets'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.pipelines.merge_splitted_datasets.nodes import merge_datasets


def create_pipeline() -> Pipeline:
    return pipeline(
        [
            node(merge_datasets, inputs=["scouts", "players", "teams"], outputs="concat"),
        ],
        namespace="merge",
        tags=["merge"],
        outputs=dict(concat="preprocessing.raw"),
    )
