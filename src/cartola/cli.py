"""Typer CLI for the Cartola aggregation pipeline.

Commands:
    aggregate: Run the pipeline and write per-year + aggregated CSVs.
    viz: Launch the Hamilton UI (requires the ``ui`` extra).
"""

import logging

import typer

from cartola.aggregation import driver

app = typer.Typer(add_completion=False, no_args_is_help=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def _parse_years(raw: str | None) -> list[int] | None:
    if raw is None:
        return None
    return [int(y.strip()) for y in raw.split(",") if y.strip()]


@app.command()
def aggregate(
    years: str | None = typer.Option(
        None,
        "--years",
        help="Comma-separated list of years to process. Default: all configured years.",
    ),
    track: bool = typer.Option(
        False,
        "--track",
        help="Send the run to the Hamilton UI tracker (requires `uv sync --extra ui`).",
    ),
) -> None:
    """Run the aggregation pipeline."""
    selected = _parse_years(years)
    df = driver.run(years=selected, track=track)
    typer.echo(f"Done. {len(df)} rows total.")


@app.command()
def viz() -> None:
    """Launch the Hamilton UI (http://localhost:8241)."""
    driver.launch_ui()


if __name__ == "__main__":
    app()
