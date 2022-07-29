"""
This is a boilerplate pipeline 'preprocessing_2022'
generated using Kedro 0.18.2
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import remove_nans
from cartola.utils.dataframes import concat_partitioned_datasets


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            concat_partitioned_datasets,
            inputs="raw_2022",
            outputs="concat_2022",
            tags=["preprocessing"],
            namespace="2022",
        ),
    ])
