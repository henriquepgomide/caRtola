"""Hamilton driver wrapper: builds the DAG, runs it, persists outputs.

``track=True`` enables the Hamilton UI tracker (requires ``sf-hamilton-ui``).
"""

import logging
from pathlib import Path

import pandas as pd
from hamilton import driver

from cartola.aggregation import nodes
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import AggregatedSchema

DEFAULT_UI_PORT = 8241
DEFAULT_UI_BASE_DIR = Path.home() / ".hamilton" / "db"

logger = logging.getLogger(__name__)

PRIMARY_DIR = Path("data/03_primary")
AGGREGATED_DIR = Path("data/04_aggregated")


def build_driver(track: bool = False) -> driver.Driver:
    """Build a Hamilton driver from the nodes module.

    Args:
        track: When ``True``, attaches the Hamilton UI tracker so the run
            shows up in the UI.

    Returns:
        A configured Hamilton :class:`~hamilton.driver.Driver`.
    """
    builder = driver.Builder().with_modules(nodes).with_config({})
    if track:
        try:
            from hamilton_sdk import adapters as ui_adapters

            tracker = ui_adapters.HamiltonTracker(
                project_id=1,
                username="cartola",
                dag_name="cartola_aggregation",
                tags={},
            )
            builder = builder.with_adapters(tracker)
        except ImportError:
            logger.warning("Hamilton UI not installed — install with `uv sync --extra ui` to enable --track.")
    return builder.build()


def run(years: list[int] | None = None, track: bool = False) -> pd.DataFrame:
    """Execute the pipeline.

    If ``years`` is ``None`` or matches all configured years (full run),
    request the per-year nodes **and** ``aggregated`` in a single
    :meth:`hamilton.driver.Driver.execute` call (avoids recomputing every
    ``year_<Y>`` node twice), validate against
    :class:`~cartola.aggregation.schema.AggregatedSchema`, then write both
    the per-year CSVs and the final aggregated CSV.

    If ``years`` is a strict subset (partial run), write only the per-year
    CSVs (no aggregation; aggregating a partial run could mislead
    downstream consumers).

    Args:
        years: Optional subset of season years to process.
        track: Forwarded to :func:`build_driver`.

    Returns:
        The validated aggregated DataFrame on a full run, or the
        concatenation of the selected per-year DataFrames on a partial run.

    Raises:
        ValueError: If ``years`` contains entries not in :data:`YEAR_REGISTRY`.
        pandera.errors.SchemaError: If the aggregated DataFrame violates
            :class:`AggregatedSchema` on a full run; the aggregated CSV is
            **not** written when this happens.
    """
    drv = build_driver(track=track)

    available = sorted(YEAR_REGISTRY)
    selected = sorted(years) if years else available
    invalid = [y for y in selected if y not in YEAR_REGISTRY]
    if invalid:
        raise ValueError(f"Years not in YEAR_REGISTRY: {invalid}")

    full_run = selected == available
    per_year_outputs = [f"year_{y}" for y in selected]
    outputs = [*per_year_outputs, "aggregated"] if full_run else per_year_outputs
    results = drv.execute(outputs)

    PRIMARY_DIR.mkdir(parents=True, exist_ok=True)
    for y, name in zip(selected, per_year_outputs, strict=True):
        df = results[name]
        out_path = PRIMARY_DIR / f"cartola_{y}.csv"
        df.to_csv(out_path, index=False)
        logger.info("Wrote %s (%d rows)", out_path, len(df))

    if not full_run:
        logger.info(
            "Partial run (%d/%d years) — skipping aggregated CSV",
            len(selected),
            len(available),
        )
        return pd.concat([results[name] for name in per_year_outputs], ignore_index=True)

    aggregated_df = AggregatedSchema.validate(results["aggregated"])
    AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)
    out = AGGREGATED_DIR / f"cartola_{available[0]}_{available[-1]}.csv"
    aggregated_df.to_csv(out, index=False)
    logger.info("Wrote %s (%d rows)", out, len(aggregated_df))
    return aggregated_df


def launch_ui(
    port: int = DEFAULT_UI_PORT,
    base_dir: str | Path = DEFAULT_UI_BASE_DIR,
    no_migration: bool = False,
    no_open: bool = False,
    settings_file: str = "mini",
    config_file: str | None = None,
) -> None:
    """Launch the Hamilton UI server (requires ``sf-hamilton-ui``).

    Blocks; serves ``http://localhost:<port>``. Defaults mirror Hamilton's
    own ``hamilton ui`` CLI (sqlite-backed mini mode under ``~/.hamilton/db``).

    Args:
        port: TCP port for the Django dev server.
        base_dir: SQLite + blob storage directory.
        no_migration: Skip Django migrations on startup.
        no_open: Skip auto-opening the browser when the server is healthy.
        settings_file: ``"mini"`` (sqlite) or ``"deploy"`` (requires ``config_file``).
        config_file: Required when ``settings_file="deploy"``.

    Raises:
        SystemExit: When ``sf-hamilton-ui`` is not installed.
    """
    try:
        from hamilton_ui import commands  # type: ignore[import-untyped]
    except ImportError as exc:
        raise SystemExit("Hamilton UI is not installed. Run `uv sync --extra ui` and try again.") from exc
    commands.run(
        port=port,
        base_dir=str(base_dir),
        no_migration=no_migration,
        no_open=no_open,
        settings_file=settings_file,
        config_file=config_file,
    )
