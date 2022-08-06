"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline
from cartola.pipelines import preprocessing as prep2022


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    pipe_2022 = pipeline(
        pipe=prep2022.create_pipeline(),
        inputs=None,
        namespace="2022",
        parameters=["params:preprocessing.map_col_names", "params:preprocessing.map_status_id_to_str"],
    )

    return {"__default__": pipe_2022, "2022": pipe_2022}
