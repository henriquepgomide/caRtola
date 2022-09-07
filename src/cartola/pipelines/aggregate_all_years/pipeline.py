"""
This is a boilerplate pipeline 'aggregate_all_years'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.commons.dataframes import concat_partitioned_datasets


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(concat_partitioned_datasets, inputs="primary", outputs="concatenated"),
        ],
        tags=["aggregated"],
        namespace="aggregated",
    )
