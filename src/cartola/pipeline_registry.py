"""Project pipelines."""

from typing import Dict

from kedro.pipeline import Pipeline, pipeline

from cartola.pipelines import aggregate_all_years, merge_splitted_datasets, preprocessing


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    params_preprocessing = {"params:preprocessing.map_col_names", "params:preprocessing.map_status_id_to_str"}

    pipe_2014 = pipeline(
        pipe=merge_splitted_datasets.create_pipeline() + preprocessing.create_pipeline(),
        namespace="2014",
        parameters=params_preprocessing,
    )

    pipe_2015 = pipeline(
        pipe=merge_splitted_datasets.create_pipeline() + preprocessing.create_pipeline(),
        namespace="2015",
        parameters=params_preprocessing,
    )

    pipe_2016 = pipeline(
        pipe=merge_splitted_datasets.create_pipeline() + preprocessing.create_pipeline(),
        namespace="2016",
        parameters=params_preprocessing,
    )

    pipe_2017 = pipeline(
        pipe=preprocessing.create_pipeline(),
        namespace="2017",
        parameters=params_preprocessing,
    )

    pipe_2018 = pipeline(
        pipe=preprocessing.create_pipeline(),
        namespace="2018",
        parameters=params_preprocessing,
    )

    pipe_2019 = pipeline(
        pipe=preprocessing.create_pipeline(),
        namespace="2019",
        parameters=params_preprocessing,
    )

    pipe_2020 = pipeline(
        pipe=preprocessing.create_pipeline(),
        namespace="2020",
        parameters=params_preprocessing,
    )

    pipe_2021 = pipeline(
        pipe=preprocessing.create_pipeline(),
        namespace="2021",
        parameters=params_preprocessing,
    )

    pipe_2022 = pipeline(
        pipe=preprocessing.create_pipeline(),
        namespace="2022",
        parameters=params_preprocessing,
    )

    pipe_aggregate = aggregate_all_years.create_pipeline()

    return {
        "__default__": (
            pipe_2014 + pipe_2015 + pipe_2016 + pipe_2017 + pipe_2018 + pipe_2019 + pipe_2020 + pipe_2021 + pipe_2022
        ),
        "2014": pipe_2014,
        "2015": pipe_2015,
        "2016": pipe_2016,
        "2017": pipe_2017,
        "2018": pipe_2018,
        "2019": pipe_2019,
        "2020": pipe_2020,
        "2021": pipe_2021,
        "2022": pipe_2022,
        "aggregate": pipe_aggregate,
    }
