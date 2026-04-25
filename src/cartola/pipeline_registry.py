"""Project pipelines."""

from typing import Dict

from kedro.pipeline import Pipeline, pipeline

from cartola.pipelines import (
    aggregate_all_years,
    merge_splitted_datasets,
    preprocessing,
)


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    params_preprocessing = {
        "params:preprocessing.map_col_names",
        "params:preprocessing.map_status_id_to_str",
        "params:preprocessing.map_posicao_to_str",
    }

    def _year_pipeline(year: int, *, with_merge: bool) -> Pipeline:
        base = preprocessing.create_pipeline()
        if with_merge:
            base = merge_splitted_datasets.create_pipeline() + base
        return pipeline(base, namespace=str(year), parameters=params_preprocessing)

    year_pipelines = {
        year: _year_pipeline(year, with_merge=year in (2014, 2015, 2016))
        for year in range(2014, 2027)
    }

    pipe_aggregate = aggregate_all_years.create_pipeline()

    default = year_pipelines[2014]
    for year in range(2015, 2027):
        default = default + year_pipelines[year]
    default = default + pipe_aggregate

    pipelines: Dict[str, Pipeline] = {
        "__default__": default,
        "aggregate": pipe_aggregate,
    }
    pipelines.update({str(y): p for y, p in year_pipelines.items()})
    return pipelines
