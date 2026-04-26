# `src/` — Source Code

This folder hosts the project's executable code:

- [`cartola/`](./cartola) — the Python [Kedro](https://docs.kedro.org/) package (pipelines, nodes, schemas, helpers).
- [`R/`](./R) — legacy R analyses kept for reference.

Tests live at the **repo root** under [`tests/`](../tests).

The rest of this document is a quick-start for setting up a local development
environment and running pipelines and tests, either with a local Python
environment (recommended) or with Docker.

---

## Prerequisites

- **Python 3.12** (the project pins `>=3.12,<3.13`).
- **[uv](https://docs.astral.sh/uv/)** for dependency and environment
  management (`brew install uv` on macOS, or
  `curl -LsSf https://astral.sh/uv/install.sh | sh`).
- **Docker** (optional) — only required for the Docker workflow below.

All commands below assume you are in the **repo root** (`caRtola/`).

---

## Local development setup

Create the virtual environment and install every dependency group
(`dev` + `test` + `lint`):

```bash
uv sync --all-groups
```

This creates `.venv/` at the repo root and installs `cartola` in editable
mode. Activate it with `source .venv/bin/activate`, or just prefix each
command with `uv run` (used throughout this README).

Install the pre-commit hooks (run once after cloning):

```bash
uv run pre-commit install
```

Lint and format on demand:

```bash
uv run ruff check --fix
uv run ruff format
```

---

## Running the pipelines

The Kedro project exposes one pipeline per season (`2014` … `2026`), an
`aggregate` pipeline that combines all seasons, and a `__default__` that
chains everything together.

```bash
uv run kedro run                       # __default__: all years + aggregate
uv run kedro run --pipeline=2024       # only the 2024 season
uv run kedro run --pipeline=aggregate  # only the cross-season aggregation
```

Pipeline inputs and outputs are declared in [`conf/base/`](../conf/base)
(`catalog*.yml`, `parameters*.yml`). Outputs are written under
[`data/`](../data) following Kedro's
[layered convention](https://docs.kedro.org/en/stable/data/data_catalog.html#data-engineering-convention)
(`01_raw/`, `02_intermediate/`, `03_primary/`, `04_feature/`).

Visualise the DAG (opens at <http://127.0.0.1:4141>):

```bash
uv run kedro viz
```

---

## Running the tests

The test suite is split into two groups via the `data` pytest marker:

- **Unit tests** — fast, no data required. Run by default.
- **Data-expectation tests** (`@pytest.mark.data`) — load CSVs from `data/`
  and skip when those files are missing. They validate the output of a real
  pipeline run.

```bash
uv run pytest                  # unit tests + data tests (data tests auto-skip if files are missing)
uv run pytest -m "not data"    # unit tests only (fastest)
uv run pytest -m data          # data-expectation tests only
```

Coverage is collected automatically and the suite fails below 90%
(see `[tool.coverage.report]` in `pyproject.toml`). To inspect the report:

```bash
uv run pytest -m "not data"
open coverage.xml              # or import into your editor / CI viewer
```

To run the data-expectation tests end-to-end, generate the data first:

```bash
uv run kedro run               # produces data/03_primary/* and data/04_feature/aggregated.csv
uv run pytest -m data
```

---

## Docker workflow

The `Dockerfile` at the repo root is a multi-stage build that resolves
dependencies with `uv` against `uv.lock` and ships a slim Python 3.12
runtime image. It does **not** include `tests/`, `notebooks/`, `docs/` or
the legacy R code — only what is needed to run the pipelines.

Build the image:

```bash
make docker-build              # docker build -t cartola:latest .
```

Run the default pipeline. The host's `conf/`, `data/` and `logs/` are
mounted into the container so outputs land back on your machine:

```bash
make docker-run
```

Run a specific pipeline:

```bash
docker run --rm \
  -v "$PWD/conf":/app/conf \
  -v "$PWD/data":/app/data \
  -v "$PWD/logs":/app/logs \
  cartola:latest \
  kedro run --pipeline=2024
```

Drop into an interactive shell inside the image (handy for debugging):

```bash
make docker-shell
```

To run the tests inside the image you'll need to bind-mount the test code
(it isn't shipped with the runtime image) and install the `test` extras —
generally easier to just run `uv run pytest` on the host.
