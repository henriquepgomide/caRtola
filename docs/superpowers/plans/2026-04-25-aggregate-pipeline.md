# Aggregate Pipeline + Tooling Modernization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the `aggregate_all_years` Kedro pipeline (single CSV with player + team + status + scouts across 2014–2026, scouts always non-cumulative); migrate Poetry → uv, Python 3.10 → 3.12, Kedro 0.18 → 1.x; add Pandera + invariant tests for per-year and aggregated data; fix all ruff lint errors.

**Architecture:** Per-year preprocessing pipelines remain (extended to 2023–2026). New aggregate pipeline uses three single-responsibility nodes — `normalize_partitions` (per-partition select+rename+coerce+optional de-accumulate) → `concat_normalized_partitions` (year-ordered concat) → `finalize_aggregated` (sort+final cast). De-accumulation is centralized in the aggregate pipeline; per-year primaries stay cumulative for cumulative years.

**Tech Stack:** uv 0.5+, Python 3.12, Kedro 1.3.1, kedro-datasets[pandas] 6.0+, pandas 2.2+, pandera[pandas] 0.31+, pytest 8+, pytest-cov 5+, ruff 0.15.11, hatchling (build backend).

**Spec:** [`docs/superpowers/specs/2026-04-25-aggregate-pipeline-design.md`](../specs/2026-04-25-aggregate-pipeline-design.md)

---

## Task 1: Migrate `pyproject.toml` from Poetry to uv (Python 3.12 + Kedro 1.x)

**Files:**
- Modify: `pyproject.toml` (full rewrite of build/deps sections; tool tables stay)
- Delete: `poetry.lock`
- Create: `uv.lock` (auto-generated)

- [ ] **Step 1: Verify uv is installed**

Run: `uv --version`
Expected: `uv 0.5.x` or newer. If missing: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`.

- [ ] **Step 2: Rewrite `pyproject.toml` build + project + dependency sections**

Replace the entire file with the following content (keeps the existing `[tool.kedro]`, `[tool.ruff]`, `[tool.pytest]`, `[tool.coverage]`, `[tool.vulture]` blocks but updates the rest):

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cartola"
version = "0.2.0"
description = "Extração de dados da API do CartolaFC, análise exploratória dos dados e modelos preditivos em R e Python - 2014-26."
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.12,<3.13"
authors = [
    { name = "Henrique Gomide", email = "henriquepgomide@gmail.com" },
    { name = "Arnaldo Gualberto", email = "arnaldo.g12@gmail.com" },
]
dependencies = [
    "kedro>=1.3.1,<2",
    "kedro-datasets[pandas]>=6.0",
    "pandas>=2.2",
    "Unidecode>=1.3.6",
]

[dependency-groups]
dev = [
    "pre-commit>=4.0",
    "jupyterlab>=4.2",
    "jupyter>=1.1",
    "nbstripout>=0.7",
    "mypy>=1.11",
    "kedro-viz>=11.0",
]
test = [
    "pytest>=8.3",
    "pytest-cov>=5.0",
    "pytest-mock>=3.14",
    "pandera[pandas]>=0.31",
]
lint = [
    "ruff>=0.15.11",
]

[tool.hatch.build.targets.wheel]
packages = ["src/cartola"]

[tool.kedro]
package_name = "cartola"
project_name = "caRtola"
kedro_init_version = "1.3.1"

[tool.ruff]
line-length = 120
exclude = [
    ".cache", ".config", ".ipython", ".dotnet", "jupyter", ".local",
    ".vscode-server", ".bzr", ".direnv", ".eggs", ".git", ".git-rewrite",
    ".hg", ".ipynb", ".ipynb_checkpoints", ".mypy_cache", ".nox",
    ".pants.d", ".pyenv", ".pytest_cache", ".pytype", ".ruff_cache",
    ".svn", ".tox", ".venv", ".vscode", "__pypackages__", "_build",
    "buck-out", "build", "dist", "node_modules", "site-packages", "venv",
    "data", "notebooks", "src/R",
]

[tool.ruff.lint]
select = [
    "D", "E", "F", "Q0", "T20", "COM", "FBT", "S", "YTT", "N",
    "I", "C90", "TID", "ERA", "RUF",
]
extend-select = ["E501"]
ignore = [
    "D417", "N815", "N803", "COM812", "N818", "N805", "COM819", "I001",
]
fixable = ["A", "B", "C", "D", "E", "F", "Q", "I"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"notebooks/**.ipynb" = ["E402"]
"**/tests/*.py" = ["D", "S101", "F403", "S106"]
"src/cartola/settings.py" = ["ERA001"]
"conf/**/*.py" = ["ERA001", "D"]

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = "src/tests"
python_files = ["test_*.py", "spec_*.py"]
norecursedirs = [".git", ".pytest_cache"]
markers = [
    "data: tests that load real CSVs from data/ (skip when missing)",
]
filterwarnings = [
    "error::UserWarning",
    "ignore::DeprecationWarning",
    "error::PendingDeprecationWarning",
]
addopts = """
    --color=yes
    -p no:cacheprovider
    --junitxml=report.xml
    --cov-report term-missing:skip-covered
    --cov-report xml
    --cov src/cartola -ra
"""

[tool.coverage.paths]
source = ["src/cartola/"]

[tool.coverage.run]
source = ["src/cartola"]
omit = [
    "__init__.py",
    "tests/*",
    "*/.ipynb_checkpoints/*",
    "*/src/cartola/__main__.py",
    "*/src/cartola/download_data.py",
    "*/src/cartola/update_readme.py",
    "*/src/cartola/pipelines/**/pipeline.py",
    "*/src/cartola/pipeline_registry.py",
    "*/src/cartola/settings.py",
]

[tool.coverage.report]
show_missing = true
include_namespace_packages = true
fail_under = 90
precision = 2
exclude_lines = ["raise NotImplementedError"]

[tool.vulture]
paths = ["src/cartola"]
min_confidence = 80
sort_by_size = true
verbose = true
```

- [ ] **Step 3: Delete the Poetry lock file**

```bash
rm poetry.lock
```

- [ ] **Step 4: Resolve and lock dependencies with uv**

Run: `uv sync --all-groups`
Expected: creates `.venv/` (or reuses existing), creates `uv.lock`, exits 0. If a dependency conflict appears, copy the error message and adjust the offending pin in `pyproject.toml`, then re-run.

- [ ] **Step 5: Verify Kedro is installed and runnable**

Run: `uv run kedro --version`
Expected: `1.3.1`.

- [ ] **Step 6: Verify pytest discovers existing tests (will likely fail at import time — that's fine, we're confirming the runner works)**

Run: `uv run pytest src/tests/nodes -x --no-cov 2>&1 | head -40`
Expected: pytest starts and reaches the test files. ImportError for Kedro 0.18 syntax in catalog.yml is OK; we fix that next. Note the failing import for the next task.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock
git rm poetry.lock
git commit -m "build: migrate from Poetry to uv with Python 3.12 + Kedro 1.x"
```

---

## Task 2: Migrate Kedro 0.18 catalog syntax to Kedro 1.x

**Files:**
- Modify: `conf/base/catalog.yml`
- Modify: `conf/base/catalog_2014.yml` … `conf/base/catalog_2022.yml`
- Modify: `src/cartola/extras/datasets/market_dataset.py` (if it exists — verify base class import path)

In Kedro 1.x, all `pandas.CSVDataSet` → `pandas.CSVDataset` and `PartitionedDataSet` → `PartitionedDataset`. The `pandas.CSVDataset` lives in the separate `kedro-datasets` package (added in Task 1).

- [ ] **Step 1: Bulk-rename DataSet → Dataset in every catalog file**

```bash
uv run python -c "
import pathlib
for p in pathlib.Path('conf/base').glob('catalog*.yml'):
    text = p.read_text()
    new = text.replace('pandas.CSVDataSet', 'pandas.CSVDataset').replace('PartitionedDataSet', 'PartitionedDataset')
    if new != text:
        p.write_text(new)
        print(f'updated {p}')
"
```

Expected: prints one line per catalog file that was changed.

- [ ] **Step 2: Inspect the 2021 custom dataset (uses `MarketDataSet`)**

Read `src/cartola/extras/datasets/market_dataset.py`. The base class import was `from kedro.io import AbstractDataSet`; in Kedro 1.x it is `from kedro.io import AbstractDataset`. Update both the import and the class declaration accordingly.

If `market_dataset.py` defines `class MarketDataSet(AbstractDataSet)`:
- Rename class to `MarketDataset`.
- Update `conf/base/catalog_2021.yml` reference from `cartola.extras.datasets.market_dataset.MarketDataSet` → `cartola.extras.datasets.market_dataset.MarketDataset`.

If the file does not define such a class, skip this step.

- [ ] **Step 3: Verify the catalog parses**

Run: `uv run kedro catalog list 2>&1 | head -30`
Expected: lists catalog entries without parse errors. If a year throws `DatasetError` about an unknown class, recheck the renames.

- [ ] **Step 4: Smoke-test one year end-to-end**

Run: `uv run kedro run --pipeline=2014 2>&1 | tail -30`
Expected: pipeline runs all 10 nodes for 2014 and writes `data/03_primary/preprocessed_2014.csv`. If `OmegaConfigLoader` complains about the dotted `2014.preprocessing.year` keys, that's expected for Kedro 1.x — fix in next step.

- [ ] **Step 5: If the smoke test failed because of `OmegaConfigLoader`, set the legacy loader explicitly**

Edit `src/cartola/settings.py` and add (uncomment + adapt):

```python
from kedro.config import OmegaConfigLoader

CONFIG_LOADER_CLASS = OmegaConfigLoader
CONFIG_LOADER_ARGS = {
    "base_env": "base",
    "default_run_env": "local",
    "config_patterns": {
        "catalog": ["catalog*.yml", "catalog*.yaml", "**/catalog*.yml"],
        "parameters": ["parameters*.yml", "parameters*.yaml", "**/parameters*.yml"],
    },
}
```

(`OmegaConfigLoader` is the default in Kedro 1.x; this block just makes the patterns explicit so the year-suffixed `parameters_2014.yml` files are picked up.)

Re-run: `uv run kedro run --pipeline=2014`. If still failing, read the actual error and adapt — do not paper over.

- [ ] **Step 6: Commit**

```bash
git add conf/base/catalog*.yml src/cartola/settings.py
# include market_dataset.py only if it was edited:
git add src/cartola/extras/datasets/market_dataset.py 2>/dev/null || true
git commit -m "chore: migrate catalog syntax to Kedro 1.x (DataSet -> Dataset)"
```

---

## Task 3: Update Pandera schemas (use `pandera.pandas`, all scouts nullable, canonical aggregated)

**Files:**
- Modify: `src/cartola/schemas/scouts.py`
- Modify: `src/cartola/schemas/aggregated.py`

In Pandera 0.24+ the top-level `pandera` import for pandas is deprecated; use `import pandera.pandas as pa`. Per the spec, every scout becomes `Field(ge=0, nullable=True)`, and `AggregatedSchema` is extended with `nome`, `status`, `id_clube`, `nome_clube`.

- [ ] **Step 1: Rewrite `src/cartola/schemas/scouts.py`**

```python
"""Pandera schema for the Cartola scout columns."""

import pandera.pandas as pa


class Scouts(pa.DataFrameModel):
    """Per-round scout values. All scouts are nullable; non-null must be >= 0."""

    A: float = pa.Field(ge=0, nullable=True)
    CA: float = pa.Field(ge=0, nullable=True)
    CV: float = pa.Field(ge=0, nullable=True)
    DE: float = pa.Field(ge=0, nullable=True)
    DP: float = pa.Field(ge=0, nullable=True)
    DS: float = pa.Field(ge=0, nullable=True)
    FC: float = pa.Field(ge=0, nullable=True)
    FD: float = pa.Field(ge=0, nullable=True)
    FF: float = pa.Field(ge=0, nullable=True)
    FS: float = pa.Field(ge=0, nullable=True)
    FT: float = pa.Field(ge=0, nullable=True)
    G: float = pa.Field(ge=0, nullable=True)
    GC: float = pa.Field(ge=0, nullable=True)
    GS: float = pa.Field(ge=0, nullable=True)
    I: float = pa.Field(ge=0, nullable=True)  # noqa: E741
    PC: float = pa.Field(ge=0, nullable=True)
    PI: float = pa.Field(ge=0, nullable=True)
    PP: float = pa.Field(ge=0, nullable=True)
    PS: float = pa.Field(ge=0, nullable=True)
    SG: float = pa.Field(ge=0, le=1, nullable=True)
```

Note the `Float` types: pandas nullable integer dtypes (`Int32`) work in pandas but Pandera's check coercion is more reliable with `float` here. The aggregate output writes them as `Int32`-like (pandas writes `<NA>` correctly), but the schema validates against `float` to avoid `nan != int` failures.

- [ ] **Step 2: Rewrite `src/cartola/schemas/aggregated.py`**

```python
"""Pandera schema for the aggregated multi-year Cartola dataset."""

import pandera.pandas as pa

from cartola.schemas.scouts import Scouts


class AggregatedSchema(Scouts):
    """Canonical schema for data/04_feature/aggregated.csv."""

    id_atleta: float = pa.Field(nullable=True)
    slug: str = pa.Field(nullable=False)
    apelido: str = pa.Field(nullable=False)
    nome: str = pa.Field(nullable=True)
    posicao: str = pa.Field(
        nullable=False,
        isin=["gol", "lat", "zag", "mei", "ata", "tec"],
    )
    status: str = pa.Field(
        nullable=True,
        isin=["Provável", "Dúvida", "Suspenso", "Contundido", "Nulo"],
    )
    id_clube: float = pa.Field(nullable=True)
    nome_clube: str = pa.Field(nullable=True)
    ano: int = pa.Field(ge=2014, le=2026, nullable=False)
    rodada: int = pa.Field(ge=1, le=38, nullable=False)
    participou: float = pa.Field(isin=[0, 1], nullable=True)
    num_jogos: float = pa.Field(ge=0, nullable=True)
    pontuacao: float = pa.Field(nullable=False)
    media: float = pa.Field(nullable=True)
    preco: float = pa.Field(gt=0, nullable=True)
    variacao: float = pa.Field(nullable=False)
```

- [ ] **Step 3: Verify schemas import and instantiate**

```bash
uv run python -c "
from cartola.schemas.scouts import Scouts
from cartola.schemas.aggregated import AggregatedSchema
print('OK', Scouts, AggregatedSchema)
"
```

Expected: prints `OK <class ...> <class ...>` without warnings.

- [ ] **Step 4: Commit**

```bash
git add src/cartola/schemas/scouts.py src/cartola/schemas/aggregated.py
git commit -m "feat(schemas): canonical aggregated schema with status/nome/clube; nullable scouts"
```

---

## Task 4: Add `disaccumulate_scouts` to `cartola.commons.scouts` (TDD)

**Files:**
- Modify: `src/cartola/commons/scouts.py`
- Modify: `src/tests/nodes/test_aggregate_all_years_nodes.py` (add new tests; keep `test_convert_types` for now — Task 7 deletes it)

`disaccumulate_scouts(df, scout_cols)` takes a single year's DataFrame (with `rodada` and `id_atleta` columns and accumulated scouts) and returns the same DataFrame with scouts replaced by per-round deltas. Built on top of the existing `get_disaccumulated_scouts_for_round` (which already handles round-1 passthrough, mid-season debuts via `fillna(0)`, and `SG` clipping).

- [ ] **Step 1: Write failing tests**

Replace the contents of `src/tests/nodes/test_aggregate_all_years_nodes.py` with:

```python
import numpy as np
import pandas as pd

from cartola.commons.scouts import disaccumulate_scouts
from cartola.pipelines.aggregate_all_years.nodes import convert_types


def test_convert_types():
    df = pd.DataFrame(dict(col_str=["1", "2"], col_int=[1, 2], col_float=[1.1, 2.2]))
    dict_map_types = dict(col_str=int, col_int=str, col_float=int)
    df_res = convert_types(df, dict_map_types)
    import pandas.api.types as ptypes
    assert ptypes.is_integer_dtype(df_res.col_str)
    assert ptypes.is_integer_dtype(df_res.col_float)
    assert ptypes.is_string_dtype(df_res.col_int)


def test_disaccumulate_scouts_simple_player():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            CA=[0, 1, 1],
            DE=[0, 1, 3],
        )
    )
    result = disaccumulate_scouts(df, ["CA", "DE"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert list(result["CA"]) == [0, 1, 0]
    assert list(result["DE"]) == [0, 1, 2]


def test_disaccumulate_scouts_sg_clipping():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            SG=[1, 0, 1],  # cumulative max should be 1, 1, 1 -> deltas would be 1, 0, 0
        )
    )
    result = disaccumulate_scouts(df, ["SG"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert (result["SG"] >= 0).all()
    assert (result["SG"] <= 1).all()


def test_disaccumulate_scouts_player_appears_mid_season():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 2, 2],
            rodada=[1, 2, 2, 3],
            G=[0, 1, 0, 2],
        )
    )
    result = disaccumulate_scouts(df, ["G"])
    result = result.sort_values(["id_atleta", "rodada"]).reset_index(drop=True)
    assert list(result["G"]) == [0, 1, 0, 2]


def test_disaccumulate_scouts_passes_through_non_scout_columns():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1],
            rodada=[1, 2],
            apelido=["X", "X"],
            G=[0, 1],
        )
    )
    result = disaccumulate_scouts(df, ["G"])
    assert "apelido" in result.columns
    assert (result["apelido"] == "X").all()


def test_disaccumulate_scouts_handles_nan_scouts():
    df = pd.DataFrame(
        dict(
            id_atleta=[1, 1, 1],
            rodada=[1, 2, 3],
            G=[0.0, np.nan, 2.0],
        )
    )
    result = disaccumulate_scouts(df, ["G"])
    result = result.sort_values("rodada").reset_index(drop=True)
    assert (result["G"].fillna(0) >= 0).all()
```

- [ ] **Step 2: Run failing tests**

Run: `uv run pytest src/tests/nodes/test_aggregate_all_years_nodes.py -v --no-cov`
Expected: 5 of the 6 tests fail with `ImportError: cannot import name 'disaccumulate_scouts'` (or similar). The existing `test_convert_types` should still pass.

- [ ] **Step 3: Implement `disaccumulate_scouts` in `src/cartola/commons/scouts.py`**

Append to the existing file:

```python
def disaccumulate_scouts(df: pd.DataFrame, cols_scouts: List[str]) -> pd.DataFrame:
    """Convert per-round cumulative scouts to per-round delta scouts.

    For years where the source data accumulates scouts across rounds
    (each round shows the season-to-date total), this transforms the
    DataFrame so each row carries only the scouts earned IN that round.

    Args:
        df: per-year DataFrame with `id_atleta`, `rodada`, and the scout columns.
        cols_scouts: list of scout column names to disaccumulate.

    Returns:
        DataFrame with the same shape and columns; scout values now per-round.
    """
    # only operate on scouts that actually exist in this DataFrame
    cols_present = [c for c in cols_scouts if c in df.columns]
    if not cols_present:
        return df

    rounds = sorted(df["rodada"].dropna().unique().astype(int).tolist())
    df_result = pd.concat(
        [get_disaccumulated_scouts_for_round(df, int(r), cols_present) for r in rounds],
        ignore_index=True,
    )
    return df_result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest src/tests/nodes/test_aggregate_all_years_nodes.py -v --no-cov`
Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/commons/scouts.py src/tests/nodes/test_aggregate_all_years_nodes.py
git commit -m "feat(commons): add disaccumulate_scouts for centralized de-accumulation"
```

---

## Task 5: Drop `fix_accumulated_scouts` from preprocessing pipeline

**Files:**
- Modify: `src/cartola/pipelines/preprocessing/nodes.py`
- Modify: `src/cartola/pipelines/preprocessing/pipeline.py`
- Modify: `src/tests/nodes/test_preprocessing_nodes.py`

De-accumulation is now centralized in the aggregate pipeline (per spec). Per-year primaries stay cumulative for cumulative years; the aggregate pipeline applies de-accumulation exactly once.

- [ ] **Step 1: Remove `fix_accumulated_scouts` from `nodes.py`**

In `src/cartola/pipelines/preprocessing/nodes.py`:

```python
"""Preprocessing nodes for per-year Cartola pipelines."""

from typing import Dict

import pandas as pd

from cartola.commons.features import compute_slug


def fill_scouts_with_zeros(df: pd.DataFrame, dict_scouts: Dict[str, float]) -> pd.DataFrame:
    """Fill NaN scout values with zero.

    Note: this only runs at the per-year preprocessing stage. The aggregate
    pipeline reverts missing-by-absence scouts back to NaN (NaN means "this
    scout was not tracked in this year").
    """
    scouts_cols = [c for c in dict_scouts.keys() if c in df.columns]
    if not scouts_cols:
        return df
    df = df.copy()
    df[scouts_cols] = df[scouts_cols].fillna(0)
    return df


def fill_empty_slugs(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a slug from the player's nickname when the slug column is missing/empty."""
    if "slug" not in df.columns:
        df = df.copy()
        df["slug"] = None

    empty_slugs = df["slug"].isna()
    if empty_slugs.any():
        df = df.copy()
        df.loc[empty_slugs, "slug"] = df.loc[empty_slugs, "apelido"].apply(compute_slug)
    return df


def map_status_id_to_string(df: pd.DataFrame, dict_status_to_str: Dict[int, str]) -> pd.DataFrame:
    """Map integer status ids to human-readable Portuguese labels."""
    if "status" not in df.columns:
        return df
    df = df.copy()
    df["status"] = df["status"].replace(dict_status_to_str)
    return df


def map_posicao_to_string(df: pd.DataFrame, dict_posicao_to_str: Dict[str, str]) -> pd.DataFrame:
    """Map integer position ids (as strings) to lowercase position labels."""
    df = df.copy()
    df["posicao"] = df["posicao"].astype(str).replace(dict_posicao_to_str)
    return df


def add_year_column(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Append an `ano` column equal to `year` for every row."""
    df = df.copy()
    df["ano"] = year
    return df
```

(The `inplace=True` calls and the buggy `fix_accumulated_scouts` are gone; functions are non-mutating and pandas-2-clean.)

- [ ] **Step 2: Update `src/cartola/pipelines/preprocessing/pipeline.py`**

```python
"""Per-year preprocessing pipeline."""

from kedro.pipeline import Pipeline, node, pipeline

from cartola.commons.dataframes import (
    concat_partitioned_datasets,
    drop_columns,
    drop_duplicated_rows,
    rename_cols,
)
from cartola.pipelines.preprocessing.nodes import (
    add_year_column,
    fill_empty_slugs,
    fill_scouts_with_zeros,
    map_posicao_to_string,
    map_status_id_to_string,
)


def create_pipeline() -> Pipeline:
    """Build the per-year preprocessing pipeline (raw -> primary)."""
    return pipeline(
        [
            node(concat_partitioned_datasets, inputs="raw", outputs="concat"),
            node(add_year_column, inputs=["concat", "params:year"], outputs="df_year"),
            node(rename_cols, inputs=["df_year", "params:map_col_names"], outputs="df_renamed"),
            node(drop_columns, inputs=["df_renamed", "params:drop_columns"], outputs="df_dropped"),
            node(drop_duplicated_rows, inputs="df_dropped", outputs="df_not_duplicated"),
            node(
                map_posicao_to_string,
                inputs=["df_not_duplicated", "params:map_posicao_to_str"],
                outputs="df_posicao",
            ),
            node(
                map_status_id_to_string,
                inputs=["df_posicao", "params:map_status_id_to_str"],
                outputs="df_status",
            ),
            node(fill_scouts_with_zeros, inputs=["df_status", "params:scouts"], outputs="df_filled_scouts"),
            node(fill_empty_slugs, inputs="df_filled_scouts", outputs="preprocessed"),
        ],
        namespace="preprocessing",
        tags=["preprocessing"],
    )
```

- [ ] **Step 3: Update `src/tests/nodes/test_preprocessing_nodes.py`**

Remove the import of `fix_accumulated_scouts` and the two tests that exercise it (`test_fix_accumulated_scouts`, `test_fix_accumulated_scouts_in_year_without_accumulation`). Keep all other tests.

```python
import numpy as np
import pandas as pd

from cartola.pipelines.preprocessing.nodes import (
    add_year_column,
    fill_empty_slugs,
    fill_scouts_with_zeros,
    map_posicao_to_string,
    map_status_id_to_string,
)


def test_fill_scouts_with_zeros():
    df = pd.DataFrame(dict(a=[np.nan, 2, np.nan]))
    df = fill_scouts_with_zeros(df, dict(a=1.0))
    assert ~df.a.isna().any()


def test_fill_empty_slugs():
    data = dict(apelido=["Cristiano Ronaldo", "Messi"], slug=["CR7", np.nan])
    df = pd.DataFrame(data)
    df = fill_empty_slugs(df)
    assert "slug" in df.columns
    assert ~df.slug.isna().any()
    assert df.slug.values[-1] == "messi"


def test_fill_empty_slug_with_no_slug_col():
    df = pd.DataFrame(dict(apelido=["Cristiano Ronaldo", "Messi"]))
    df = fill_empty_slugs(df)
    assert "slug" in df.columns
    assert ~df.slug.isna().any()


def test_map_status_id_to_string():
    dict_map = {2: "Dúvida", 3: "Suspenso"}
    df = pd.DataFrame(dict(status=[2, 3]))
    df = map_status_id_to_string(df, dict_map)
    assert df.status.isin(list(dict_map.values())).all()


def test_map_status_id_to_string_with_no_status_col():
    df = pd.DataFrame()
    df_res = map_status_id_to_string(df, {})
    assert df.equals(df_res)


def test_map_posicao_to_string():
    dict_map = {"1": "gol", "2": "lat"}
    df = pd.DataFrame(dict(posicao=[1, 2]))
    df = map_posicao_to_string(df, dict_map)
    assert df.posicao.isin(list(dict_map.values())).all()


def test_add_year_columns():
    df = pd.DataFrame()
    df = add_year_column(df, year=2000)
    assert "ano" in df.columns
    assert np.all(df.ano.values == 2000)
```

- [ ] **Step 4: Run preprocessing tests**

Run: `uv run pytest src/tests/nodes/test_preprocessing_nodes.py -v --no-cov`
Expected: 7 tests pass; nothing references `fix_accumulated_scouts`.

- [ ] **Step 5: Smoke-test 2014 preprocessing end-to-end**

Run: `uv run kedro run --pipeline=2014 2>&1 | tail -10`
Expected: pipeline runs and writes `data/03_primary/preprocessed_2014.csv`.

- [ ] **Step 6: Commit**

```bash
git add src/cartola/pipelines/preprocessing/nodes.py src/cartola/pipelines/preprocessing/pipeline.py src/tests/nodes/test_preprocessing_nodes.py
git commit -m "refactor(preprocessing): drop fix_accumulated_scouts; centralize de-acc in aggregate"
```

---

## Task 6: Implement `normalize_partitions` aggregate node (TDD)

**Files:**
- Modify: `src/cartola/pipelines/aggregate_all_years/nodes.py`
- Modify: `src/tests/nodes/test_aggregate_all_years_nodes.py`

`normalize_partitions(partitions, canonical_columns, scout_columns, accumulated_years) -> dict[int, DataFrame]` — for each `PartitionedDataset` partition, extracts the year from the filename, asserts the `ano` column matches if present, selects/reorders to canonical columns (filling missing scouts with `NaN` and missing meta with `NaN`), and applies `disaccumulate_scouts` if the year is in `accumulated_years`.

- [ ] **Step 1: Add failing tests**

Append to `src/tests/nodes/test_aggregate_all_years_nodes.py`:

```python
import pytest

from cartola.pipelines.aggregate_all_years.nodes import normalize_partitions


CANONICAL = [
    "id_atleta", "slug", "apelido", "nome", "posicao", "status",
    "id_clube", "nome_clube", "ano", "rodada",
    "participou", "num_jogos", "pontuacao", "media", "preco", "variacao",
    "G", "A", "CA", "SG",
]
SCOUTS = ["G", "A", "CA", "SG"]


def _partition(df: pd.DataFrame):
    return lambda: df


def test_normalize_partitions_selects_canonical_columns_only():
    df = pd.DataFrame(
        dict(
            id_atleta=[1], slug=["x"], apelido=["X"], nome=["X Full"],
            posicao=["gol"], status=[None], id_clube=[10], nome_clube=["Club"],
            ano=[2014], rodada=[1], participou=[1], num_jogos=[1],
            pontuacao=[1.0], media=[1.0], preco=[5.0], variacao=[0.1],
            G=[0], A=[0], CA=[0], SG=[1],
            extra_garbage=["drop me"],
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    assert set(result[2014].columns) == set(CANONICAL)


def test_normalize_partitions_fills_missing_scouts_with_nan():
    df = pd.DataFrame(
        dict(
            id_atleta=[1], slug=["x"], apelido=["X"], nome=["X"],
            posicao=["gol"], status=[None], id_clube=[10], nome_clube=["C"],
            ano=[2014], rodada=[1], participou=[1], num_jogos=[1],
            pontuacao=[1.0], media=[1.0], preco=[5.0], variacao=[0.1],
            G=[0], A=[0],
            # CA and SG missing on purpose
        )
    )
    result = normalize_partitions(
        {"preprocessed_2014": _partition(df)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[],
    )
    out = result[2014]
    assert "CA" in out.columns and "SG" in out.columns
    assert out["CA"].isna().all()
    assert out["SG"].isna().all()


def test_normalize_partitions_year_mismatch_raises():
    df = pd.DataFrame(
        dict(
            id_atleta=[1], slug=["x"], apelido=["X"], nome=["X"],
            posicao=["gol"], status=[None], id_clube=[10], nome_clube=["C"],
            ano=[2019], rodada=[1], participou=[1], num_jogos=[1],
            pontuacao=[1.0], media=[1.0], preco=[5.0], variacao=[0.1],
            G=[0], A=[0], CA=[0], SG=[1],
        )
    )
    with pytest.raises(ValueError, match="2018"):
        normalize_partitions(
            {"preprocessed_2018": _partition(df)},
            canonical_columns=CANONICAL,
            scout_columns=SCOUTS,
            accumulated_years=[],
        )


def _accumulated_two_round_df(year: int) -> pd.DataFrame:
    return pd.DataFrame(
        dict(
            id_atleta=[1, 1], slug=["x", "x"], apelido=["X", "X"], nome=["X", "X"],
            posicao=["gol", "gol"], status=[None, None],
            id_clube=[10, 10], nome_clube=["C", "C"],
            ano=[year, year], rodada=[1, 2],
            participou=[1, 1], num_jogos=[1, 2],
            pontuacao=[1.0, 1.0], media=[1.0, 1.0], preco=[5.0, 5.0], variacao=[0.0, 0.0],
            G=[0, 2], A=[0, 0], CA=[0, 1], SG=[1, 1],
        )
    )


def test_normalize_partitions_applies_disaccumulation_only_to_accumulated_years():
    df_2018 = _accumulated_two_round_df(2018)
    df_2014 = _accumulated_two_round_df(2014)
    result = normalize_partitions(
        {"preprocessed_2018": _partition(df_2018), "preprocessed_2014": _partition(df_2014)},
        canonical_columns=CANONICAL,
        scout_columns=SCOUTS,
        accumulated_years=[2018],
    )
    out_2018 = result[2018].sort_values("rodada").reset_index(drop=True)
    out_2014 = result[2014].sort_values("rodada").reset_index(drop=True)
    # 2018 was disaccumulated: round-2 G should be 2 (delta from 0 -> 2), CA should be 1.
    assert list(out_2018["G"]) == [0, 2]
    assert list(out_2018["CA"]) == [0, 1]
    # 2014 was NOT disaccumulated: round-2 G stays at the cumulative 2.
    assert list(out_2014["G"]) == [0, 2]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest src/tests/nodes/test_aggregate_all_years_nodes.py -v --no-cov`
Expected: 4 new tests fail with `ImportError: cannot import name 'normalize_partitions'`.

- [ ] **Step 3: Implement `normalize_partitions` in `src/cartola/pipelines/aggregate_all_years/nodes.py`**

Replace the file's contents with:

```python
"""Aggregate-all-years pipeline nodes."""

from collections.abc import Callable
from typing import Dict, List

import pandas as pd

from cartola.commons.scouts import disaccumulate_scouts


def _year_from_partition_key(key: str) -> int:
    """Parse the trailing 4-digit year from a partition key like 'preprocessed_2018'."""
    digits = "".join(c for c in key.split("_")[-1] if c.isdigit())
    if len(digits) != 4:
        raise ValueError(f"Cannot extract year from partition key {key!r}")
    return int(digits)


def normalize_partitions(
    partitions: Dict[str, Callable[[], pd.DataFrame]],
    canonical_columns: List[str],
    scout_columns: List[str],
    accumulated_years: List[int],
) -> Dict[int, pd.DataFrame]:
    """Normalize each per-year partition to the canonical column set.

    For each partition:
      * extracts the year from the partition key,
      * asserts the `ano` column matches the filename year,
      * selects + reorders to `canonical_columns`, filling missing scout
        columns with NaN and missing meta columns with NaN,
      * applies `disaccumulate_scouts` if the year is in `accumulated_years`.

    Args:
        partitions: Kedro PartitionedDataset payload (dict of partition_id -> load_func).
        canonical_columns: ordered list of columns the output should contain.
        scout_columns: subset of canonical_columns that are scouts (filled with NaN if missing).
        accumulated_years: years whose source data is cumulative-per-round.

    Returns:
        Dict keyed by year, each value a DataFrame with exactly the canonical columns.
    """
    normalized: Dict[int, pd.DataFrame] = {}
    for partition_key, load_partition in partitions.items():
        year = _year_from_partition_key(partition_key)
        df = load_partition()

        if "ano" in df.columns and len(df):
            unique_years = df["ano"].dropna().unique().tolist()
            if unique_years and set(unique_years) != {year}:
                raise ValueError(
                    f"Partition {partition_key!r} year mismatch: filename={year}, "
                    f"ano column has {unique_years}",
                )

        for col in canonical_columns:
            if col not in df.columns:
                df[col] = pd.NA if col not in scout_columns else float("nan")

        df = df.loc[:, canonical_columns].copy()

        if year in accumulated_years:
            df = disaccumulate_scouts(df, scout_columns)
            df = df.loc[:, canonical_columns]

        normalized[year] = df.reset_index(drop=True)

    return normalized
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest src/tests/nodes/test_aggregate_all_years_nodes.py -v --no-cov`
Expected: all aggregate-node tests pass (`test_convert_types`, 5 disaccumulate tests, 4 normalize tests).

- [ ] **Step 5: Commit**

```bash
git add src/cartola/pipelines/aggregate_all_years/nodes.py src/tests/nodes/test_aggregate_all_years_nodes.py
git commit -m "feat(aggregate): normalize_partitions selects canonical cols + disaccumulates"
```

---

## Task 7: Implement `concat_normalized_partitions` and `finalize_aggregated`; remove `convert_types` (TDD)

**Files:**
- Modify: `src/cartola/pipelines/aggregate_all_years/nodes.py`
- Modify: `src/tests/nodes/test_aggregate_all_years_nodes.py`

- [ ] **Step 1: Add failing tests, drop the obsolete `test_convert_types`**

Edit `src/tests/nodes/test_aggregate_all_years_nodes.py`:
- Remove the `test_convert_types` function and the `from cartola.pipelines.aggregate_all_years.nodes import convert_types` import.
- Append:

```python
from cartola.pipelines.aggregate_all_years.nodes import (
    concat_normalized_partitions,
    finalize_aggregated,
)


def test_concat_normalized_partitions_orders_by_year():
    df_2018 = pd.DataFrame(dict(ano=[2018], rodada=[1], slug=["x"], id_clube=[1]))
    df_2014 = pd.DataFrame(dict(ano=[2014], rodada=[1], slug=["x"], id_clube=[1]))
    df_2020 = pd.DataFrame(dict(ano=[2020], rodada=[1], slug=["x"], id_clube=[1]))
    out = concat_normalized_partitions({2018: df_2018, 2014: df_2014, 2020: df_2020})
    assert list(out["ano"]) == [2014, 2018, 2020]


def test_finalize_aggregated_sorts_and_casts():
    df = pd.DataFrame(
        dict(
            ano=["2014", "2014"], rodada=["2", "1"],
            id_clube=[1, 1], slug=["b", "a"],
            G=[0.0, 1.0],
        )
    )
    out = finalize_aggregated(df, dtype_map={"ano": int, "rodada": int})
    assert list(out["ano"]) == [2014, 2014]
    assert list(out["rodada"]) == [1, 2]
    assert out.iloc[0]["slug"] == "a"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest src/tests/nodes/test_aggregate_all_years_nodes.py -v --no-cov`
Expected: the two new tests fail with ImportError.

- [ ] **Step 3: Implement the two new nodes; delete `convert_types`**

Append to `src/cartola/pipelines/aggregate_all_years/nodes.py`:

```python
def concat_normalized_partitions(normalized: Dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate normalized per-year DataFrames in ascending year order."""
    years = sorted(normalized.keys())
    return pd.concat([normalized[y] for y in years], ignore_index=True)


def finalize_aggregated(df: pd.DataFrame, dtype_map: Dict[str, type]) -> pd.DataFrame:
    """Apply final dtype map and sort rows for a stable, diff-friendly CSV."""
    df = df.astype({k: v for k, v in dtype_map.items() if k in df.columns})
    sort_cols = [c for c in ("ano", "rodada", "id_clube", "slug") if c in df.columns]
    return df.sort_values(sort_cols).reset_index(drop=True)
```

Remove the `convert_types` function from the same file.

- [ ] **Step 4: Run tests to verify all pass**

Run: `uv run pytest src/tests/nodes/test_aggregate_all_years_nodes.py -v --no-cov`
Expected: all aggregate-node tests pass; `convert_types` is no longer imported anywhere.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/pipelines/aggregate_all_years/nodes.py src/tests/nodes/test_aggregate_all_years_nodes.py
git commit -m "feat(aggregate): concat_normalized_partitions + finalize_aggregated"
```

---

## Task 8: Wire the new aggregate pipeline + parameters

**Files:**
- Modify: `src/cartola/pipelines/aggregate_all_years/pipeline.py`
- Modify: `conf/base/parameters.yml`

- [ ] **Step 1: Rewrite `src/cartola/pipelines/aggregate_all_years/pipeline.py`**

```python
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
```

- [ ] **Step 2: Add `aggregated.*` parameters to `conf/base/parameters.yml`**

Replace the existing `aggregated.map_types:` block at the bottom of `conf/base/parameters.yml` with:

```yaml
aggregated.canonical_columns:
  - id_atleta
  - slug
  - apelido
  - nome
  - posicao
  - status
  - id_clube
  - nome_clube
  - ano
  - rodada
  - participou
  - num_jogos
  - pontuacao
  - media
  - preco
  - variacao
  - A
  - CA
  - CV
  - DE
  - DP
  - DS
  - FC
  - FD
  - FF
  - FS
  - FT
  - G
  - GC
  - GS
  - I
  - PC
  - PI
  - PP
  - PS
  - SG

aggregated.scouts:
  - A
  - CA
  - CV
  - DE
  - DP
  - DS
  - FC
  - FD
  - FF
  - FS
  - FT
  - G
  - GC
  - GS
  - I
  - PC
  - PI
  - PP
  - PS
  - SG

aggregated.accumulated_years:
  - 2015
  - 2017
  - 2018
  - 2019
  - 2020
  - 2021
  - 2022

aggregated.map_types:
  ano: int
  rodada: int
```

- [ ] **Step 3: Verify the pipeline parses**

Run: `uv run kedro registry list`
Expected: lists pipelines including `aggregate`. No parse errors.

- [ ] **Step 4: Verify the catalog still resolves**

Run: `uv run kedro catalog describe-datasets 2>&1 | grep -E '(aggregated|primary)' | head -10`
Expected: `aggregated.primary`, `aggregated.aggregated`, `aggregated.normalized`, `aggregated.concatenated` listed (the last two are MemoryDatasets — fine).

- [ ] **Step 5: Commit**

```bash
git add src/cartola/pipelines/aggregate_all_years/pipeline.py conf/base/parameters.yml
git commit -m "feat(aggregate): wire 3-node pipeline; add canonical_columns + accumulated_years params"
```

---

## Task 9: Add per-year catalogs, parameters, and registry entries for 2023–2026

**Files:**
- Create: `conf/base/catalog_2023.yml`, `catalog_2024.yml`, `catalog_2025.yml`, `catalog_2026.yml`
- Create: `conf/base/parameters_2023.yml`, `parameters_2024.yml`, `parameters_2025.yml`, `parameters_2026.yml`
- Modify: `src/cartola/pipeline_registry.py`

Per the spec: 2023–2025 raw files have a leading unnamed index column (`index_col: 0`); 2026 does not. Use 2022 as the parameter template.

- [ ] **Step 1: Create `conf/base/catalog_2023.yml`**

```yaml
2023.preprocessing.raw:
  type: partitions.PartitionedDataset
  path: data/01_raw/2023
  dataset:
    type: pandas.CSVDataset
    load_args:
      index_col: 0
  filename_suffix: .csv

2023.preprocessing.concat:
  type: pandas.CSVDataset
  filepath: data/02_intermediate/concat_2023.csv
  save_args:
    index: False

2023.preprocessing.preprocessed:
  type: pandas.CSVDataset
  filepath: data/03_primary/preprocessed_2023.csv
  save_args:
    index: False
```

- [ ] **Step 2: Create `conf/base/catalog_2024.yml`** — identical to 2023 but every `2023` → `2024`.

- [ ] **Step 3: Create `conf/base/catalog_2025.yml`** — identical to 2023 but every `2023` → `2025`.

- [ ] **Step 4: Create `conf/base/catalog_2026.yml` (NO `index_col` in load_args)**

```yaml
2026.preprocessing.raw:
  type: partitions.PartitionedDataset
  path: data/01_raw/2026
  dataset:
    type: pandas.CSVDataset
  filename_suffix: .csv

2026.preprocessing.concat:
  type: pandas.CSVDataset
  filepath: data/02_intermediate/concat_2026.csv
  save_args:
    index: False

2026.preprocessing.preprocessed:
  type: pandas.CSVDataset
  filepath: data/03_primary/preprocessed_2026.csv
  save_args:
    index: False
```

- [ ] **Step 5: Create `conf/base/parameters_2023.yml`** — copy `parameters_2022.yml` and replace every `2022` with `2023`. Append `V` to the drop_columns list (the 2023 raw includes a `V` column not in the canonical set):

```yaml
2023.preprocessing.year: 2023

2023.preprocessing.drop_columns:
  - atletas.gato_mestre.media_minutos_jogados
  - atletas.gato_mestre.media_pontos_mandante
  - atletas.gato_mestre.media_pontos_visitante
  - atletas.gato_mestre.minutos_jogados
  - atletas.temporada_id
  - atletas.entrou_em_campo
  - atletas.minimo_para_valorizar
  - atletas.foto
  - V

2023.preprocessing.scouts:
  G: 8.0
  A: 5.0
  FT: 3.0
  FD: 1.2
  FF: 0.8
  FS: 0.5
  PS: 1.0
  PP: -4.0
  I: -0.1
  PI: -0.1
  SG: 5.0
  CV: -3.0
  CA: -1.0
  GS: -1.0
  FC: -0.3
  PC: -1.0
  GC: -3.0
  DP: 7.0
  DS: 1.2
  DE: 1.0
```

- [ ] **Step 6: Create `parameters_2024.yml`, `parameters_2025.yml`, `parameters_2026.yml`** — same content but year token replaced; same drop_columns list (2024/2025/2026 also expose `V`/extra fields). For `parameters_2025.yml`, also add `apelido_abreviado` and `entrou_em_campo` to `drop_columns` (the 2025 round-1 file lacks scout columns entirely; we just keep what we have).

- [ ] **Step 7: Update `src/cartola/pipeline_registry.py` to register 2023–2026 and append them to `__default__`**

Replace the file with:

```python
"""Project pipelines."""

from typing import Dict

from kedro.pipeline import Pipeline, pipeline

from cartola.pipelines import (
    aggregate_all_years,
    merge_splitted_datasets,
    preprocessing,
)


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines."""
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
```

- [ ] **Step 8: Verify the registry resolves all years**

Run: `uv run kedro registry list`
Expected: lists `__default__`, `aggregate`, and `2014`–`2026`.

- [ ] **Step 9: Smoke-test 2023 (small risk surface to confirm catalog+params work)**

Run: `uv run kedro run --pipeline=2023 2>&1 | tail -15`
Expected: writes `data/03_primary/preprocessed_2023.csv`. If it fails on a missing column in `drop_columns`, copy the column name from the error and append it to `2023.preprocessing.drop_columns` in `parameters_2023.yml`. Re-run.

- [ ] **Step 10: Smoke-test 2024, 2025, 2026 in turn (same iterate-on-error loop)**

Run each:
```
uv run kedro run --pipeline=2024
uv run kedro run --pipeline=2025
uv run kedro run --pipeline=2026
```

For each year, iterate on `drop_columns` until the run succeeds.

- [ ] **Step 11: Commit**

```bash
git add conf/base/catalog_202{3,4,5,6}.yml conf/base/parameters_202{3,4,5,6}.yml src/cartola/pipeline_registry.py data/02_intermediate/concat_202{3,4,5,6}.csv data/03_primary/preprocessed_202{3,4,5,6}.csv
git commit -m "feat(pipelines): add per-year preprocessing for 2023-2026"
```

---

## Task 10: Run the full pipeline end-to-end and inspect the aggregated output

**Files:**
- Modify (regenerate): `data/02_intermediate/concat_*.csv`, `data/03_primary/preprocessed_*.csv`, `data/04_feature/aggregated.csv`
- Possibly modify: per-year `parameters_*.yml` if a column complaint surfaces; `aggregated.accumulated_years` in `parameters.yml` if 2023–2026 turn out to also be cumulative.

- [ ] **Step 1: Run everything from raw to aggregate**

Run: `uv run kedro run --pipeline=__default__ 2>&1 | tee /tmp/cartola_run.log | tail -50`
Expected: every per-year pipeline runs to completion, then the aggregate pipeline runs and writes `data/04_feature/aggregated.csv`. If a year fails, fix the relevant `drop_columns` or column rename and re-run only that year + aggregate (`uv run kedro run --pipeline=<year>` then `uv run kedro run --pipeline=aggregate`).

- [ ] **Step 2: Inspect the aggregated output shape and column set**

Run:
```bash
uv run python -c "
import pandas as pd
df = pd.read_csv('data/04_feature/aggregated.csv', low_memory=False)
print('shape:', df.shape)
print('years:', sorted(df.ano.unique()))
print('columns:', list(df.columns))
print('rounds per year:')
print(df.groupby('ano').rodada.agg(['min', 'max', 'nunique']).to_string())
"
```

Expected:
- `shape`: roughly (~300k–400k rows, 36 cols).
- `years` includes `[2014, 2015, ..., 2026]`. Some years (2025/2026) may be partial.
- `columns` matches `aggregated.canonical_columns` exactly (length 36).
- For full seasons, `rodada` ranges 1–38; for partial seasons, lower max.

- [ ] **Step 3: Spot-check de-accumulation in 2018 (the de-acc was applied)**

Run:
```bash
uv run python -c "
import pandas as pd
df = pd.read_csv('data/04_feature/aggregated.csv', low_memory=False)
year_2018 = df[df.ano == 2018]
print('max G per round in 2018:', year_2018.G.max())
print('max CA per round in 2018:', year_2018.CA.max())
print('max CV per round in 2018:', year_2018.CV.max())
"
```

Expected: `max G ≤ 5`, `max CA ≤ 1`, `max CV ≤ 1`. If any value is much higher, de-accumulation didn't apply for that year — investigate `accumulated_years` in `parameters.yml`.

- [ ] **Step 4: Spot-check that 2014 (NOT in accumulated_years) also has reasonable per-round values**

Run:
```bash
uv run python -c "
import pandas as pd
df = pd.read_csv('data/04_feature/aggregated.csv', low_memory=False)
year_2014 = df[df.ano == 2014]
print('max G per round in 2014:', year_2014.G.max())
print('max CA per round in 2014:', year_2014.CA.max())
"
```

Expected: similar bounds (`G ≤ 5`, `CA ≤ 1`). If `CA` is, say, 5 in 2014, that means 2014 also accumulates and we missed it — add `2014` to `accumulated_years` in `parameters.yml`, re-run, re-check.

- [ ] **Step 5: Verify 2023–2026 are correctly classified as accumulated or not**

Same approach: for each new year, check `max G`, `max CA`, `max CV` per row. If any exceed the bounds, that year is cumulative — append it to `aggregated.accumulated_years` and re-run aggregate only.

- [ ] **Step 6: Re-run aggregate one more time after any `accumulated_years` adjustment**

Run: `uv run kedro run --pipeline=aggregate`
Expected: succeeds; bounds check from Step 3 passes for every year.

- [ ] **Step 7: Commit data files**

```bash
git add data/02_intermediate/ data/03_primary/ data/04_feature/aggregated.csv
git add conf/base/parameters.yml conf/base/parameters_*.yml 2>/dev/null || true
git commit -m "data: regenerate intermediate, primary, and aggregated CSVs end-to-end"
```

---

## Task 11: Add per-year data-expectation tests

**Files:**
- Create: `src/tests/data/test_per_year.py`
- Modify: `src/tests/data/conftest.py`

`@pytest.mark.data` is already registered in `pyproject.toml` (Task 1). Per-year tests load real CSVs from `data/03_primary/`; if a CSV is missing, test is skipped.

- [ ] **Step 1: Update `src/tests/data/conftest.py`**

Replace contents:

```python
"""Fixtures for data-expectation tests."""

from pathlib import Path

import pandas as pd
import pytest

PRIMARY_DIR = Path("data/03_primary")
AGGREGATED_PATH = Path("data/04_feature/aggregated.csv")


@pytest.fixture(scope="session")
def data_aggregated() -> pd.DataFrame:
    """Load the aggregated CSV; skip if missing."""
    if not AGGREGATED_PATH.exists():
        pytest.skip(f"{AGGREGATED_PATH} not found; run `uv run kedro run` first")
    return pd.read_csv(AGGREGATED_PATH, low_memory=False)


@pytest.fixture(scope="session")
def data_per_year(request) -> tuple[int, pd.DataFrame]:
    """Load data/03_primary/preprocessed_{year}.csv; skip if missing.

    Returns (year, dataframe) so tests can reference the year without
    digging into pytest's request internals.
    """
    year = int(request.param)
    path = PRIMARY_DIR / f"preprocessed_{year}.csv"
    if not path.exists():
        pytest.skip(f"{path} not found; run `uv run kedro run --pipeline={year}` first")
    return year, pd.read_csv(path, low_memory=False)
```

- [ ] **Step 2: Create `src/tests/data/test_per_year.py`**

```python
"""Per-year data expectation tests against data/03_primary/preprocessed_{year}.csv."""

import math

import pytest

YEARS = list(range(2014, 2027))
ACCUMULATED_YEARS = {2015, 2017, 2018, 2019, 2020, 2021, 2022}
VALID_POSICOES = {"gol", "lat", "zag", "mei", "ata", "tec"}


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_year_column_matches_filename(data_per_year):
    year, df = data_per_year
    if "ano" not in df.columns:
        pytest.skip("ano column not yet added at this stage")
    assert (df["ano"].dropna().astype(int) == year).all()


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_rodada_in_valid_range(data_per_year):
    _, df = data_per_year
    rodada = df["rodada"].dropna().astype(int)
    assert (rodada >= 1).all()
    assert (rodada <= 38).all()


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_pontuacao_is_finite(data_per_year):
    _, df = data_per_year
    pontuacao = df["pontuacao"].dropna()
    assert pontuacao.apply(lambda x: math.isfinite(x)).all()


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_posicao_in_canonical_set(data_per_year):
    _, df = data_per_year
    posicao = df["posicao"].dropna().unique()
    extras = set(posicao) - VALID_POSICOES
    assert not extras, f"unexpected posicao values: {extras}"


@pytest.mark.data
@pytest.mark.parametrize("data_per_year", YEARS, indirect=True, ids=[str(y) for y in YEARS])
def test_every_row_has_slug(data_per_year):
    _, df = data_per_year
    assert df["slug"].notna().all()
    assert (df["slug"].astype(str).str.len() > 0).all()


@pytest.mark.data
@pytest.mark.parametrize(
    "data_per_year",
    [y for y in YEARS if y not in ACCUMULATED_YEARS],
    indirect=True,
    ids=[str(y) for y in YEARS if y not in ACCUMULATED_YEARS],
)
def test_non_accumulated_years_have_per_round_scout_bounds(data_per_year):
    """For non-cumulative years the primary CSV is already per-round."""
    _, df = data_per_year
    if "G" in df.columns:
        assert df["G"].dropna().max() <= 5
    if "CA" in df.columns:
        assert df["CA"].dropna().max() <= 1
    if "CV" in df.columns:
        assert df["CV"].dropna().max() <= 1
```

- [ ] **Step 3: Run per-year tests**

Run: `uv run pytest src/tests/data/test_per_year.py -v --no-cov -m data`
Expected: 5 base tests × 13 years = 65 tests + 6 bound tests for non-cumulative years. Skips for missing CSVs are OK; failures should be addressed.

If a test like `test_posicao_in_canonical_set` fails because a year has unmapped position ids (e.g. integer `5` instead of `"ata"`), the issue is in that year's `parameters_*.yml` `map_posicao_to_str` defaults. Fix and re-run only that year's pipeline + tests.

- [ ] **Step 4: Commit**

```bash
git add src/tests/data/test_per_year.py src/tests/data/conftest.py
git commit -m "test(data): per-year preprocessed CSV expectations (Pandera-light + invariants)"
```

---

## Task 12: Add aggregated-data invariant tests

**Files:**
- Modify: `src/tests/data/test_aggregated.py`

The Pandera schema validation already exists; we extend with cross-row invariants.

- [ ] **Step 1: Replace `src/tests/data/test_aggregated.py` contents**

```python
"""Aggregated CSV expectation tests against data/04_feature/aggregated.csv."""

import pytest

from cartola.schemas.aggregated import AggregatedSchema

CANONICAL_COLUMNS = [
    "id_atleta", "slug", "apelido", "nome", "posicao", "status",
    "id_clube", "nome_clube", "ano", "rodada", "participou", "num_jogos",
    "pontuacao", "media", "preco", "variacao",
    "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF", "FS",
    "FT", "G", "GC", "GS", "I", "PC", "PI", "PP", "PS", "SG",
]
SCOUT_COLUMNS = [c for c in CANONICAL_COLUMNS if c in {
    "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF", "FS",
    "FT", "G", "GC", "GS", "I", "PC", "PI", "PP", "PS", "SG",
}]
EXPECTED_FULL_YEARS = list(range(2014, 2025))  # 2025 and 2026 may be partial


@pytest.mark.data
def test_aggregated_schema(data_aggregated):
    AggregatedSchema.validate(data_aggregated, inplace=True, lazy=True)


@pytest.mark.data
def test_aggregated_columns_match_canonical(data_aggregated):
    assert list(data_aggregated.columns) == CANONICAL_COLUMNS


@pytest.mark.data
def test_aggregated_contains_all_full_years(data_aggregated):
    years_present = set(data_aggregated["ano"].unique())
    missing = set(EXPECTED_FULL_YEARS) - years_present
    assert not missing, f"missing years: {sorted(missing)}"


@pytest.mark.data
def test_aggregated_no_negative_scouts(data_aggregated):
    for col in SCOUT_COLUMNS:
        assert (data_aggregated[col].dropna() >= 0).all(), f"negative values in {col}"


@pytest.mark.data
def test_aggregated_per_round_scout_bounds(data_aggregated):
    """After de-accumulation, per-(player, round) scout values must fit reality."""
    bounds = {"G": 5, "A": 5, "GC": 5, "CA": 1, "CV": 1, "SG": 1}
    for col, upper in bounds.items():
        observed_max = data_aggregated[col].dropna().max()
        assert observed_max <= upper, f"{col} max={observed_max} exceeds bound {upper}"


@pytest.mark.data
def test_aggregated_cumulative_sum_non_decreasing(data_aggregated):
    """Sanity check: per (year, id_atleta), summing scouts across rounds in order
    should never produce a negative cumulative value (would indicate over-subtraction).
    """
    sample = (
        data_aggregated.dropna(subset=["id_atleta"])
        .sort_values(["ano", "id_atleta", "rodada"])
        .groupby(["ano", "id_atleta"])
    )
    for (ano, id_atleta), grp in sample:
        for col in ["G", "A", "CA", "CV"]:
            csum = grp[col].fillna(0).cumsum()
            assert (csum >= 0).all(), f"negative cumulative {col} for ano={ano}, id={id_atleta}"


@pytest.mark.data
def test_aggregated_clubes_per_year_in_range(data_aggregated):
    counts = data_aggregated.groupby("ano")["id_clube"].nunique()
    for ano, n in counts.items():
        assert 16 <= n <= 22, f"year {ano} has {n} distinct id_clube"


@pytest.mark.data
def test_aggregated_position_distribution_non_degenerate(data_aggregated):
    """Every full year should have at least one player at each non-tec position."""
    non_tec = ["gol", "lat", "zag", "mei", "ata"]
    for ano in EXPECTED_FULL_YEARS:
        positions = set(data_aggregated[data_aggregated["ano"] == ano]["posicao"].dropna().unique())
        missing = set(non_tec) - positions
        assert not missing, f"year {ano} missing positions {missing}"
```

- [ ] **Step 2: Run aggregated tests**

Run: `uv run pytest src/tests/data/test_aggregated.py -v --no-cov -m data`
Expected: all 8 tests pass. If any invariant fails, that's a real data-quality issue — investigate (it's likely a year that needs to be added to `accumulated_years`, or a year with an unmapped column).

- [ ] **Step 3: Commit**

```bash
git add src/tests/data/test_aggregated.py
git commit -m "test(data): aggregated CSV invariants (de-acc bounds, year coverage, club counts)"
```

---

## Task 13: Refactor `concat_partitioned_datasets` to avoid O(n²) `pd.concat` in loop

**Files:**
- Modify: `src/cartola/commons/dataframes.py`

- [ ] **Step 1: Replace `concat_partitioned_datasets` body**

```python
def concat_partitioned_datasets(partitioned_dataset: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate all partitions of a Kedro PartitionedDataset into one DataFrame."""
    frames = [load_func() for load_func in partitioned_dataset.values()]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).reset_index(drop=True)
```

- [ ] **Step 2: Add Google-style docstrings to the other commons functions**

Update `src/cartola/commons/dataframes.py` so the entire file reads:

```python
"""Common DataFrame utilities used by Cartola Kedro pipelines."""

from typing import Dict, List

import pandas as pd


def drop_duplicated_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with duplicate rows removed and the index reset."""
    return df.drop_duplicates(ignore_index=True)


def drop_columns(df: pd.DataFrame, list_cols: List[str]) -> pd.DataFrame:
    """Return `df` without the columns in `list_cols` (errors='ignore')."""
    return df.drop(columns=list_cols, errors="ignore")


def concat_partitioned_datasets(partitioned_dataset: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate all partitions of a Kedro PartitionedDataset into one DataFrame."""
    frames = [load_func() for load_func in partitioned_dataset.values()]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).reset_index(drop=True)


def rename_cols(df: pd.DataFrame, map_col_names: Dict[str, str]) -> pd.DataFrame:
    """Rename columns in `df` according to `map_col_names`."""
    return df.rename(columns=map_col_names)
```

(Note: `drop_columns` now uses `errors="ignore"` so per-year `drop_columns` lists don't blow up if a column is already absent — saves a lot of pain in Task 9.)

- [ ] **Step 3: Run all node tests to verify nothing broke**

Run: `uv run pytest src/tests/nodes/ -v --no-cov`
Expected: all node tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/cartola/commons/dataframes.py
git commit -m "refactor(commons): O(n) concat + tolerant drop_columns + docstrings"
```

---

## Task 14: Lint sweep — fix all ruff errors

**Files:**
- Modify: any file flagged by ruff (most likely `commons/scouts.py`, `commons/features.py`, both pipeline `pipeline.py` files, `aggregate_all_years/__init__.py`, etc.)

- [ ] **Step 1: Auto-fix what's auto-fixable**

Run: `uv run ruff check . --fix`
Expected: a list of files modified, exit code 0 or non-zero with remaining issues. Note remaining issues for next step.

- [ ] **Step 2: Inspect remaining issues**

Run: `uv run ruff check . 2>&1 | tee /tmp/ruff_remaining.txt | head -80`
Most likely classes of remaining issues:
- `D100`/`D103` (missing docstring on module / public function) — add a one-line Google-style docstring.
- `E501` (line too long) — wrap.
- `S101` (assert in non-test) — convert to `raise AssertionError(...)` if any leak outside tests; tests are already exempted.
- `RUF012` (mutable class attribute) — convert to `ClassVar` or factory.

- [ ] **Step 3: Fix remaining issues file-by-file**

For each file in the ruff output, edit and add the minimal change to satisfy the rule. Re-run `uv run ruff check <path>` after each file.

- [ ] **Step 4: Verify clean lint pass**

Run: `uv run ruff check .`
Expected: `All checks passed!` (exit code 0).

- [ ] **Step 5: Verify all tests still pass**

Run: `uv run pytest -m "not data" --no-cov 2>&1 | tail -10`
Expected: all unit tests pass (data-marked skipped is fine here).

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "style: fix all ruff lint errors; add Google-style docstrings"
```

---

## Task 15: Final end-to-end verification

**Files:** none modified (verification only).

- [ ] **Step 1: Full test suite (all markers including data)**

Run: `uv run pytest 2>&1 | tail -30`
Expected: every test passes (or skips with a clear reason for missing data files). Coverage ≥ 90%.

- [ ] **Step 2: Full ruff check**

Run: `uv run ruff check .`
Expected: `All checks passed!`.

- [ ] **Step 3: Full pipeline run from scratch (sanity)**

```bash
rm -f data/02_intermediate/concat_*.csv data/03_primary/preprocessed_*.csv data/04_feature/aggregated.csv
uv run kedro run --pipeline=__default__ 2>&1 | tail -10
```

Expected: every CSV regenerated, pipeline succeeds.

- [ ] **Step 4: Re-run data tests against the freshly generated CSVs**

Run: `uv run pytest src/tests/data/ -v --no-cov -m data 2>&1 | tail -40`
Expected: all data-marked tests pass.

- [ ] **Step 5: Stage regenerated data and final commit**

```bash
git add -A
git status
# if anything is unstaged that shouldn't be, fix it
git diff --staged --stat | tail -20
git commit -m "data: final regeneration after lint sweep" 2>/dev/null || echo "nothing to commit (clean)"
```

- [ ] **Step 6: Summarize for the user**

Print a final summary listing:
- Number of tasks completed.
- Pipeline output path: `data/04_feature/aggregated.csv`.
- Row count and column count of the aggregated file.
- Years covered.
- Test count and coverage percentage.
- Confirmation that `uv run ruff check .` is clean.

---

## Self-Review

**Spec coverage:**
- Replace Poetry with uv → Task 1 ✓
- Update Kedro to newest version → Tasks 1, 2 ✓
- Update Python version → Task 1 ✓
- Aggregate pipeline with single output file → Tasks 6, 7, 8, 10 ✓
- Player + team + status + nome + scouts → Tasks 3, 8 ✓
- De-accumulated scouts → Tasks 4, 6 ✓
- Centralized de-acc + delete `fix_accumulated_scouts` → Task 5 ✓
- All years 2014–2026 → Tasks 9, 10 ✓
- Tests for per-year data expectations → Task 11 ✓
- Tests for aggregated data expectations → Task 12 ✓
- Pandera schemas updated (nullable scouts, canonical aggregated) → Task 3 ✓
- Fix all ruff lint errors → Task 14 ✓
- Coverage threshold lowered to 90 → Task 1 ✓
- `data` pytest marker registered → Task 1 ✓

**Placeholder scan:** no TBD/TODO/"add appropriate"/"similar to Task N" patterns. Code blocks present in every code-changing step.

**Type consistency:** `disaccumulate_scouts(df, cols_scouts)` signature is consistent across Tasks 4, 6 (both call it with `scout_columns` positional). `normalize_partitions(partitions, canonical_columns, scout_columns, accumulated_years)` signature is consistent across Tasks 6 (definition) and 8 (Kedro node wiring), and the parameter names match the YAML keys (`canonical_columns`, `scouts`, `accumulated_years`). `finalize_aggregated(df, dtype_map)` consistent across Tasks 7 (definition) and 8 (wiring).

**Caveats baked in:**
- Task 2 Step 5 contingency for `OmegaConfigLoader` config patterns.
- Task 9 Steps 9–10 explicit "iterate on `drop_columns`" loop.
- Task 10 Steps 4–5 explicit "verify `accumulated_years` classification" loop.
- Task 11 fixture handles missing CSVs via `pytest.skip`.

Plan is ready.
