"""Pipeline definition for merge_splitted_datasets (years 2014-2016)."""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.pipelines.merge_splitted_datasets.nodes import merge_datasets


def create_pipeline() -> Pipeline:
    """Build the merge_splitted_datasets pipeline.

    The output is kept as the namespaced ``merge.concat`` dataset; the
    cross-namespace handoff to ``preprocessing.raw`` is wired in
    ``pipeline_registry`` after both sub-pipelines have been wrapped under
    the shared year namespace, which keeps Kedro's dotted-name validator
    happy (see ``kedro/pipeline/node.py::_node_dataset_name_validation``).
    """
    return pipeline(
        [
            node(merge_datasets, inputs=["scouts", "players", "teams"], outputs="concat"),
        ],
        namespace="merge",
        tags=["merge"],
    )
