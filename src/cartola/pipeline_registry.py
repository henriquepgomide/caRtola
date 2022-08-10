"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline
from cartola.pipelines import preprocessing_2022 as prep2022


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    pipe_2022 = prep2022.create_pipeline()
    return {"__default__": pipe_2022}
