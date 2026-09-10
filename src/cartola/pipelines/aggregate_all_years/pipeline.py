"""Aggregate-all-years pipeline: per-year primaries -> single canonical CSV."""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.pipelines.aggregate_all_years.nodes import (
    concat_normalized_partitions,
    finalize_aggregated,
    normalize_partitions,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Build the aggregate pipeline."""
    return pipeline(
        [
            node(
                normalize_partitions,
                inputs=[
                    "primary",
                    "params:canonical_columns",
                    "params:scouts",
                    "params:accumulated_years",
                    "params:clube_id_map",
                ],
                outputs="normalized",
            ),
            node(
                concat_normalized_partitions,
                inputs="normalized",
                outputs="concatenated",
            ),
            node(
                finalize_aggregated,
                inputs=["concatenated", "params:map_types"],
                outputs="aggregated",
            ),
        ],
        tags=["aggregated"],
        namespace="aggregated",
    )
