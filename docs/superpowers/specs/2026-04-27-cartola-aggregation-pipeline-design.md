# Cartola FC Aggregation Pipeline — Design Doc

- **Date**: 2026-04-27
- **Status**: Approved (brainstorming phase complete)
- **Owner**: arnaldo.gualberto
- **Replaces**: Existing Kedro pipeline (to be removed)

---

## 1. Problem

The repo contains raw Cartola FC CSVs from 2014–2026 in heterogeneous shapes (multi-file per-year, single-file, per-round files), with column names that drift across years and three scouts that were renamed (`PE`→`PI`, `RB`→`DS`, `DD`→`DE`). The existing Kedro pipeline:

- Doesn't aggregate years into a single dataset.
- Only registers years up to 2022 (missing 2023–2026).
- Has an empty `aggregate_all_years` package (placeholder, never implemented).
- Brings significant infrastructure overhead (Kedro framework, Poetry, kedro-docker, kedro-viz) for a workflow that runs only locally.
- Doesn't disaccumulate scouts that the Cartola API returns cumulatively (2015, 2017, 2018, 2019, 2020, 2021, 2022).

We need a single, harmonized, per-(year, round, player) DataFrame covering 2014–2026, produced by a maintainable local pipeline.

## 2. Goals

- Produce a single aggregated CSV `data/04_aggregated/cartola_2014_2026.csv` (38 columns, schema in §6) covering all years.
- Per-year intermediate CSVs persisted to `data/03_primary/cartola_<year>.csv` for inspection/debug.
- Disaccumulate scouts for the years where the API returns cumulative values.
- Replace Kedro entirely with a lighter, function-based pipeline framework.
- Use `uv` as the package manager.
- Be trivially extensible: adding year N+1 = single config entry.
- Be testable at unit, integration, and data-quality levels.

## 3. Non-Goals

- No production deployment (no Docker, no Kubernetes, no cloud).
- No database; data stays as CSV.
- No scheduled runs / orchestration daemon — pipeline is run manually.
- No ML modeling, training, or serving — only aggregation.
- No changes to R code in `src/R/` or to existing notebooks.

## 4. Constraints

- Python 3.10+ (current project pins `3.10.*`).
- Local-only execution.
- Pure CSV input/output (no DBs).
- Output must be inspectable by humans (CSV, not Parquet).
- Per-year code reuse is a hard requirement — same logic should not be duplicated across years.

## 5. Tooling Decisions

| Concern | Choice | Rationale |
|---|---|---|
| Pipeline framework | **Hamilton** | Function-as-node model, `@parameterize` for per-year reuse, DAG inferred from signatures, lightweight, optional Hamilton UI |
| Package manager | **uv** | User requirement |
| CLI | **Typer** | Type-hinted, simple, integrates with `uv run` |
| Data validation | **Pandera** | Pythonic schemas, runs in pytest, no infra; rejected Soda for being SQL/YAML-heavy and overkill |
| Test framework | **pytest** | Already used in the project |
| Visualization | **Hamilton UI** (`sf-hamilton-ui`) | Interactive DAG, run history, lineage; launched via `cartola viz` |
| DataFrame library | **pandas** | Already used; no need to switch |

### Tools considered and rejected

- **Kedro**: too heavy, framework adds ceremony for a 2-stage pipeline.
- **ZenML**: MLOps-focused, Stack/ArtifactStore concepts add no value here.
- **Metaflow**: good `resume` semantics but heavier than Hamilton; flow-class boilerplate.
- **Ploomber**: YAML-heavy, less Pythonic.
- **Dagster**: closer to Hamilton but requires running a server for the UI.
- **DuckDB / dbt**: SQL would make schema mapping verbose given 13 years of drift.
- **Soda**: data observability tool; overkill for local schema validation, would add DuckDB dep.

## 6. Aggregated Schema (38 columns)

Canonical schema produced by the pipeline. Column order is fixed and follows logical groups (context → team → player → game state → scouts).

### Contexto (5)
| # | Column | Dtype | Notes |
|---|---|---|---|
| 1 | `ano` | `int16` | Added by pipeline |
| 2 | `rodada` | `int8` | From `Rodada` / `atletas.rodada_id` |
| 3 | `id_clube` | `Int32` (nullable) | Always rebuilt from `nome_clube` via `TEAM_NAME_TO_ID` map (see §6.1). Nullable only when name can't be resolved. |
| 4 | `nome_clube` | `string` | From `Nome` / `atletas.clube.id.full.name` |
| 5 | `id_atleta` | `int64` | From `AtletaID` / `atletas.atleta_id` |

### Info do jogador (10)
| # | Column | Dtype | Availability |
|---|---|---|---|
| 6 | `nome` | `string` | NaN for 2014–2016 |
| 7 | `apelido` | `string` | All years |
| 8 | `apelido_abreviado` | `string` | 2022+ only |
| 9 | `slug` | `string` | Computed via `compute_slug(apelido)` if absent |
| 10 | `foto` | `string` | 2017+ |
| 11 | `posicao` | `string` | Label: `gol`, `zag`, `lat`, `mei`, `ata`, `tec` |
| 12 | `status` | `string` | Label: `Provável`, `Dúvida`, `Suspenso`, `Contundido`, `Nulo`. NaN pre-2017 |
| 13 | `pontuacao` | `float32` | All years |
| 14 | `media` | `float32` | All years |
| 15 | `preco` | `float32` | All years |

### Game state (2)
| # | Column | Dtype | Availability |
|---|---|---|---|
| 16 | `variacao` | `float32` | All years |
| 17 | `num_jogos` | `Int16` (nullable) | NaN for 2017 |

### Scouts harmonizados (21)
`float32` (NaN where the scout doesn't exist for that year — see §7.6).

`A`, `CA`, `CV`, `DE`, `DP`, `DS`, `FC`, `FD`, `FF`, `FS`, `FT`, `G`, `GC`, `GS`, `I`, `PC`, `PI`, `PP`, `PS`, `SG`, `V`

**Renames applied** (legacy → canonical):
- `PE` → `PI`
- `RB` → `DS`
- `DD` → `DE`

**Dropped columns** (not part of the canonical schema):
- `participou` (legacy 2014–2016; can be inferred from `num_jogos > 0`)
- `minimo_para_valorizar` (2022+ only; not needed for cross-year analysis)
- `entrou_em_campo` (2024+ only; not needed for cross-year analysis)
- `Posicao`, `Jogos`, `Partida`, `Mando`, `Titular`, `Substituido`, `TempoJogado`, `Nota` (2014 extras not part of the cross-year canonical schema)
- `athletes.atletas.scout` (2017 noise column)
- Original CSV index columns

### 6.1 Team name → id_clube map (`TEAM_NAME_TO_ID`)

Lives in `aggregation/schema.py`. Used to **always rebuild** `id_clube` from `nome_clube` (after normalizing: uppercase + strip accents). This bypasses the buggy `atletas.clube_id` in 2018 (which contains ambiguous abbreviations like `ATL` for both Atlético-MG and Atlético-PR).

Key→id mapping (full names + common abbreviations, both pointing to the canonical id):

```python
TEAM_NAME_TO_ID = {
    "AME": 327, "AMÉRICA-MG": 327,
    "ATHLÉTICO-PR": 293, "ATLÉTICO-PR": 293, "CAP": 293,
    "ATLÉTICO-GO": 373,
    "CAM": 282, "ATLÉTICO-MG": 282,
    "AVA": 314, "AVAÍ": 314,
    "BAH": 265, "BAHIA": 265,
    "BOT": 263, "BOTAFOGO": 263,
    "BRAGANTINO": 280,
    "CEA": 354, "CEARÁ": 354,
    "CFC": 294, "CORITIBA": 294,
    "CHA": 315, "CHAPECOENSE": 315,
    "COR": 264, "CORINTHIANS": 264,
    "CRI": 288,
    "CRU": 283, "CRUZEIRO": 283,
    "CSA": 341,
    "CUIABÁ": 1371,
    "FIG": 316, "FIGUEIRENSE": 316,
    "FLA": 262, "FLAMENGO": 262,
    "FLU": 266, "FLUMINENSE": 266,
    "FORTALEZA": 356,
    "GOI": 290, "GOIÁS": 290,
    "GRE": 284, "GRÊMIO": 284,
    "INT": 285, "INTERNACIONAL": 285,
    "JEC": 317, "JOINVILLE": 317,
    "JUVENTUDE": 286,
    "PAL": 275, "PALMEIRAS": 275,
    "PAR": 270, "PARANÁ": 270,
    "PON": 303, "PONTE PRETA": 303,
    "SAN": 277, "SANTOS": 277,
    "SAO": 276, "SÃO PAULO": 276,
    "SCZ": 344, "SANTA CRUZ": 344,
    "SPO": 292, "SPORT": 292, "SPT": 292,
    "VAS": 267, "VASCO": 267,
    "VIT": 287, "VITÓRIA": 287,
}
```

**Resolution policy** (in `team.resolve_id_clube`):
1. Normalize `nome_clube`: `unidecode(name.strip().upper())`. Compare against an unidecoded version of the map keys.
2. If found → set canonical `id_clube`.
3. If not found OR `nome_clube` is NaN/empty → leave `id_clube` as NaN, log a warning with the row count grouped by `(ano, nome_clube)`.

**Empirical impact** (from raw data audit):
- 2014 has ~48% rows with empty club info (1 single row has actual points; others are noise/zero rows). These will surface as `id_clube` NaN and be visible to downstream consumers.
- 2015, 2016, 2019+ have ~0% empty club info.
- 2018's "ATL" ambiguity is fully resolved by always rebuilding from the full name.

## 7. Pipeline Design

### 7.1 Architecture

The pipeline is organized **by entity** (team, player, scouts) — mirroring the schema groups in §6. A small `columns.py` handles the cross-cutting raw→canonical rename; the rest is entity-aligned.

```
                   ┌──────────────────┐
                   │   raw CSVs       │
                   │ data/01_raw/Y/   │
                   └────────┬─────────┘
                            │
                            ▼
               ┌────────────────────────┐
               │  reader (per shape)    │  readers.py
               │  - season_files        │
               │  - monolithic          │
               │  - round_files         │
               └────────────┬───────────┘
                            ▼
               ┌────────────────────────┐
               │  rename_columns        │  columns.py
               │  raw → canonical names │
               └────────────┬───────────┘
                            ▼
               ┌────────────────────────┐
               │  team                  │  team.py
               │  resolve_id_clube      │
               │  (via TEAM_NAME_TO_ID) │
               └────────────┬───────────┘
                            ▼
               ┌────────────────────────┐
               │  player                │  player.py
               │  map_position →        │
               │  map_status →          │
               │  fill_missing_slug     │
               └────────────┬───────────┘
                            ▼
               ┌────────────────────────┐
               │  scouts                │  scouts.py
               │  harmonize_names →     │
               │  disaccumulate (if cat)│
               │  → fill_within_year    │
               └────────────┬───────────┘
                            ▼
            ┌────────────────────────────────┐
            │  per-year DataFrame            │
            │  data/03_primary/cartola_Y.csv │
            └────────────┬───────────────────┘
                         │   (one node per year via @parameterize)
                         ▼
            ┌────────────────────────────────┐
            │  aggregated DataFrame          │
            │  pd.concat(all years)          │
            │  data/04_aggregated/...csv     │
            └────────────────────────────────┘
```

### 7.2 Module structure (entity-organized)

```
src/cartola/
├── __init__.py
├── cli.py                     # Typer CLI: `aggregate`, `viz`
├── aggregation/
│   ├── __init__.py
│   ├── schema.py              # CANONICAL_COLUMNS, dtypes, AggregatedSchema (Pandera)
│   ├── columns.py             # COLUMN_RENAME_MAP, rename_columns()
│   │                          # cross-cutting: raw → canonical column names
│   ├── readers.py             # read_season_files, read_monolithic, read_round_files
│   ├── team.py                # TEAM_NAME_TO_ID, resolve_id_clube()
│   ├── player.py              # POSITION_MAP, STATUS_MAP, map_position(),
│   │                          # map_status(), fill_missing_slug()
│   ├── scouts.py              # SCOUTS, SCOUT_RENAME_MAP,
│   │                          # harmonize_scout_names(), disaccumulate_scouts(),
│   │                          # fill_scouts_within_year(), process()
│   ├── catalog.py             # YearConfig dataclass, YEAR_REGISTRY dict
│   ├── nodes.py               # Hamilton @parameterize'd nodes per year +
│   │                          # `aggregated` final node (orchestrates entities)
│   └── driver.py              # build_driver(), run(years, output_dir, track)
├── commons/
│   ├── __init__.py
│   ├── dataframes.py          # concat helpers, drop_duplicates
│   └── features.py            # compute_slug
├── download_data.py           # KEPT as-is (independent script)
└── update_readme.py           # KEPT as-is
```

**Why entity-based**: matches schema groups (§6), domain-aligned naming, scales naturally as features grow per entity. The cross-cutting `rename_columns` lives in `columns.py` to avoid fragmenting the rename map across files.

### 7.3 The catalog (`catalog.py`)

The catalog is the **single source of truth** for per-year metadata. Adding year N+1 = adding one entry.

```python
from dataclasses import dataclass
from typing import Callable

import pandas as pd

@dataclass(frozen=True)
class YearConfig:
    year: int
    raw_dir: str                       # data/01_raw/<year>
    reader: Callable[[str, int], pd.DataFrame]
    accumulated: bool = False          # if True, run disaccumulate_scouts
    has_scouts: bool = True            # if False, scout columns will all be NaN

YEAR_REGISTRY: dict[int, YearConfig] = {
    2014: YearConfig(2014, "data/01_raw/2014", read_season_files,  accumulated=False),
    2015: YearConfig(2015, "data/01_raw/2015", read_season_files,  accumulated=True),
    2016: YearConfig(2016, "data/01_raw/2016", read_season_files,  accumulated=False),
    2017: YearConfig(2017, "data/01_raw/2017", read_monolithic,    accumulated=True),
    2018: YearConfig(2018, "data/01_raw/2018", read_round_files,   accumulated=True),
    2019: YearConfig(2019, "data/01_raw/2019", read_round_files,   accumulated=True),
    2020: YearConfig(2020, "data/01_raw/2020", read_round_files,   accumulated=True),
    2021: YearConfig(2021, "data/01_raw/2021", read_round_files,   accumulated=True),
    2022: YearConfig(2022, "data/01_raw/2022", read_round_files,   accumulated=True),
    2023: YearConfig(2023, "data/01_raw/2023", read_round_files,   accumulated=False),
    2024: YearConfig(2024, "data/01_raw/2024", read_round_files,   accumulated=False),
    2025: YearConfig(2025, "data/01_raw/2025", read_round_files,   accumulated=False, has_scouts=False),
    2026: YearConfig(2026, "data/01_raw/2026", read_round_files,   accumulated=False),
}
```

### 7.4 Hamilton nodes (`nodes.py`)

Each year becomes one Hamilton node via `@parameterize`. The aggregated node depends on all year nodes.

```python
from hamilton.function_modifiers import parameterize, value
import pandas as pd

from cartola.aggregation import columns, team, player, scouts
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS

# Generate {"year_2014": {"year": value(2014)}, "year_2015": {...}, ...}
_PARAMS = {f"year_{y}": {"year": value(y)} for y in YEAR_REGISTRY}

@parameterize(**_PARAMS)
def year_dataframe(year: int) -> pd.DataFrame:
    """Reads raw data and applies entity-by-entity transformations to produce
    one year of data in the canonical schema."""
    cfg = YEAR_REGISTRY[year]
    raw = cfg.reader(cfg.raw_dir, year)
    df = columns.rename_columns(raw)
    df = team.resolve_id_clube(df)
    df = player.map_position(df)
    df = player.map_status(df)
    df = player.fill_missing_slug(df)
    df = scouts.process(df, accumulated=cfg.accumulated, has_scouts=cfg.has_scouts)
    df["ano"] = year
    return df.reindex(columns=CANONICAL_COLUMNS)

def aggregated(
    year_2014: pd.DataFrame, year_2015: pd.DataFrame, year_2016: pd.DataFrame,
    year_2017: pd.DataFrame, year_2018: pd.DataFrame, year_2019: pd.DataFrame,
    year_2020: pd.DataFrame, year_2021: pd.DataFrame, year_2022: pd.DataFrame,
    year_2023: pd.DataFrame, year_2024: pd.DataFrame, year_2025: pd.DataFrame,
    year_2026: pd.DataFrame,
) -> pd.DataFrame:
    """Concat all years into one DataFrame."""
    frames = [
        year_2014, year_2015, year_2016, year_2017, year_2018, year_2019,
        year_2020, year_2021, year_2022, year_2023, year_2024, year_2025, year_2026,
    ]
    return pd.concat(frames, ignore_index=True).reset_index(drop=True)
```

When 2027 is added: add it to `YEAR_REGISTRY` and add `year_2027: pd.DataFrame` to the `aggregated` signature. Two edits, both in obvious places.

### 7.5 Scout disaccumulation (`scouts.py`)

```python
def disaccumulate_scouts(df: pd.DataFrame, scout_cols: list[str]) -> pd.DataFrame:
    """Convert season-cumulative scouts to per-round values.
    
    Cartola API returns scouts as season-cumulative on some years. The per-round
    delta is the diff against the player's previous appearance.
    
    Edge cases handled:
    - Player skipped a round: cumulative didn't change → diff = 0 ✓
    - First appearance: keep the cumulative value as the per-round value
    - Cartola correction lowering a scout: kept as negative (caller's choice),
      except SG (clean sheet) which is clipped at 0.
    """
    df = df.sort_values(["id_atleta", "rodada"]).copy()
    df[scout_cols] = df[scout_cols].fillna(0.0)
    diffs = df.groupby("id_atleta", sort=False)[scout_cols].diff()
    first = df.groupby("id_atleta", sort=False).cumcount() == 0
    diffs.loc[first, :] = df.loc[first, scout_cols].values
    if "SG" in scout_cols:
        diffs["SG"] = diffs["SG"].clip(lower=0)
    df[scout_cols] = diffs.values
    return df
```

### 7.6 NaN policy for scouts

The `scouts.process` function in `scouts.py` applies the rules below. Pseudocode:

```python
def process(df, accumulated: bool, has_scouts: bool) -> pd.DataFrame:
    if not has_scouts:
        for col in SCOUTS:
            df[col] = pd.NA          # all 21 scouts NaN (e.g., 2025)
        return df

    df = harmonize_scout_names(df)   # PE→PI, RB→DS, DD→DE
    present = [c for c in SCOUTS if c in df.columns]
    df[present] = df[present].fillna(0.0)
    if accumulated:
        df = disaccumulate_scouts(df, scout_cols=present)
    return df
```

Resulting policy:

- **Within a year, for scout columns that exist in raw data**: missing values mean "no scout credited" → fill with `0.0` before disaccumulation.
- **For scout columns that don't exist in that year**: stay `NaN` after concat (e.g., `V` for `ano < 2023`).
- **For 2025 (`has_scouts=False`)**: all 21 scout columns are `NaN`.

### 7.7 CLI (`cli.py`)

```bash
# Run the pipeline for all configured years (default)
$ uv run cartola aggregate

# Run for a subset
$ uv run cartola aggregate --years 2022,2023,2024

# Run and send lineage to Hamilton UI
$ uv run cartola aggregate --track

# Launch Hamilton UI server (open http://localhost:8241)
$ uv run cartola viz
```

`aggregate` writes:
- `data/03_primary/cartola_<year>.csv` for each year processed.
- `data/04_aggregated/cartola_<min>_<max>.csv` for the concatenated result.

## 8. Test Strategy

```
tests/
├── conftest.py                # shared fixtures, tiny DataFrames
├── fixtures/                  # synthetic mini CSVs, committed to git
│   ├── 2014/{2014_jogadores,2014_scouts_raw,2014_times}.csv
│   ├── 2017/2017_scouts_raw.csv
│   └── 2018/{rodada-1,rodada-2}.csv
├── unit/                      # one test file per source module (1:1)
│   ├── test_schema.py
│   ├── test_columns.py        # rename_columns: legacy → canonical names
│   ├── test_readers.py        # each reader against fixtures
│   ├── test_team.py           # resolve_id_clube + edge cases (see below)
│   ├── test_player.py         # map_position, map_status, fill_missing_slug
│   ├── test_scouts.py         # harmonize_names, disaccumulate edge cases
│   ├── test_catalog.py        # all years valid, raw_dir exists
│   └── test_nodes.py
├── integration/
│   └── test_pipeline_end_to_end.py  # Hamilton driver with synthetic fixtures,
│                                    # checks columns, dtypes, row counts
└── data_quality/
    ├── test_pandera_schema.py       # AggregatedSchema.validate(...)
    └── test_real_data_smoke.py      # runs full pipeline on real data;
                                     # validates schema + sanity checks per year
```

### Unit test coverage targets

**`test_columns.py`**
- `test_rename_columns_legacy_2014`: `Apelido`→`apelido`, `AtletaID`→`id_atleta`, etc.
- `test_rename_columns_modern_atletas_prefix`: `atletas.atleta_id`→`id_atleta`, `atletas.clube.id.full.name`→`nome_clube`.

**`test_team.py`**
- `test_resolve_id_clube_full_name`: "Flamengo" → 262.
- `test_resolve_id_clube_abbreviation`: "FLA" → 262.
- `test_resolve_id_clube_with_accents`: "São Paulo" / "SAO PAULO" → 276.
- `test_resolve_id_clube_unknown_name_stays_nan`: "Time XYZ" → NaN, warning logged.
- `test_resolve_id_clube_overrides_raw_2018`: 2018 row with `id_clube="ATL"` and `nome_clube="Atlético-MG"` → id_clube=282 (not the buggy abbreviation).
- `test_resolve_id_clube_parana`: "Paraná" → 270.

**`test_player.py`**
- `test_map_position_legacy_id_to_label`: int 1 → "gol", 5 → "ata".
- `test_map_status_legacy_id_to_label`: int 7 → "Provável", 5 → "Contundido".
- `test_fill_missing_slug_uses_apelido`: NaN slug → `compute_slug(apelido)`.

**`test_scouts.py`**
- `test_harmonize_scout_names`: PE→PI, RB→DS, DD→DE applied.
- `test_disaccumulate_basic`: simple 2-round case.
- `test_disaccumulate_skipped_round`: player misses a round.
- `test_disaccumulate_first_appearance_mid_season`: player joins in round 5.
- `test_disaccumulate_sg_clip`: SG never goes negative.
- `test_disaccumulate_retroactive_correction`: cumulative goes down → kept as negative for non-SG scouts.
- `test_process_no_scouts_year`: `has_scouts=False` → all 21 scouts NaN.

**`test_catalog.py`**
- `test_all_years_have_existing_raw_dir`: every YEAR_REGISTRY entry points to a real directory.
- `test_accumulated_years_match_spec`: confirms 2015, 2017, 2018, 2019, 2020, 2021, 2022 are flagged accumulated.

### Pandera schema (in `aggregation/schema.py`)

```python
import pandera as pa
from pandera.typing import Series

class AggregatedSchema(pa.DataFrameModel):
    ano: Series[int] = pa.Field(ge=2014, le=2030)
    rodada: Series[int] = pa.Field(ge=0, le=38)
    id_clube: Series[pd.Int32Dtype] = pa.Field(nullable=True)
    nome_clube: Series[str] = pa.Field(nullable=True)
    id_atleta: Series[int]
    # ... player info, game state ...
    pontuacao: Series[float] = pa.Field(nullable=True)
    A: Series[float] = pa.Field(nullable=True, ge=0)
    SG: Series[float] = pa.Field(nullable=True, ge=0)
    # ... 21 scouts ...
    
    class Config:
        strict = True   # rejects unexpected columns
        unique = ["ano", "rodada", "id_atleta"]
```

### Smoke test (`test_real_data_smoke.py`)

Runs the pipeline on real data for all configured years and asserts:
- Schema validates.
- Row count per year is within reasonable bounds (e.g. 2018+: between 5k and 30k rows per year).
- For 2018+: number of unique rounds is between 30 and 38.
- For 2018+: total `G` per year is in `[100, 1500]`.
- For 2025: all scout columns are entirely NaN (catalog says `has_scouts=False`).

## 9. Removal Plan (Kedro Cleanup)

### Files to delete
- `src/cartola/__main__.py`
- `src/cartola/pipeline_registry.py`
- `src/cartola/settings.py`
- `src/cartola/pipelines/` (entire dir)
- `src/cartola/extras/` (entire dir)
- `src/cartola/schemas/` (empty, just delete)
- `src/tests/` (Kedro test scaffolding)
- `conf/` (entire dir; map_col_names and map_status_id_to_str ported into Python)
- `poetry.lock`
- `Dockerfile`, `.dockerignore`, `.dive-ci`
- `data/02_intermediate/` (no longer used)
- Existing CSVs in `data/03_primary/` (will be overwritten by new pipeline; keep folder)

### Files to rewrite
- `pyproject.toml`: Poetry → uv, drop kedro deps, add `sf-hamilton[visualization]`, `sf-hamilton-ui`, `typer`, `pandera`, `pandas`, `pyarrow` (for parquet read in tests if any), `unidecode`. Dev deps: `pytest`, `pytest-cov`, `pre-commit`, etc.
- `Makefile`: replace kedro/docker targets with `uv run` shortcuts (`make aggregate`, `make viz`, `make test`).
- `README.md`: remove the line "Estamos preparando um pipeline para agregar os dados…" once the pipeline ships; add a "Pipeline" section.

### Files to keep untouched
- `src/R/`
- `src/cartola/download_data.py`
- `src/cartola/update_readme.py`
- `src/cartola/commons/features.py`
- `src/cartola/commons/dataframes.py` (lightly trimmed if needed)
- `data/01_raw/`
- `notebooks/`
- `.github/`, `.gitignore`, `.markdownlint.yaml`, `.pre-commit-config.yaml`, `LICENSE`, `setup.cfg`

## 10. Maintenance Workflow

When the next Cartola season opens (e.g. 2027):

1. New CSVs land under `data/01_raw/2027/` (handled by existing `download_data.py`).
2. Add **one entry** to `YEAR_REGISTRY` in `catalog.py`.
3. Add `year_2027: pd.DataFrame` to the `aggregated()` signature in `nodes.py`.
4. Run `uv run cartola aggregate`. New aggregated CSV is produced.
5. If a new scout appears: add it to `SCOUTS` in `schema.py` and to the Pandera model.
6. If the raw shape changes: add a new reader function in `readers.py` and reference it in the catalog entry.

## 11. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Pandera too strict, breaking on subtle dtype drift | Start with `strict=False` for the smoke tests, tighten incrementally |
| Hamilton UI dep is heavy / brittle | Mark as optional (`uv add --optional ui sf-hamilton-ui`); `cartola viz` prints install hint if missing |
| Disaccumulation breaks on a year with weird API behavior | Per-year unit tests with year-specific fixtures; smoke test catches regressions |
| `@parameterize` with 13+ years generates a wide DAG | Hamilton handles this fine; UI shows it readably |
| Old preprocessed CSVs in `data/03_primary/` create confusion | Delete `data/02_intermediate/` outright; new pipeline overwrites `data/03_primary/cartola_<year>.csv` |
