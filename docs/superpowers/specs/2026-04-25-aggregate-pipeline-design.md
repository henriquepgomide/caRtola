# Aggregate-all-years pipeline + tooling modernization

**Status:** approved (brainstorm), awaiting plan
**Author:** Arnaldo Gualberto (with Cursor agent)
**Date:** 2026-04-25
**Branch:** `feat/aggregate-pipeline`

## Goal

Finish the `aggregate_all_years` Kedro pipeline so the project produces a
single `data/04_feature/aggregated.csv` with player + team + scouts columns
across every year for which we have raw data (2014–2026), with scouts always
in per-round (non-cumulative) form.

Bundled tooling work, scoped together because the migration unblocks the
pipeline work:

- Replace Poetry with `uv`.
- Bump Kedro from `0.18.2` to the latest `1.x`.
- Bump Python from `3.10` to `3.12`.
- Add data-expectation tests (per year + aggregated).
- Fix all ruff lint errors.

## Non-goals

- No refactor of the per-year `merge_splitted_datasets` pipelines.
- No new feature engineering beyond the canonical column set.
- No change to the upstream R scripts under `src/R/`.
- No CI workflow rewrite beyond what's required for `uv` and Python 3.12.

## Architecture overview

```
data/01_raw/{year}/*                     ┐
        │                                │
        ▼                                │  per-year pipelines
{year}.merge.*  (only 2014–2016)         │  (existing pattern,
        │                                │   extended to 2023–2026)
        ▼                                │
{year}.preprocessing.preprocessed   ─────┘
   = data/03_primary/preprocessed_{year}.csv
        │
        ▼
aggregated.primary  (PartitionedDataset over data/03_primary)
        │
        ▼
normalize_partitions  ── per-partition: select canonical cols,
        │                add missing scouts as 0, coerce types,
        │                de-accumulate if year ∈ ACCUMULATED_YEARS
        ▼
concat_normalized_partitions  (year-ascending, deterministic)
        │
        ▼
finalize_aggregated  (sort rows, final dtype map)
        │
        ▼
aggregated.aggregated = data/04_feature/aggregated.csv
```

## Tooling & environment

### Replace Poetry with uv

- Convert `pyproject.toml` to PEP 621 (`[project]` table). Move dev/test/lint
  groups under `[dependency-groups]` (uv-native) instead of
  `[tool.poetry.group.*.dependencies]`.
- Switch `[build-system]` from `poetry-core` to `hatchling` (uv's
  recommended backend; minimal config — no Poetry leftovers).
- Replace `poetry.lock` with `uv.lock`.
- Update CI workflows (`.github/workflows/*`) to install uv and run
  `uv sync` / `uv run` instead of `poetry install` / `poetry run`.

### Python 3.12

- `requires-python = ">=3.12"`.
- Drop the `numba<0.59` constraint (no consumer of numba in the runtime
  code path; it was a transitive pin for an old `ydata-profiling`).

### Kedro 1.x

- `kedro>=1.0,<2`.
- Add `kedro-datasets[pandas]` (datasets moved out of core in 0.19+).
- Catalog migration: `PartitionedDataSet` → `PartitionedDataset`,
  `pandas.CSVDataSet` → `pandas.CSVDataset` in every `conf/base/catalog*.yml`.
- `[tool.kedro] project_version` updated to the new Kedro version.
- Bump `kedro-viz` to a 1.x-compatible version. Drop `kedro-docker` (unused).
- Verify `settings.py` (which is mostly commented-out template) still works
  with the new defaults via a `kedro run --pipeline=2014` smoke test.

### Pandas 2 / Pandera

- `pandas>=2.2`.
- `pandera>=0.20`.
- Replace `df.replace(..., inplace=True)` and `df.fillna(..., inplace=True)`
  on slices with non-inplace assignments — fixes both ruff (eventually) and
  the project's strict pytest warning filter (`error::PendingDeprecationWarning`).

## Aggregate pipeline (the main deliverable)

### Nodes

Three single-responsibility nodes in
`src/cartola/pipelines/aggregate_all_years/nodes.py`:

```python
def normalize_partitions(
    partitions: dict[str, Callable[[], pd.DataFrame]],
    canonical_columns: list[str],
    scout_columns: list[str],
    accumulated_years: list[int],
) -> dict[int, pd.DataFrame]: ...

def concat_normalized_partitions(
    normalized: dict[int, pd.DataFrame],
) -> pd.DataFrame: ...

def finalize_aggregated(
    df: pd.DataFrame,
    dtype_map: dict[str, str],
) -> pd.DataFrame: ...
```

### `normalize_partitions` behaviour (per partition)

1. Extract `year` from the partition key (filename `preprocessed_2018` →
   `2018`). Single source of truth — no implicit assumption that the `ano`
   column exists.
2. Assert `df["ano"].unique() == [year]` if the column exists. Mismatch
   raises `ValueError` (loud failure on data integrity).
3. **Select canonical columns only.** Drop everything else by omission.
   Missing scout columns are added as `NaN` (not `0`) — being absent from
   the source year means "we don't know", not "zero". Missing player/team
   meta columns are also added as `NaN`. Pandas nullable integer dtypes
   (`Int32`) are used for scouts so they can hold `NaN` without being
   silently coerced to `float64`.
4. **Coerce types** to the partition-level dtype map (no final cast yet —
   that's `finalize_aggregated`'s job; this only ensures the DataFrame is
   concat-compatible).
5. **De-accumulate** if `year in accumulated_years` by calling
   `cartola.commons.scouts.disaccumulate_scouts(df, scout_columns)`.

### Output ordering

- `concat_normalized_partitions` iterates `sorted(normalized.keys())` so
  the resulting CSV is deterministic and diff-friendly across runs.
- `finalize_aggregated` then `df.sort_values(["ano", "rodada", "id_clube",
  "slug"]).reset_index(drop=True)`.

### De-accumulation centralization

- Move/extract `disaccumulate_scouts(df, scout_cols)` to
  `cartola/commons/scouts.py`. Implementation reuses the existing
  `get_disaccumulated_scouts_for_round` (round-aware, already correct for
  the SG clip and "first appearance mid-season" cases).
- **Delete** `fix_accumulated_scouts` from
  `cartola/pipelines/preprocessing/nodes.py` and from the preprocessing
  pipeline DAG. Per-year primary CSVs stay cumulative for the cumulative
  years; de-accumulation is applied exactly once, in the aggregate
  pipeline. This eliminates the bitwise-NOT bug and the "did this file
  already get de-accumulated?" question.
- Update `tests/nodes/test_preprocessing_nodes.py`: remove the two
  `test_fix_accumulated_scouts*` tests. Add `test_disaccumulate_scouts*`
  in `tests/nodes/test_aggregate_all_years_nodes.py` covering the same
  cases.

### Parameters

In `conf/base/parameters.yml` under `aggregated.*`:

```yaml
aggregated.canonical_columns: [ ... ordered list, see Schema ... ]
aggregated.scouts: [A, CA, CV, DE, DP, DS, FC, FD, FF, FS, FT, G, GC, GS, I, PC, PI, PP, PS, SG]
aggregated.accumulated_years: [2015, 2017, 2018, 2019, 2020, 2021, 2022]
aggregated.map_types: { ano: int, rodada: int, ...full dtype map... }
```

`accumulated_years` is verified for 2023–2026 during implementation by
spot-checking a couple of rounds (round 2 totals > round 1 totals for the
same player → cumulative). New cumulative years get appended.

### Catalog (Kedro 1.x syntax)

```yaml
aggregated.primary:
  type: PartitionedDataset
  path: data/03_primary
  dataset:
    type: pandas.CSVDataset
  filename_suffix: .csv

aggregated.aggregated:
  type: pandas.CSVDataset
  filepath: data/04_feature/aggregated.csv
  save_args:
    index: False
```

## New years 2023–2026

- Add `conf/base/catalog_2023.yml` … `catalog_2026.yml` mirroring
  `catalog_2022.yml`. The 2026 raw files don't have an unnamed-index
  column (visible from `data/01_raw/2026/rodada-1.csv`); set
  `load_args.index_col` per year based on quick inspection.
- Add `conf/base/parameters_2023.yml` … `parameters_2026.yml`. Start
  from `parameters_2022.yml` and adjust per-year `drop_columns` after a
  smoke run.
- Drop the 2026-only `V` column via `drop_columns` (not part of the
  canonical scout set).
- Add `pipe_2023` … `pipe_2026` to `pipeline_registry.py` and append them
  to `__default__`. `__default__` ends with the aggregate pipeline so a
  single `kedro run` produces every CSV.

## Canonical schema

Final aggregated columns, in CSV order:

| Group       | Column        | Type           | Nullable |
| ----------- | ------------- | -------------- | -------- |
| Player ID   | `id_atleta`   | `Int64`        | yes      |
| Player ID   | `slug`        | `string`       | no       |
| Player ID   | `apelido`     | `string`       | no       |
| Player ID   | `nome`        | `string`       | yes      |
| Player meta | `posicao`     | `string`       | no       |
| Player meta | `status`      | `string`       | yes      |
| Team        | `id_clube`    | `Int64`        | yes      |
| Team        | `nome_clube`  | `string`       | yes      |
| Time        | `ano`         | `int`          | no       |
| Time        | `rodada`      | `int` (1..38)  | no       |
| Game        | `participou`  | `Int8` (0/1)   | yes      |
| Game        | `num_jogos`   | `Int16` (≥0)   | yes      |
| Game        | `pontuacao`   | `float`        | no       |
| Game        | `media`       | `float`        | yes      |
| Game        | `preco`       | `float` (>0)   | yes      |
| Game        | `variacao`    | `float`        | yes      |
| Scouts (20) | A, CA, CV, DE, DP, DS, FC, FD, FF, FS, FT, G, GC, GS, I, PI, PP, SG | `Int32` (≥0 when not null) | yes |
| Scouts      | PC, PS        | `float` (≥0 when not null) | yes |

All scout columns are nullable. A `NaN` means "this scout was not tracked
in this year's source data". When a scout *is* present, it must be `≥ 0`
(enforced by Pandera's `Field(ge=0, nullable=True)` and a pytest invariant
`(df[col].dropna() >= 0).all()`).

`posicao ∈ {gol, lat, zag, mei, ata, tec}`.
`status ∈ {Provável, Dúvida, Suspenso, Contundido, Nulo} ∪ {NaN}`.

The `cartola/schemas/aggregated.py` Pandera model is updated to match.
`cartola/schemas/scouts.py` is updated so every scout is
`Field(ge=0, nullable=True)` (previously the 18 "core" scouts were
non-nullable). This reflects the rule above: missing → `NaN`, present →
`≥ 0`.

## Tests

### Layer 1 — node unit tests (`src/tests/nodes/`)

Pure-Python, fast, fixture-driven:

- `test_disaccumulate_scouts_simple_player`
- `test_disaccumulate_scouts_sg_clipping`
- `test_disaccumulate_scouts_player_appears_mid_season`
- `test_normalize_partition_canonical_columns`
- `test_normalize_partition_year_mismatch_raises`
- `test_normalize_partition_applies_disaccumulation_only_for_accumulated_years`
- `test_concat_normalized_partitions_preserves_year_order`
- `test_finalize_aggregated_dtypes_and_sort`

### Layer 2 — per-year data expectations (`src/tests/data/test_per_year.py`)

Parametrized over `year ∈ [2014..2026]`. For each year, load
`data/03_primary/preprocessed_{year}.csv` and assert:

- Pandera `PerYearSchema` (relaxed superset of `AggregatedSchema`).
- `ano == year` for every row.
- `rodada ∈ [1, max_observed]`.
- `pontuacao` is finite.
- `posicao ∈ {gol, lat, zag, mei, ata, tec}`.
- Every row has a non-empty `slug`.
- For non-cumulative years only: per-(player, round) scout bounds (`G ≤ 5`,
  `A ≤ 5`, `CA ≤ 1`, `CV ≤ 1`).

### Layer 3 — aggregated expectations (`src/tests/data/test_aggregated.py`)

Loads `data/04_feature/aggregated.csv`:

- Pandera `AggregatedSchema.validate(..., lazy=True)`.
- All expected years present (full 2014–2024; 2025/2026 if data is there).
- Every (year, round) combination has at least one row, where round ranges
  within that year's observed maximum.
- Column set equals exactly the canonical list (no extras).
- **De-accumulation invariants:** per-(player, round) bounds for
  `G, A, GC, CA, CV`; `SG ∈ {0, 1}`; no negative values in any scout
  column (`(df[scout].dropna() >= 0).all()` for each scout).
- Cumulative sums of any scout per (year, id_atleta) are non-decreasing
  across rounds (computed on `.fillna(0)` for the test only).
- `posicao` distribution per year is non-degenerate.
- 16 ≤ distinct `id_clube` per year ≤ 22.

### Test infrastructure

- New `pytest` marker `data` registered in `[tool.pytest.ini_options]
  markers`. Layer 2/3 tests are `@pytest.mark.data`.
- `src/tests/data/conftest.py` provides the `data_aggregated` fixture
  (already exists) and a parametrized `data_per_year` fixture. If a CSV
  is missing, the test `pytest.skip`s.
- Coverage target lowered from `100` to `90`. Add
  `cartola/pipelines/**/pipeline.py` and `cartola/__main__.py` to the
  `omit` list.

## Lint cleanup

Run `uv run ruff check .` and fix everything. Explicit decisions:

- Add Google-style docstrings to public functions in `commons/*.py` and
  the new aggregate nodes (`D` rule).
- Refactor the `pd.concat`-in-loop in `concat_partitioned_datasets` to a
  single `pd.concat([f() for f in partitions.values()], ignore_index=True)`.
- Replace inplace pandas operations with assignments.
- `cartola/settings.py` (Kedro template scaffolding) gets per-file-ignore
  for `ERA001`.
- Bump ruff to `>= 0.6` (compatible with Python 3.12).

## Error handling

- **Loud failure on data integrity:** partition filename year ≠ `ano`
  column → `ValueError`.
- **Graceful skip on optional columns:** missing scouts → `NaN`; missing
  player/team meta → `NaN`. Never crash because a year lacks an optional
  column. The `≥ 0` rule applies only to non-null values.
- **Pandera validation** in tests uses `lazy=True` so all violations
  surface in one shot.

## Implementation order

1. Migrate `pyproject.toml` to uv + Python 3.12 + Kedro 1.x. Verify
   `uv run kedro --version` and `uv run pytest src/tests/nodes` pass.
2. Add 2023–2026 catalogs/parameters/registry entries.
3. Refactor preprocessing: delete `fix_accumulated_scouts` from nodes and
   from the preprocessing pipeline DAG. Update its tests.
4. Implement aggregate pipeline nodes, schema, parameters.
5. `uv run kedro run --pipeline=__default__` to regenerate every CSV from
   raw → aggregated. Iterate on per-year `drop_columns` if any year
   throws.
6. Add per-year + aggregated data-expectation tests; iterate until green.
7. `uv run ruff check . --fix` then fix remaining issues by hand.
8. Run the full test suite (`uv run pytest`) and lint
   (`uv run ruff check .`).
9. Commit in logical chunks (uv migration, then aggregate pipeline, then
   tests/lint).

## Open questions / risks

- **Cumulative-year detection for 2023–2026.** We will spot-check during
  implementation. If any of these years is also cumulative, append it to
  `aggregated.accumulated_years`.
- **Kedro 1.x migration surprises.** Mitigated by per-step smoke tests.
  If a major incompatibility appears (e.g. `ConfigLoader` rework requires
  `OmegaConfigLoader` setup that breaks template), we fall back to the
  latest 0.19.x and document why.
- **`kedro-viz` 1.x compatibility** is mentioned in their changelog but
  may lag a release behind core Kedro. If incompatible at implementation
  time, drop `kedro-viz` from dev deps with a TODO to re-add.
- **Existing primary CSVs in git** (`data/03_primary/preprocessed_*.csv`)
  will all be regenerated. The diff will be large and that's expected.
