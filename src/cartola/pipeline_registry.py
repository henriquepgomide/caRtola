"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline
from cartola.pipelines import preprocessing


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    params_preprocessing = ["params:preprocessing.map_col_names", "params:preprocessing.map_status_id_to_str"]
    pipe_2021 = pipeline(
        pipe=preprocessing.create_pipeline(),
        inputs=None,
        namespace="2021",
        parameters=params_preprocessing,
    )
    
    pipe_2022 = pipeline(
        pipe=preprocessing.create_pipeline(),
        inputs=None,
        namespace="2022",
        parameters=params_preprocessing,
    )

    return {
        "__default__": pipe_2021 + pipe_2022, 
        "2021": pipe_2021,
        "2022": pipe_2022
    }
