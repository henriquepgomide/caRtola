"""Pipeline that aggregates per-year preprocessed CSVs into a single feature table."""

from cartola.pipelines.aggregate_all_years.pipeline import create_pipeline

__all__ = ["create_pipeline"]

__version__ = "0.1"
