"""Pipeline definition for merge_splitted_datasets (years 2014-2016)."""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.pipelines.merge_splitted_datasets.nodes import merge_datasets


def create_pipeline() -> Pipeline:
    """Build the merge_splitted_datasets pipeline."""
    return pipeline(
        [
            node(merge_datasets, inputs=["scouts", "players", "teams"], outputs="concat"),
        ],
        namespace="merge",
        tags=["merge"],
        outputs=dict(concat="preprocessing.raw"),
    )
