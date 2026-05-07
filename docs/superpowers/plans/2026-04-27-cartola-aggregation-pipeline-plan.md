# Cartola Aggregation Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the legacy Kedro pipeline with a Hamilton-based, entity-organized aggregation pipeline that produces a single harmonized CSV (`data/04_aggregated/cartola_2014_2026.csv`) covering all 13 years of Cartola FC data.

**Architecture:** Function-based DAG using Hamilton's `@parameterize` (one node per year), feeding a final `aggregated` concat node. Per-year processing flows through entity-aligned modules (`columns` → `team` → `player` → `scouts`). Year-specific config lives in a single `YEAR_REGISTRY` catalog. CSV-in / CSV-out, all local.

**Tech Stack:** Python 3.12+, `uv` (package mgr), Hamilton (`sf-hamilton`), Hamilton UI (`sf-hamilton-ui`), Typer (CLI), Pandera (schema validation), pytest, pandas, unidecode, ruff (lint+format).

**Spec reference:** `docs/superpowers/specs/2026-04-27-cartola-aggregation-pipeline-design.md`.

**Working principles:** TDD (red → green → commit). DRY. YAGNI. Frequent small commits. After every test step, run with `-v` and verify the expected pass/fail outcome before continuing.

---

## Phase 0 — Cleanup and Project Setup

### Task 0.1: Delete Kedro / Docker artifacts

**Files:**
- Delete: `src/cartola/__main__.py`
- Delete: `src/cartola/pipeline_registry.py`
- Delete: `src/cartola/settings.py`
- Delete: `src/cartola/pipelines/` (entire dir)
- Delete: `src/cartola/extras/` (entire dir)
- Delete: `src/cartola/schemas/` (entire dir, if exists)
- Delete: `src/tests/` (Kedro test scaffolding)
- Delete: `conf/` (entire dir — `parameters.yml` content is ported into Python in later tasks)
- Delete: `poetry.lock`
- Delete: `Dockerfile`, `.dockerignore`, `.dive-ci`
- Delete: `data/02_intermediate/` (entire dir, no longer used)

- [ ] **Step 1: Verify the files exist before deleting**

```bash
ls src/cartola/__main__.py src/cartola/pipeline_registry.py src/cartola/settings.py
ls -d src/cartola/pipelines src/cartola/extras src/tests conf data/02_intermediate
ls poetry.lock Dockerfile .dockerignore .dive-ci
```

Expected: most/all listed (some like `src/cartola/schemas` may be missing — that's fine).

- [ ] **Step 2: Delete them**

```bash
rm -f src/cartola/__main__.py src/cartola/pipeline_registry.py src/cartola/settings.py
rm -rf src/cartola/pipelines src/cartola/extras src/cartola/schemas src/tests conf data/02_intermediate
rm -f poetry.lock Dockerfile .dockerignore .dive-ci
```

- [ ] **Step 3: Verify they're gone**

```bash
ls src/cartola/ conf 2>&1 | head -20
```

Expected: `conf` reports "No such file"; `src/cartola/` shows only `__init__.py`, `commons/`, `download_data.py`, `update_readme.py`.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove Kedro and Docker scaffolding ahead of pipeline rewrite"
```

---

### Task 0.2: Rewrite `pyproject.toml` for `uv` + ruff

**Files:**
- Modify: `pyproject.toml` (full rewrite)
- Optionally autofix `src/cartola/` (ruff modernization of pre-existing code)

- [ ] **Step 1: Replace `pyproject.toml` with the uv-native, ruff-based version**

```toml
[project]
name = "cartola"
version = "0.2.0"
description = "Local pipeline that aggregates Cartola FC data (2014–2026) into a single harmonized CSV. Plus exploratory analyses in R/Python."
authors = [{ name = "Henrique Gomide", email = "henriquepgomide@gmail.com" }]
license = { text = "MIT" }
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pandas>=2.2,<3.0",
    "sf-hamilton>=1.83",
    "typer>=0.12",
    "pandera>=0.20,<2.0",
    "unidecode>=1.3.6",
    "pyarrow>=15.0",
    "requests>=2.31",
]

[project.optional-dependencies]
ui = ["sf-hamilton-ui>=0.0.17"]

[project.scripts]
cartola = "cartola.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cartola"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.12",
    "pre-commit>=3.7",
    "ruff>=0.6",
    "mypy>=1.10",
    "nbstripout>=0.7",
]

[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (import order)
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
]
ignore = [
    "E203",  # whitespace before ':' (ruff-format compatibility)
]

[tool.pytest.ini_options]
addopts = "--cov-report term-missing --cov src/cartola -ra"
testpaths = ["tests"]

[tool.coverage.report]
fail_under = 0
show_missing = true
exclude_lines = ["pragma: no cover", "raise NotImplementedError"]
```

Notes on the design:
- `ruff` replaces `black` + `isort` + `flake8` — single tool, faster, one config.
- `requests>=2.31` is required at runtime (`src/cartola/download_data.py` imports it).
- `sf-hamilton-ui>=0.0.17` (PyPI's latest at the time of writing).
- `pandera<2.0` keeps the schema model API stable until we migrate.
- `requires-python = ">=3.12"` lets us use modern typing without `from __future__ import annotations` boilerplate (current Python ecosystem fully supports 3.12/3.13).

- [ ] **Step 2: Generate the lock file with uv**

```bash
uv sync --extra ui --group dev
```

Expected: produces `uv.lock` and `.venv/`. If `uv` is not installed, run `curl -LsSf https://astral.sh/uv/install.sh | sh` first.

- [ ] **Step 3: Smoke check the install**

```bash
uv run python -c "import pandas, hamilton, typer, pandera, unidecode, requests; print('ok')"
```

Expected: `ok`.

- [ ] **Step 4: (Optional) Modernize pre-existing src with ruff**

```bash
uv run ruff check --fix src/cartola/
uv run ruff format src/cartola/
uv run ruff check src/cartola/   # must be "All checks passed!"
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock src/cartola/
git commit -m "chore: switch to uv + ruff toolchain (Python 3.12+)"
```

---

### Task 0.3: Initialize the new `tests/` skeleton

**Files:**
- Create: `tests/__init__.py` (empty)
- Create: `tests/conftest.py`
- Create: `tests/unit/__init__.py` (empty)
- Create: `tests/integration/__init__.py` (empty)
- Create: `tests/data_quality/__init__.py` (empty)
- Create: `tests/fixtures/.gitkeep` (empty)

- [ ] **Step 1: Create empty package markers**

```bash
mkdir -p tests/unit tests/integration tests/data_quality tests/fixtures
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/data_quality/__init__.py tests/fixtures/.gitkeep
```

- [ ] **Step 2: Create `tests/conftest.py` with shared fixtures**

```python
"""Shared pytest fixtures for the Cartola aggregation pipeline tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the synthetic test-fixture CSVs."""
    return FIXTURES_DIR


@pytest.fixture
def repo_root() -> Path:
    """Path to the repo root, useful for the real-data smoke test."""
    return REPO_ROOT


@pytest.fixture
def empty_player_df() -> pd.DataFrame:
    """An empty DataFrame with the canonical column set, useful for edge-case tests."""
    from cartola.aggregation.schema import CANONICAL_COLUMNS

    return pd.DataFrame(columns=CANONICAL_COLUMNS)
```

- [ ] **Step 3: Run pytest to confirm collection works (no tests yet)**

```bash
uv run pytest -q
```

Expected: `no tests ran in 0.XXs` (exit 5 is fine — means no tests collected).

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: scaffold tests/ tree with conftest"
```

---

## Phase 1 — Foundation modules (entity layer, no Hamilton yet)

### Task 1.1: `schema.py` — canonical columns, dtypes, label maps

**Files:**
- Create: `src/cartola/aggregation/__init__.py` (empty)
- Create: `src/cartola/aggregation/schema.py`
- Create: `tests/unit/test_schema.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_schema.py`:

```python
"""Tests for the canonical schema constants."""
import pandas as pd

from cartola.aggregation import schema


def test_canonical_columns_count_is_38():
    assert len(schema.CANONICAL_COLUMNS) == 38


def test_canonical_columns_start_with_context_block():
    assert schema.CANONICAL_COLUMNS[:5] == [
        "ano",
        "rodada",
        "id_clube",
        "nome_clube",
        "id_atleta",
    ]


def test_scouts_count_is_21():
    assert len(schema.SCOUTS) == 21


def test_scouts_set_matches_expected():
    expected = {
        "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF",
        "FS", "FT", "G", "GC", "GS", "I", "PC", "PI", "PP",
        "PS", "SG", "V",
    }
    assert set(schema.SCOUTS) == expected


def test_position_map_includes_all_six_labels():
    assert set(schema.POSITION_MAP.values()) == {"gol", "lat", "zag", "mei", "ata", "tec"}


def test_status_map_matches_kedro_legacy():
    assert schema.STATUS_MAP[7] == "Provável"
    assert schema.STATUS_MAP[5] == "Contundido"
    assert schema.STATUS_MAP[6] == "Nulo"


def test_dtypes_includes_all_canonical_columns():
    missing = set(schema.CANONICAL_COLUMNS) - set(schema.DTYPES)
    assert missing == set(), f"DTYPES missing: {missing}"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_schema.py -v
```

Expected: `ModuleNotFoundError: cartola.aggregation`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/__init__.py` — empty.

`src/cartola/aggregation/schema.py`:

```python
"""Canonical schema for the aggregated Cartola DataFrame.

This module is the single source of truth for:
- column names and order in the final aggregated CSV (CANONICAL_COLUMNS, DTYPES)
- the canonical scout list (SCOUTS)
- categorical label maps (POSITION_MAP, STATUS_MAP)

The Pandera DataFrame model (AggregatedSchema) is added in a later task.
"""
from __future__ import annotations

import pandas as pd

# 21 canonical scouts, ordered alphabetically.
SCOUTS: list[str] = [
    "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF",
    "FS", "FT", "G", "GC", "GS", "I", "PC", "PI", "PP",
    "PS", "SG", "V",
]

# Final column order: contexto (5) → info do jogador (10) → game state (2) → scouts (21).
CANONICAL_COLUMNS: list[str] = [
    # contexto
    "ano",
    "rodada",
    "id_clube",
    "nome_clube",
    "id_atleta",
    # info do jogador
    "nome",
    "apelido",
    "apelido_abreviado",
    "slug",
    "foto",
    "posicao",
    "status",
    "pontuacao",
    "media",
    "preco",
    # game state
    "variacao",
    "num_jogos",
    # scouts
    *SCOUTS,
]

# Per-column pandas dtypes used after harmonization.
# Nullable types (Int*) are required for columns that may legitimately be NaN.
DTYPES: dict[str, str] = {
    "ano": "int16",
    "rodada": "int8",
    "id_clube": "Int32",
    "nome_clube": "string",
    "id_atleta": "int64",
    "nome": "string",
    "apelido": "string",
    "apelido_abreviado": "string",
    "slug": "string",
    "foto": "string",
    "posicao": "string",
    "status": "string",
    "pontuacao": "float32",
    "media": "float32",
    "preco": "float32",
    "variacao": "float32",
    "num_jogos": "Int16",
    **{col: "float32" for col in SCOUTS},
}

# Cartola posicao_id (int) → label.
POSITION_MAP: dict[int, str] = {
    1: "gol",
    2: "lat",
    3: "zag",
    4: "mei",
    5: "ata",
    6: "tec",
}

# Cartola status_id (int) → label. Source: Kedro legacy conf/base/parameters.yml.
STATUS_MAP: dict[int, str] = {
    2: "Dúvida",
    3: "Suspenso",
    5: "Contundido",
    6: "Nulo",
    7: "Provável",
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_schema.py -v
```

Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/__init__.py src/cartola/aggregation/schema.py tests/unit/test_schema.py
git commit -m "feat(aggregation): add canonical schema constants (38 cols, 21 scouts)"
```

---

### Task 1.2: `columns.py` — raw → canonical column rename

**Files:**
- Create: `src/cartola/aggregation/columns.py`
- Create: `tests/unit/test_columns.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_columns.py`:

```python
"""Tests for column renaming (raw → canonical)."""
import pandas as pd

from cartola.aggregation import columns


def test_rename_columns_legacy_2014():
    raw = pd.DataFrame({
        "AtletaID": [1],
        "Apelido": ["Foo"],
        "ClubeID": [262],
        "Rodada": [1],
        "Pontos": [10.0],
    })
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta", "apelido", "id_clube", "rodada", "pontuacao"]


def test_rename_columns_modern_atletas_prefix():
    raw = pd.DataFrame({
        "atletas.atleta_id": [1],
        "atletas.apelido": ["Foo"],
        "atletas.clube.id.full.name": ["Flamengo"],
        "atletas.clube_id": ["FLA"],
        "atletas.rodada_id": [1],
        "atletas.pontos_num": [10.0],
        "atletas.posicao_id": ["mei"],
        "atletas.status_id": ["Provável"],
    })
    out = columns.rename_columns(raw)
    expected = {
        "id_atleta", "apelido", "nome_clube", "id_clube", "rodada",
        "pontuacao", "posicao", "status",
    }
    assert set(out.columns) == expected


def test_rename_columns_drops_known_noise_columns():
    raw = pd.DataFrame({
        "AtletaID": [1],
        "Participou": [1],
        "athletes.atletas.scout": ["{}"],
        "atletas.minimo_para_valorizar": [1.0],
        "atletas.entrou_em_campo": [True],
    })
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta"]


def test_rename_columns_preserves_unknown_scouts():
    raw = pd.DataFrame({"AtletaID": [1], "G": [0.0], "PE": [0.0], "DD": [0.0]})
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta", "G", "PE", "DD"]


def test_rename_columns_drops_empty_index_column():
    raw = pd.DataFrame({"": [0], "AtletaID": [1]})
    out = columns.rename_columns(raw)
    assert list(out.columns) == ["id_atleta"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_columns.py -v
```

Expected: `ModuleNotFoundError` for `cartola.aggregation.columns`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/columns.py`:

```python
"""Cross-cutting column rename: raw CSV column names → canonical schema names.

Sourced from the legacy Kedro `parameters.yml::preprocessing.map_col_names` plus
columns we explicitly drop because they are noise or out-of-canon.
"""
from __future__ import annotations

import pandas as pd

# Raw column name → canonical name. Order does not matter; pandas resolves by exact match.
COLUMN_RENAME_MAP: dict[str, str] = {
    # ---- legacy 2014–2016 ---------------------------------------------------
    "Apelido": "apelido",
    "AtletaID": "id_atleta",
    "ClubeID": "id_clube",
    "ClubeNome": "nome_clube",
    "Nome": "nome_clube",  # appears as the team name in 2014_times.csv merge
    "Rodada": "rodada",
    "Pontos": "pontuacao",
    "PontosMedia": "media",
    "Preco": "preco",
    "PrecoVariacao": "variacao",
    "PosicaoID": "posicao",
    # ---- snake_case API (2017 monolithic with mixed naming) -----------------
    "atleta_id": "id_atleta",
    "clube_id": "id_clube",
    "rodada_id": "rodada",
    "posicao_id": "posicao",
    "status_id": "status",
    "pontos_num": "pontuacao",
    "media_num": "media",
    "preco_num": "preco",
    "variacao_num": "variacao",
    "jogos_num": "num_jogos",
    # ---- modern `atletas.*` prefix (2017+) ----------------------------------
    "atletas.apelido": "apelido",
    "atletas.apelido_abreviado": "apelido_abreviado",
    "atletas.atleta_id": "id_atleta",
    "atletas.clube.id.full.name": "nome_clube",
    "atletas.clube_id": "id_clube",
    "atletas.foto": "foto",
    "atletas.jogos_num": "num_jogos",
    "atletas.media_num": "media",
    "atletas.nome": "nome",
    "atletas.pontos_num": "pontuacao",
    "atletas.posicao_id": "posicao",
    "atletas.preco_num": "preco",
    "atletas.rodada_id": "rodada",
    "atletas.slug": "slug",
    "atletas.status_id": "status",
    "atletas.variacao_num": "variacao",
}

# Columns we drop unconditionally (noise, legacy-only, or out-of-canon).
COLUMNS_TO_DROP: frozenset[str] = frozenset({
    "",  # unnamed index column written by R/pandas with index=True
    "Participou", "participou",
    "Posicao", "Jogos", "Partida", "Mando", "Titular",
    "Substituido", "TempoJogado", "Nota",
    "athletes.atletas.scout",
    "atletas.minimo_para_valorizar",
    "atletas.entrou_em_campo",
    "atletas.temporada_id",
    "Abreviacao",  # from times.csv merge — not part of canonical schema
})


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop noise columns then rename raw → canonical via COLUMN_RENAME_MAP.

    Unknown columns are passed through unchanged so downstream entity modules
    (and the final reindex against CANONICAL_COLUMNS) can decide what to keep.
    """
    keep = [c for c in df.columns if c not in COLUMNS_TO_DROP]
    return df[keep].rename(columns=COLUMN_RENAME_MAP)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_columns.py -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/columns.py tests/unit/test_columns.py
git commit -m "feat(aggregation): add raw→canonical column rename"
```

---

### Task 1.3: `team.py` — TEAM_NAME_TO_ID + resolve_id_clube

**Files:**
- Create: `src/cartola/aggregation/team.py`
- Create: `tests/unit/test_team.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_team.py`:

```python
"""Tests for team-entity transformations."""
import logging

import pandas as pd

from cartola.aggregation import team


def test_resolve_id_clube_full_name():
    df = pd.DataFrame({"nome_clube": ["Flamengo"], "id_clube": [pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 262


def test_resolve_id_clube_abbreviation():
    df = pd.DataFrame({"nome_clube": ["FLA"], "id_clube": [pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 262


def test_resolve_id_clube_with_accents():
    df = pd.DataFrame({"nome_clube": ["São Paulo", "SAO PAULO"], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert (out["id_clube"] == 276).all()


def test_resolve_id_clube_unknown_name_stays_nan(caplog):
    df = pd.DataFrame({
        "ano": [2024, 2024],
        "nome_clube": ["Time XYZ", "Time XYZ"],
        "id_clube": [pd.NA, pd.NA],
    })
    with caplog.at_level(logging.WARNING):
        out = team.resolve_id_clube(df)
    assert out["id_clube"].isna().all()
    assert any("Time XYZ" in record.message for record in caplog.records)


def test_resolve_id_clube_overrides_raw_2018_atl_ambiguity():
    # 2018 raw has id_clube="ATL" (string abbreviation, ambiguous between MG and PR).
    # We always rebuild from the full name → id 282.
    df = pd.DataFrame({"nome_clube": ["Atlético-MG"], "id_clube": ["ATL"]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 282


def test_resolve_id_clube_parana():
    df = pd.DataFrame({"nome_clube": ["Paraná"], "id_clube": [pd.NA]})
    out = team.resolve_id_clube(df)
    assert out["id_clube"].iloc[0] == 270


def test_resolve_id_clube_returns_int32_nullable_dtype():
    df = pd.DataFrame({"nome_clube": ["Flamengo", "Time XYZ"], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert str(out["id_clube"].dtype) == "Int32"


def test_resolve_id_clube_handles_nan_name():
    df = pd.DataFrame({"nome_clube": [None, "Flamengo"], "id_clube": [pd.NA, pd.NA]})
    out = team.resolve_id_clube(df)
    assert pd.isna(out["id_clube"].iloc[0])
    assert out["id_clube"].iloc[1] == 262
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_team.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/team.py`:

```python
"""Team-entity transformations.

Always rebuilds `id_clube` from the normalized `nome_clube`. This bypasses the
buggy raw `clube_id` in 2018 (string abbreviations, sometimes ambiguous like
"ATL" for both Atlético-MG and Atlético-PR).
"""
from __future__ import annotations

import logging

import pandas as pd
from unidecode import unidecode

logger = logging.getLogger(__name__)


# Full names + common abbreviations → canonical Cartola team id.
TEAM_NAME_TO_ID: dict[str, int] = {
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

# Pre-compute the unidecoded lookup once. Both keys (uppercased + accent-stripped).
_NAME_TO_ID_NORMALIZED: dict[str, int] = {
    unidecode(name.strip().upper()): team_id for name, team_id in TEAM_NAME_TO_ID.items()
}


def _normalize_name(name: object) -> str | None:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return None
    text = str(name).strip()
    if not text:
        return None
    return unidecode(text.upper())


def resolve_id_clube(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild `id_clube` from `nome_clube` using TEAM_NAME_TO_ID.

    Returns the input DataFrame with `id_clube` cast to `Int32` (nullable).
    Rows whose `nome_clube` cannot be resolved get NaN id_clube and a single
    aggregated WARN log per (ano, nome_clube) group is emitted.
    """
    df = df.copy()

    if "nome_clube" not in df.columns:
        df["id_clube"] = pd.array([pd.NA] * len(df), dtype="Int32")
        return df

    normalized = df["nome_clube"].map(_normalize_name)
    resolved = normalized.map(_NAME_TO_ID_NORMALIZED)

    df["id_clube"] = resolved.astype("Int32")

    unresolved_mask = df["id_clube"].isna() & df["nome_clube"].notna() & (df["nome_clube"].astype(str).str.strip() != "")
    if unresolved_mask.any():
        group_cols = [c for c in ("ano", "nome_clube") if c in df.columns]
        groups = (
            df.loc[unresolved_mask, group_cols]
            .groupby(group_cols, dropna=False)
            .size()
            .sort_values(ascending=False)
        )
        for key, count in groups.items():
            logger.warning("Unresolved nome_clube=%r (%d row(s))", key, count)

    return df
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_team.py -v
```

Expected: 8 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/team.py tests/unit/test_team.py
git commit -m "feat(aggregation): rebuild id_clube from nome_clube via TEAM_NAME_TO_ID"
```

---

### Task 1.4: `player.py` — position/status mapping + slug fill

**Files:**
- Create: `src/cartola/aggregation/player.py`
- Create: `tests/unit/test_player.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_player.py`:

```python
"""Tests for player-entity transformations."""
import pandas as pd

from cartola.aggregation import player


def test_map_position_int_id_to_label():
    df = pd.DataFrame({"posicao": [1, 5]})
    out = player.map_position(df)
    assert out["posicao"].tolist() == ["gol", "ata"]


def test_map_position_passes_through_existing_labels():
    # 2017–2022 already store the label string.
    df = pd.DataFrame({"posicao": ["zag", "mei"]})
    out = player.map_position(df)
    assert out["posicao"].tolist() == ["zag", "mei"]


def test_map_position_unknown_value_becomes_nan():
    df = pd.DataFrame({"posicao": [99, "alien"]})
    out = player.map_position(df)
    assert out["posicao"].isna().all()


def test_map_position_handles_missing_column():
    df = pd.DataFrame({"id_atleta": [1, 2]})
    out = player.map_position(df)
    assert "posicao" in out.columns
    assert out["posicao"].isna().all()


def test_map_status_int_id_to_label():
    df = pd.DataFrame({"status": [7, 5, 6]})
    out = player.map_status(df)
    assert out["status"].tolist() == ["Provável", "Contundido", "Nulo"]


def test_map_status_passes_through_existing_labels():
    df = pd.DataFrame({"status": ["Provável", "Suspenso"]})
    out = player.map_status(df)
    assert out["status"].tolist() == ["Provável", "Suspenso"]


def test_map_status_handles_missing_column():
    df = pd.DataFrame({"id_atleta": [1]})
    out = player.map_status(df)
    assert "status" in out.columns
    assert out["status"].isna().all()


def test_fill_missing_slug_uses_compute_slug():
    df = pd.DataFrame({"apelido": ["Yago Pikachu", "Foo"], "slug": [None, "foo-existing"]})
    out = player.fill_missing_slug(df)
    assert out["slug"].tolist() == ["yago-pikachu", "foo-existing"]


def test_fill_missing_slug_creates_column_if_missing():
    df = pd.DataFrame({"apelido": ["Foo Bar"]})
    out = player.fill_missing_slug(df)
    assert out["slug"].iloc[0] == "foo-bar"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_player.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/player.py`:

```python
"""Player-entity transformations: position/status normalization and slug fill."""
from __future__ import annotations

import pandas as pd

from cartola.aggregation.schema import POSITION_MAP, STATUS_MAP
from cartola.commons.features import compute_slug

_POSITION_LABELS = set(POSITION_MAP.values())
_STATUS_LABELS = set(STATUS_MAP.values())


def _coerce_with_map(value: object, id_to_label: dict[int, str], known_labels: set[str]) -> object:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NA
    if isinstance(value, str):
        text = value.strip()
        if text in known_labels:
            return text
        try:
            value = int(text)
        except (TypeError, ValueError):
            return pd.NA
    try:
        return id_to_label.get(int(value), pd.NA)
    except (TypeError, ValueError):
        return pd.NA


def map_position(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the `posicao` column to the label set {gol, lat, zag, mei, ata, tec}.

    Accepts either int Cartola ids (legacy 2014–2016, 2023+) or pre-mapped label
    strings (2017–2022). Unknown values become NaN.
    """
    df = df.copy()
    if "posicao" not in df.columns:
        df["posicao"] = pd.array([pd.NA] * len(df), dtype="string")
        return df
    df["posicao"] = df["posicao"].map(
        lambda v: _coerce_with_map(v, POSITION_MAP, _POSITION_LABELS)
    ).astype("string")
    return df


def map_status(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the `status` column to the label set {Provável, Dúvida, Suspenso, Contundido, Nulo}.

    Accepts either int ids (2023+) or label strings (2017–2022). Pre-2017 there
    is no status data → column is created as all-NaN.
    """
    df = df.copy()
    if "status" not in df.columns:
        df["status"] = pd.array([pd.NA] * len(df), dtype="string")
        return df
    df["status"] = df["status"].map(
        lambda v: _coerce_with_map(v, STATUS_MAP, _STATUS_LABELS)
    ).astype("string")
    return df


def fill_missing_slug(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing `slug` values from `apelido` via compute_slug()."""
    df = df.copy()
    if "slug" not in df.columns:
        df["slug"] = pd.NA
    needs_fill = df["slug"].isna()
    if "apelido" in df.columns:
        df.loc[needs_fill, "slug"] = df.loc[needs_fill, "apelido"].map(
            lambda x: compute_slug(x) if isinstance(x, str) and x else pd.NA
        )
    return df
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_player.py -v
```

Expected: 9 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/player.py tests/unit/test_player.py
git commit -m "feat(aggregation): add player position/status mapping and slug fill"
```

---

### Task 1.5: `scouts.py` — rename, disaccumulate, fill, process

**Files:**
- Create: `src/cartola/aggregation/scouts.py`
- Create: `tests/unit/test_scouts.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_scouts.py`:

```python
"""Tests for the scouts module: rename, disaccumulate, fill, process."""
import numpy as np
import pandas as pd

from cartola.aggregation import scouts
from cartola.aggregation.schema import SCOUTS


def test_harmonize_scout_names_renames_legacy():
    df = pd.DataFrame({"PE": [1.0], "RB": [2.0], "DD": [3.0], "G": [4.0]})
    out = scouts.harmonize_scout_names(df)
    assert set(out.columns) == {"PI", "DS", "DE", "G"}


def test_harmonize_scout_names_preserves_modern_columns():
    df = pd.DataFrame({"PI": [1.0], "G": [2.0]})
    out = scouts.harmonize_scout_names(df)
    assert list(out.columns) == ["PI", "G"]


def test_disaccumulate_basic_two_rounds():
    df = pd.DataFrame({
        "id_atleta": [1, 1],
        "rodada": [1, 2],
        "G": [1.0, 3.0],   # cumulative: 1 then 3 → per-round 1, 2
        "SG": [0.0, 1.0],
    })
    out = scouts.disaccumulate_scouts(df, scout_cols=["G", "SG"])
    assert out["G"].tolist() == [1.0, 2.0]
    assert out["SG"].tolist() == [0.0, 1.0]


def test_disaccumulate_skipped_round_is_zero():
    df = pd.DataFrame({
        "id_atleta": [1, 1, 1],
        "rodada": [1, 2, 3],
        "G": [1.0, 1.0, 2.0],   # round 2 absent → diff=0; round 3 → 1
    })
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].tolist() == [1.0, 0.0, 1.0]


def test_disaccumulate_first_appearance_mid_season_keeps_cumulative():
    df = pd.DataFrame({
        "id_atleta": [1],
        "rodada": [5],
        "G": [3.0],
    })
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].iloc[0] == 3.0


def test_disaccumulate_sg_clipped_at_zero():
    df = pd.DataFrame({
        "id_atleta": [1, 1],
        "rodada": [1, 2],
        "SG": [2.0, 1.0],   # cumulative went DOWN (Cartola correction)
    })
    out = scouts.disaccumulate_scouts(df, scout_cols=["SG"])
    assert out["SG"].tolist() == [2.0, 0.0]


def test_disaccumulate_retroactive_correction_keeps_negative_for_non_sg():
    df = pd.DataFrame({
        "id_atleta": [1, 1],
        "rodada": [1, 2],
        "G": [2.0, 1.0],
    })
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].tolist() == [2.0, -1.0]


def test_process_no_scouts_year_fills_all_with_nan():
    df = pd.DataFrame({"id_atleta": [1, 2], "rodada": [1, 1]})
    out = scouts.process(df, accumulated=False, has_scouts=False)
    for col in SCOUTS:
        assert col in out.columns
        assert out[col].isna().all()


def test_process_legacy_year_renames_and_fills_zero():
    df = pd.DataFrame({
        "id_atleta": [1],
        "rodada": [1],
        "PE": [np.nan],
        "RB": [3.0],
        "G": [1.0],
    })
    out = scouts.process(df, accumulated=False, has_scouts=True)
    assert out["PI"].iloc[0] == 0.0
    assert out["DS"].iloc[0] == 3.0
    assert out["G"].iloc[0] == 1.0


def test_process_accumulated_year_disaccumulates():
    df = pd.DataFrame({
        "id_atleta": [1, 1],
        "rodada": [1, 2],
        "G": [1.0, 4.0],
    })
    out = scouts.process(df, accumulated=True, has_scouts=True)
    assert out["G"].tolist() == [1.0, 3.0]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_scouts.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/scouts.py`:

```python
"""Scout-entity transformations: rename, disaccumulate, NaN policy."""
from __future__ import annotations

import pandas as pd

from cartola.aggregation.schema import SCOUTS

# Legacy → canonical scout name renames.
SCOUT_RENAME_MAP: dict[str, str] = {
    "PE": "PI",
    "RB": "DS",
    "DD": "DE",
}


def harmonize_scout_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename legacy scout columns to canonical names (PE→PI, RB→DS, DD→DE)."""
    return df.rename(columns=SCOUT_RENAME_MAP)


def disaccumulate_scouts(df: pd.DataFrame, scout_cols: list[str]) -> pd.DataFrame:
    """Convert season-cumulative scouts to per-round values.

    The Cartola API returns scouts as season-cumulative for some years
    (2015, 2017–2022). The per-round delta is the diff against the player's
    previous appearance.

    Edge cases handled:
    - Player skipped a round → diff = 0 (cumulative unchanged).
    - First appearance of a player → keep the cumulative value as the per-round value.
    - Cartola correction lowering a scout → kept as negative (caller's choice),
      except SG (clean sheet) which is clipped at 0.
    """
    df = df.sort_values(["id_atleta", "rodada"], kind="mergesort").reset_index(drop=True).copy()
    df[scout_cols] = df[scout_cols].fillna(0.0)

    diffs = df.groupby("id_atleta", sort=False)[scout_cols].diff()
    first = df.groupby("id_atleta", sort=False).cumcount() == 0
    diffs.loc[first, :] = df.loc[first, scout_cols].values

    if "SG" in scout_cols:
        diffs["SG"] = diffs["SG"].clip(lower=0)

    df[scout_cols] = diffs.values
    return df


def process(df: pd.DataFrame, *, accumulated: bool, has_scouts: bool) -> pd.DataFrame:
    """Apply the canonical scout pipeline.

    Behavior:
    - has_scouts=False → all 21 SCOUTS become NaN columns (e.g. 2025).
    - has_scouts=True  → rename PE/RB/DD; missing scout values within a year fill
      with 0.0; if accumulated, run disaccumulate_scouts on present scouts.

    Scout columns absent from the input remain absent → they will be NaN after
    the final reindex against CANONICAL_COLUMNS in nodes.year_dataframe.
    """
    df = df.copy()

    if not has_scouts:
        for col in SCOUTS:
            df[col] = pd.NA
        return df

    df = harmonize_scout_names(df)
    present = [c for c in SCOUTS if c in df.columns]
    if not present:
        return df
    df[present] = df[present].fillna(0.0)
    if accumulated:
        df = disaccumulate_scouts(df, scout_cols=present)
    return df
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_scouts.py -v
```

Expected: 10 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/scouts.py tests/unit/test_scouts.py
git commit -m "feat(aggregation): add scouts processing (rename, disaccumulate, fill)"
```

---

## Phase 2 — Readers (per raw shape)

### Task 2.1: Create test fixtures (synthetic mini CSVs)

**Files:**
- Create: `tests/fixtures/2014/2014_jogadores.csv`
- Create: `tests/fixtures/2014/2014_scouts_raw.csv`
- Create: `tests/fixtures/2014/2014_times.csv`
- Create: `tests/fixtures/2017/2017_scouts_raw.csv`
- Create: `tests/fixtures/2018/rodada-1.csv`
- Create: `tests/fixtures/2018/rodada-2.csv`

- [ ] **Step 1: Create the 2014 fixture (one player, two rounds)**

`tests/fixtures/2014/2014_jogadores.csv`:

```csv
ID,Apelido,ClubeID,PosicaoID
80583,Lucas Lima,277,4
36443,Test Player,262,5
```

`tests/fixtures/2014/2014_scouts_raw.csv` (note: `Posicao` is INT in real 2014 data, redundant with `PosicaoID` in jogadores — the reader drops it):

```csv
AtletaID,Rodada,ClubeID,Participou,Posicao,Jogos,Pontos,PontosMedia,Preco,PrecoVariacao,Partida,Mando,Titular,Substituido,TempoJogado,Nota,FS,PE,A,FT,FD,FF,G,I,PP,RB,FC,GC,CA,CV,SG,DD,DP,GS
80583,1,277,1,4,1,5.5,5.5,9.0,0.5,1,1,1,0,90,7.0,2,1,0,0,1,0,0,1,0,3,1,0,0,0,0,0,0,0
80583,2,277,1,4,2,7.0,6.25,9.5,0.5,2,1,1,0,90,7.0,1,0,1,0,0,2,1,0,0,2,0,0,1,0,1,0,0,0
36443,1,262,1,5,1,2.0,2.0,8.0,0.0,1,0,1,0,90,5.0,1,0,0,0,0,1,0,0,0,1,2,0,0,0,0,0,0,0
36443,2,262,0,5,1,0.0,1.0,8.0,0.0,,,0,,,,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

`tests/fixtures/2014/2014_times.csv`:

```csv
ID,Nome,Abreviacao,Slug
262,Flamengo,FLA,flamengo
277,Santos,SAN,santos
```

- [ ] **Step 2: Create the 2017 monolithic fixture**

`tests/fixtures/2017/2017_scouts_raw.csv`:

```csv
,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,athletes.atletas.scout,atletas.apelido,atletas.atleta_id,atletas.clube.id.full.name,atletas.clube_id,atletas.foto,atletas.jogos_num,atletas.media_num,atletas.nome,atletas.pontos_num,atletas.posicao_id,atletas.preco_num,Rodada,atletas.status_id,atletas.variacao_num
0,0,0,0,0,0,1,0,0,2,0,0,0,0,0,1,0,1,0,,Juan,36540,Flamengo,FLA,https://example.com/foto.png,1,5.0,Juan Silveira dos Santos,5.0,zag,8.0,1,Provável,0.0
1,1,0,0,0,0,2,1,1,3,0,1,0,0,1,0,0,2,1,,Juan,36540,Flamengo,FLA,https://example.com/foto.png,2,5.5,Juan Silveira dos Santos,6.0,zag,8.5,2,Provável,0.5
```

- [ ] **Step 3: Create the 2018 round-files fixture**

`tests/fixtures/2018/rodada-1.csv`:

```csv
"","atletas.nome","atletas.slug","atletas.apelido","atletas.foto","atletas.atleta_id","atletas.rodada_id","atletas.clube_id","atletas.posicao_id","atletas.status_id","atletas.pontos_num","atletas.preco_num","atletas.variacao_num","atletas.media_num","atletas.clube.id.full.name","FC","FD","FF","FS","G","I","RB","CA","PE","A","SG","DD","FT","GS","CV","GC","DP","PP"
"1","Matheus Ferraz Pereira","matheus-ferraz","Matheus Ferraz","https://example.com/p.png",38632,1,"AME","zag","Nulo",2.5,6.0,0.0,2.5,"Atlético-MG",1,0,0,1,0,0,2,0,0,0,1,0,0,0,0,0,0,0
```

`tests/fixtures/2018/rodada-2.csv`:

```csv
"","atletas.nome","atletas.slug","atletas.apelido","atletas.foto","atletas.atleta_id","atletas.rodada_id","atletas.clube_id","atletas.posicao_id","atletas.status_id","atletas.pontos_num","atletas.preco_num","atletas.variacao_num","atletas.media_num","atletas.clube.id.full.name","FC","FD","FF","FS","G","I","RB","CA","PE","A","SG","DD","FT","GS","CV","GC","DP","PP"
"1","Matheus Ferraz Pereira","matheus-ferraz","Matheus Ferraz","https://example.com/p.png",38632,2,"AME","zag","Provável",4.0,6.5,0.5,3.25,"Atlético-MG",2,1,0,2,0,0,3,1,0,0,2,0,0,0,0,0,0,0
```

- [ ] **Step 4: Verify fixtures load**

```bash
uv run python -c "
import pandas as pd
print(pd.read_csv('tests/fixtures/2014/2014_scouts_raw.csv').shape)
print(pd.read_csv('tests/fixtures/2017/2017_scouts_raw.csv').shape)
print(pd.read_csv('tests/fixtures/2018/rodada-1.csv').shape)
"
```

Expected: `(4, 34)`, `(2, 34)`, `(1, 34)`.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add synthetic mini-CSV fixtures for 2014/2017/2018"
```

---

### Task 2.2: `readers.py` — implement and test the three readers

**Files:**
- Create: `src/cartola/aggregation/readers.py`
- Create: `tests/unit/test_readers.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_readers.py`:

```python
"""Tests for the three raw-shape readers."""
import pandas as pd

from cartola.aggregation import readers


def test_read_season_files_2014_merges_jogadores_scouts_times(fixtures_dir):
    df = readers.read_season_files(str(fixtures_dir / "2014"), year=2014)
    # 4 rows in 2014_scouts_raw.csv → 4 rows after merge
    assert len(df) == 4
    # nome_clube comes from the times-file merge ("Nome" column)
    assert "nome_clube" in df.columns or "Nome" in df.columns
    # Apelido from jogadores merge
    assert "Apelido" in df.columns or "apelido" in df.columns


def test_read_season_files_2014_brings_scout_columns(fixtures_dir):
    df = readers.read_season_files(str(fixtures_dir / "2014"), year=2014)
    # legacy scout names should be present pre-rename
    assert {"FS", "PE", "G", "RB", "DD", "SG"}.issubset(df.columns)


def test_read_monolithic_2017(fixtures_dir):
    df = readers.read_monolithic(str(fixtures_dir / "2017"), year=2017)
    assert len(df) == 2
    assert "atletas.atleta_id" in df.columns
    assert "Rodada" in df.columns


def test_read_round_files_2018_concats_all_rounds(fixtures_dir):
    df = readers.read_round_files(str(fixtures_dir / "2018"), year=2018)
    # rodada-1 + rodada-2 → 2 rows
    assert len(df) == 2
    assert set(df["atletas.rodada_id"].unique()) == {1, 2}


def test_read_round_files_handles_missing_dir(tmp_path):
    """Empty year directory → empty DataFrame, not an error."""
    empty = tmp_path / "empty_year"
    empty.mkdir()
    df = readers.read_round_files(str(empty), year=2099)
    assert df.empty
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_readers.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/readers.py`:

```python
"""Raw-shape readers. Each reader returns a single per-(player, round) DataFrame
with the raw column names — renaming/harmonization happens downstream.

Three shapes correspond to three eras of the project:
- season_files: jogadores.csv + scouts_raw.csv + times.csv (2014–2016)
- monolithic:   single <year>_scouts_raw.csv with player+team metadata (2017)
- round_files:  rodada-N.csv per round, concatenated (2018+)
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_ROUND_FILE_RE = re.compile(r"rodada-(\d+)\.csv$", re.IGNORECASE)


def read_season_files(raw_dir: str, year: int) -> pd.DataFrame:
    """2014–2016: merge `<year>_scouts_raw.csv` (per-round data) with
    `<year>_jogadores.csv` (player metadata) and `<year>_times.csv` (team names).

    Returns a wide DataFrame keyed by (AtletaID, Rodada) with team `Nome`.
    """
    base = Path(raw_dir)
    scouts = pd.read_csv(base / f"{year}_scouts_raw.csv")
    jogadores = pd.read_csv(base / f"{year}_jogadores.csv")
    times = pd.read_csv(base / f"{year}_times.csv")

    # 2014 scouts has a `Posicao` column that is redundant with jogadores.PosicaoID
    # (both int, same values). Drop to avoid a duplicate column after the merge.
    if "Posicao" in scouts.columns:
        scouts = scouts.drop(columns=["Posicao"])

    jog_keep = jogadores[["ID", "Apelido", "PosicaoID"]].rename(columns={"ID": "AtletaID"})
    df = scouts.merge(jog_keep, on="AtletaID", how="left")

    times_keep = times[["ID", "Nome"]].rename(columns={"ID": "ClubeID"})
    df = df.merge(times_keep, on="ClubeID", how="left")

    return df


def read_monolithic(raw_dir: str, year: int) -> pd.DataFrame:
    """2017: a single CSV containing player metadata + scouts in one wide table."""
    path = Path(raw_dir) / f"{year}_scouts_raw.csv"
    return pd.read_csv(path)


def read_round_files(raw_dir: str, year: int) -> pd.DataFrame:
    """2018+: per-round files `rodada-N.csv`. Concat everything."""
    base = Path(raw_dir)
    if not base.exists():
        logger.warning("Raw dir does not exist: %s", base)
        return pd.DataFrame()

    files = sorted(
        (p for p in base.glob("rodada-*.csv") if _ROUND_FILE_RE.search(p.name)),
        key=lambda p: int(_ROUND_FILE_RE.search(p.name).group(1)),
    )
    if not files:
        logger.warning("No rodada-*.csv files in %s", base)
        return pd.DataFrame()

    frames = [pd.read_csv(p) for p in files]
    return pd.concat(frames, ignore_index=True)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_readers.py -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/readers.py tests/unit/test_readers.py
git commit -m "feat(aggregation): add three raw-shape readers (season/monolithic/round)"
```

---

## Phase 3 — Catalog, Hamilton nodes, driver

### Task 3.1: `catalog.py` — YearConfig + YEAR_REGISTRY

**Files:**
- Create: `src/cartola/aggregation/catalog.py`
- Create: `tests/unit/test_catalog.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_catalog.py`:

```python
"""Tests for the YEAR_REGISTRY catalog."""
from pathlib import Path

import pytest

from cartola.aggregation import catalog


EXPECTED_YEARS = list(range(2014, 2027))


def test_registry_covers_2014_to_2026():
    assert sorted(catalog.YEAR_REGISTRY) == EXPECTED_YEARS


def test_accumulated_years_match_spec():
    expected_accumulated = {2015, 2017, 2018, 2019, 2020, 2021, 2022}
    actual = {y for y, cfg in catalog.YEAR_REGISTRY.items() if cfg.accumulated}
    assert actual == expected_accumulated


def test_2025_has_no_scouts_flag():
    assert catalog.YEAR_REGISTRY[2025].has_scouts is False


def test_all_years_have_existing_raw_dir(repo_root):
    missing = [
        y for y, cfg in catalog.YEAR_REGISTRY.items()
        if not (repo_root / cfg.raw_dir).is_dir()
    ]
    assert missing == [], f"Years with missing raw dirs: {missing}"


@pytest.mark.parametrize("year", EXPECTED_YEARS)
def test_each_year_has_callable_reader(year):
    cfg = catalog.YEAR_REGISTRY[year]
    assert callable(cfg.reader)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_catalog.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/catalog.py`:

```python
"""Single source of truth for per-year metadata.

Adding year N+1 = a single new entry in YEAR_REGISTRY (and one extra parameter
in nodes.aggregated()).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from cartola.aggregation.readers import (
    read_monolithic,
    read_round_files,
    read_season_files,
)


@dataclass(frozen=True)
class YearConfig:
    year: int
    raw_dir: str
    reader: Callable[[str, int], pd.DataFrame]
    accumulated: bool = False
    has_scouts: bool = True


YEAR_REGISTRY: dict[int, YearConfig] = {
    2014: YearConfig(2014, "data/01_raw/2014", read_season_files, accumulated=False),
    2015: YearConfig(2015, "data/01_raw/2015", read_season_files, accumulated=True),
    2016: YearConfig(2016, "data/01_raw/2016", read_season_files, accumulated=False),
    2017: YearConfig(2017, "data/01_raw/2017", read_monolithic,   accumulated=True),
    2018: YearConfig(2018, "data/01_raw/2018", read_round_files,  accumulated=True),
    2019: YearConfig(2019, "data/01_raw/2019", read_round_files,  accumulated=True),
    2020: YearConfig(2020, "data/01_raw/2020", read_round_files,  accumulated=True),
    2021: YearConfig(2021, "data/01_raw/2021", read_round_files,  accumulated=True),
    2022: YearConfig(2022, "data/01_raw/2022", read_round_files,  accumulated=True),
    2023: YearConfig(2023, "data/01_raw/2023", read_round_files,  accumulated=False),
    2024: YearConfig(2024, "data/01_raw/2024", read_round_files,  accumulated=False),
    2025: YearConfig(2025, "data/01_raw/2025", read_round_files,  accumulated=False, has_scouts=False),
    2026: YearConfig(2026, "data/01_raw/2026", read_round_files,  accumulated=False),
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_catalog.py -v
```

Expected: 17 PASS (4 single + 13 parametrized).

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/catalog.py tests/unit/test_catalog.py
git commit -m "feat(aggregation): add YEAR_REGISTRY catalog (2014–2026)"
```

---

### Task 3.2: `nodes.py` — Hamilton @parameterize nodes

**Files:**
- Create: `src/cartola/aggregation/nodes.py`
- Create: `tests/unit/test_nodes.py`

- [ ] **Step 1: Write the failing test**

`tests/unit/test_nodes.py`:

```python
"""Tests for the Hamilton nodes module."""
import inspect

import pandas as pd
from hamilton import driver

from cartola.aggregation import nodes
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS


def test_module_exposes_year_dataframe_and_aggregated():
    assert "year_dataframe" in dir(nodes)
    assert "aggregated" in dir(nodes)


def test_aggregated_signature_matches_registry():
    sig = inspect.signature(nodes.aggregated)
    expected = {f"year_{y}" for y in YEAR_REGISTRY}
    assert set(sig.parameters) == expected


def test_driver_dag_has_one_node_per_year_plus_aggregated():
    """@parameterize materializes year_<Y> nodes only at driver-build time."""
    drv = driver.Builder().with_modules(nodes).build()
    node_names = {n.name for n in drv.list_available_variables()}
    expected_years = {f"year_{y}" for y in YEAR_REGISTRY}
    assert expected_years.issubset(node_names)
    assert "aggregated" in node_names


def test_aggregated_concats_input_frames():
    df_a = pd.DataFrame({c: pd.Series(dtype="object") for c in CANONICAL_COLUMNS})
    kwargs = {f"year_{y}": df_a for y in YEAR_REGISTRY}
    out = nodes.aggregated(**kwargs)
    assert list(out.columns) == CANONICAL_COLUMNS
    assert len(out) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_nodes.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Write the implementation**

`src/cartola/aggregation/nodes.py`:

```python
"""Hamilton nodes for the aggregation pipeline.

One per-year node is generated dynamically from YEAR_REGISTRY via
@parameterize, plus a final `aggregated` node that concatenates them.
"""
from __future__ import annotations

import pandas as pd
from hamilton.function_modifiers import parameterize, value

from cartola.aggregation import columns, player, scouts, team
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import CANONICAL_COLUMNS

_PARAMS = {f"year_{y}": {"year": value(y)} for y in YEAR_REGISTRY}


@parameterize(**_PARAMS)
def year_dataframe(year: int) -> pd.DataFrame:
    """Reads raw data for `year` and applies entity-by-entity transformations
    to produce one year of data in the canonical schema.
    """
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
    """Concat all year DataFrames, preserving CANONICAL_COLUMNS order."""
    frames = [
        year_2014, year_2015, year_2016, year_2017, year_2018, year_2019,
        year_2020, year_2021, year_2022, year_2023, year_2024, year_2025, year_2026,
    ]
    return (
        pd.concat(frames, ignore_index=True)
        .reset_index(drop=True)
        .reindex(columns=CANONICAL_COLUMNS)
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/unit/test_nodes.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/nodes.py tests/unit/test_nodes.py
git commit -m "feat(aggregation): add Hamilton nodes (per-year + aggregated)"
```

---

### Task 3.3: `driver.py` — Hamilton driver, run, persist

**Files:**
- Create: `src/cartola/aggregation/driver.py`

- [ ] **Step 1: Write the implementation directly (no unit test — covered by integration tests)**

`src/cartola/aggregation/driver.py`:

```python
"""Hamilton driver wrapper: builds the DAG, runs it, persists outputs.

`track=True` enables the Hamilton UI tracker (requires `sf-hamilton-ui`).
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from hamilton import driver

from cartola.aggregation import nodes
from cartola.aggregation.catalog import YEAR_REGISTRY

logger = logging.getLogger(__name__)

PRIMARY_DIR = Path("data/03_primary")
AGGREGATED_DIR = Path("data/04_aggregated")


def build_driver(track: bool = False) -> driver.Driver:
    """Build a Hamilton driver from the nodes module.

    `track=True` attaches the Hamilton UI tracker so the run shows up in the UI.
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
            logger.warning(
                "Hamilton UI not installed — install with `uv sync --extra ui` to enable --track."
            )
    return builder.build()


def run(years: list[int] | None = None, track: bool = False) -> pd.DataFrame:
    """Execute the pipeline.

    If `years` is None or matches all configured years → write the per-year CSVs
    AND the final aggregated CSV.

    If `years` is a strict subset → write only the per-year CSVs (no aggregation;
    aggregating a partial run could mislead downstream consumers).
    """
    drv = build_driver(track=track)

    available = sorted(YEAR_REGISTRY)
    selected = sorted(years) if years else available
    invalid = [y for y in selected if y not in YEAR_REGISTRY]
    if invalid:
        raise ValueError(f"Years not in YEAR_REGISTRY: {invalid}")

    PRIMARY_DIR.mkdir(parents=True, exist_ok=True)

    per_year_outputs = [f"year_{y}" for y in selected]
    results = drv.execute(per_year_outputs)
    for y, name in zip(selected, per_year_outputs):
        df = results[name]
        out_path = PRIMARY_DIR / f"cartola_{y}.csv"
        df.to_csv(out_path, index=False)
        logger.info("Wrote %s (%d rows)", out_path, len(df))

    if selected != available:
        logger.info("Partial run (%d/%d years) — skipping aggregated CSV", len(selected), len(available))
        return pd.concat([results[name] for name in per_year_outputs], ignore_index=True)

    AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)
    aggregated_df = drv.execute(["aggregated"])["aggregated"]
    out = AGGREGATED_DIR / f"cartola_{available[0]}_{available[-1]}.csv"
    aggregated_df.to_csv(out, index=False)
    logger.info("Wrote %s (%d rows)", out, len(aggregated_df))
    return aggregated_df


def launch_ui() -> None:
    """Launch the Hamilton UI server (requires `sf-hamilton-ui`)."""
    try:
        from hamilton_ui import commands  # type: ignore[import-untyped]
    except ImportError as exc:
        raise SystemExit(
            "Hamilton UI is not installed. Run `uv sync --extra ui` and try again."
        ) from exc
    commands.run()  # blocks; serves http://localhost:8241 by default
```

- [ ] **Step 2: Smoke check the driver imports cleanly**

```bash
uv run python -c "from cartola.aggregation.driver import build_driver; print(build_driver())"
```

Expected: prints something like `<hamilton.driver.Driver object at ...>` (no errors).

- [ ] **Step 3: Commit**

```bash
git add src/cartola/aggregation/driver.py
git commit -m "feat(aggregation): add Hamilton driver, run() and launch_ui()"
```

---

## Phase 4 — Pandera schema validation

### Task 4.1: Add `AggregatedSchema` to `schema.py`

**Files:**
- Modify: `src/cartola/aggregation/schema.py` (append the Pandera model at the bottom)
- Create: `tests/data_quality/test_pandera_schema.py`

- [ ] **Step 1: Write the failing test**

`tests/data_quality/test_pandera_schema.py`:

```python
"""Pandera schema validation tests."""
import pandas as pd
import pandera as pa
import pytest

from cartola.aggregation.schema import AggregatedSchema, CANONICAL_COLUMNS, SCOUTS


def _good_row(**overrides):
    base = {col: pd.NA for col in CANONICAL_COLUMNS}
    base.update({
        "ano": 2024,
        "rodada": 1,
        "id_clube": 262,
        "nome_clube": "Flamengo",
        "id_atleta": 1,
        "apelido": "Foo",
        "slug": "foo",
        "posicao": "mei",
        "pontuacao": 5.0,
        "media": 5.0,
        "preco": 8.0,
        "variacao": 0.0,
    })
    for col in SCOUTS:
        base[col] = 0.0
    base.update(overrides)
    return base


def _build_df(rows):
    """Build a small DataFrame with dtypes that mirror what the real pipeline produces.

    `coerce=True` on the schema lets Pandera handle minor numeric upcasts.
    """
    df = pd.DataFrame(rows, columns=CANONICAL_COLUMNS)
    df["ano"] = df["ano"].astype("int64")
    df["rodada"] = df["rodada"].astype("int64")
    df["id_clube"] = df["id_clube"].astype("Int32")
    df["id_atleta"] = df["id_atleta"].astype("int64")
    df["num_jogos"] = df["num_jogos"].astype("Int16")
    for col in ("nome_clube", "nome", "apelido", "apelido_abreviado", "slug", "foto", "posicao", "status"):
        df[col] = df[col].astype("string")
    for col in ("pontuacao", "media", "preco", "variacao", *SCOUTS):
        df[col] = df[col].astype("float64")
    return df


def test_valid_minimal_row_passes():
    df = _build_df([_good_row()])
    AggregatedSchema.validate(df)


def test_id_clube_nullable_passes():
    df = _build_df([_good_row(id_clube=pd.NA, nome_clube="Time XYZ")])
    AggregatedSchema.validate(df)


def test_rodada_out_of_range_fails():
    df = _build_df([_good_row(rodada=99)])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


def test_ano_out_of_range_fails():
    df = _build_df([_good_row(ano=1990)])
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)


def test_unique_ano_rodada_id_atleta_violation_fails():
    rows = [_good_row(id_atleta=1), _good_row(id_atleta=1)]
    df = _build_df(rows)
    with pytest.raises(pa.errors.SchemaError):
        AggregatedSchema.validate(df)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/data_quality/test_pandera_schema.py -v
```

Expected: `ImportError` for `AggregatedSchema` (not yet defined).

- [ ] **Step 3: Append the Pandera model to `src/cartola/aggregation/schema.py`**

Note: we use generic `int`/`float`/`str` dtypes (not `pd.Int*Dtype`) so the schema validates regardless of whether the column is numpy-int64 or pandas-Int64; `pd.Int32Dtype` is used only for `id_clube` because we explicitly need nullable integers there. `coerce=True` is enabled at the model level to allow Pandera to upcast minor dtype differences.

We also use `import pandera.pandas as pa` (instead of the bare `import pandera as pa`) to silence the FutureWarning Pandera 0.31+ emits when pandas-specific classes are imported from the top-level module.

Add at the end of the file:

```python

# ---------------------------------------------------------------------------
# Pandera schema (data-quality contract)
# ---------------------------------------------------------------------------
import pandera.pandas as pa  # noqa: E402  (kept here to keep the constants section clean)
from pandera.typing import Series  # noqa: E402


class AggregatedSchema(pa.DataFrameModel):
    """Pandera contract for the final aggregated DataFrame."""

    ano: Series[int] = pa.Field(ge=2014, le=2030)
    rodada: Series[int] = pa.Field(ge=0, le=38)
    id_clube: Series[pd.Int32Dtype] = pa.Field(nullable=True)
    nome_clube: Series[str] = pa.Field(nullable=True)
    id_atleta: Series[int]

    nome: Series[str] = pa.Field(nullable=True)
    apelido: Series[str] = pa.Field(nullable=True)
    apelido_abreviado: Series[str] = pa.Field(nullable=True)
    slug: Series[str] = pa.Field(nullable=True)
    foto: Series[str] = pa.Field(nullable=True)
    posicao: Series[str] = pa.Field(nullable=True)
    status: Series[str] = pa.Field(nullable=True)

    pontuacao: Series[float] = pa.Field(nullable=True)
    media: Series[float] = pa.Field(nullable=True)
    preco: Series[float] = pa.Field(nullable=True)

    variacao: Series[float] = pa.Field(nullable=True)
    num_jogos: Series[pd.Int16Dtype] = pa.Field(nullable=True)

    A: Series[float] = pa.Field(nullable=True, ge=0)
    CA: Series[float] = pa.Field(nullable=True, ge=0)
    CV: Series[float] = pa.Field(nullable=True, ge=0)
    DE: Series[float] = pa.Field(nullable=True, ge=0)
    DP: Series[float] = pa.Field(nullable=True, ge=0)
    DS: Series[float] = pa.Field(nullable=True, ge=0)
    FC: Series[float] = pa.Field(nullable=True, ge=0)
    FD: Series[float] = pa.Field(nullable=True, ge=0)
    FF: Series[float] = pa.Field(nullable=True, ge=0)
    FS: Series[float] = pa.Field(nullable=True, ge=0)
    FT: Series[float] = pa.Field(nullable=True, ge=0)
    G: Series[float] = pa.Field(nullable=True, ge=0)
    GC: Series[float] = pa.Field(nullable=True, ge=0)
    GS: Series[float] = pa.Field(nullable=True, ge=0)
    I: Series[float] = pa.Field(nullable=True, ge=0)
    PC: Series[float] = pa.Field(nullable=True, ge=0)
    # PI/DS can be negative after disaccumulation if Cartola corrected backwards.
    PI: Series[float] = pa.Field(nullable=True)
    PP: Series[float] = pa.Field(nullable=True, ge=0)
    PS: Series[float] = pa.Field(nullable=True, ge=0)
    SG: Series[float] = pa.Field(nullable=True, ge=0)
    V: Series[float] = pa.Field(nullable=True, ge=0)

    class Config:
        strict = True
        coerce = True
        unique = ["ano", "rodada", "id_atleta"]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/data_quality/test_pandera_schema.py -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/cartola/aggregation/schema.py tests/data_quality/test_pandera_schema.py
git commit -m "feat(aggregation): add Pandera AggregatedSchema (38 cols, uniqueness check)"
```

---

## Phase 5 — CLI

### Task 5.1: `cli.py` — `aggregate` and `viz` commands

**Files:**
- Create: `src/cartola/cli.py`

- [ ] **Step 1: Write the implementation directly (CLI smoke-tested in next step)**

`src/cartola/cli.py`:

```python
"""Typer CLI for the Cartola aggregation pipeline.

Commands:
- aggregate: run the pipeline and write per-year + aggregated CSVs.
- viz:       launch the Hamilton UI (requires the `ui` extra).
"""
from __future__ import annotations

import logging
from typing import Optional

import typer

from cartola.aggregation import driver

app = typer.Typer(add_completion=False, no_args_is_help=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _parse_years(raw: Optional[str]) -> Optional[list[int]]:
    if raw is None:
        return None
    return [int(y.strip()) for y in raw.split(",") if y.strip()]


@app.command()
def aggregate(
    years: Optional[str] = typer.Option(
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
```

- [ ] **Step 2: Smoke check the CLI**

```bash
uv run cartola --help
uv run cartola aggregate --help
```

Expected: typer prints the help text for each command (no errors).

- [ ] **Step 3: Commit**

```bash
git add src/cartola/cli.py
git commit -m "feat(cli): add Typer entry point with aggregate and viz commands"
```

---

## Phase 6 — Integration and smoke tests

### Task 6.1: End-to-end integration test against fixtures

**Note:** We cannot easily monkey-patch `YEAR_REGISTRY` because `@parameterize` captures it at import time and `aggregated()`'s signature is fixed to all 13 years. So this test calls the same chain as `nodes.year_dataframe` directly with fixture paths, which exercises every entity module + every reader on a real DataFrame end-to-end.

**Files:**
- Create: `tests/integration/test_pipeline_end_to_end.py`

- [ ] **Step 1: Write the failing test**

`tests/integration/test_pipeline_end_to_end.py`:

```python
"""Integration test: exercise the full per-year pipeline against synthetic fixtures.

Calls the same chain as nodes.year_dataframe directly (without going through
Hamilton) so we can pass fixture paths instead of the production raw dirs.
"""
from pathlib import Path

import pandas as pd
import pytest

from cartola.aggregation import columns, driver, player, scouts, team
from cartola.aggregation.catalog import YearConfig
from cartola.aggregation.readers import read_monolithic, read_round_files, read_season_files
from cartola.aggregation.schema import CANONICAL_COLUMNS


def _process_year(cfg: YearConfig, year: int) -> pd.DataFrame:
    """Replicates nodes.year_dataframe with an injected YearConfig."""
    raw = cfg.reader(cfg.raw_dir, year)
    df = columns.rename_columns(raw)
    df = team.resolve_id_clube(df)
    df = player.map_position(df)
    df = player.map_status(df)
    df = player.fill_missing_slug(df)
    df = scouts.process(df, accumulated=cfg.accumulated, has_scouts=cfg.has_scouts)
    df["ano"] = year
    return df.reindex(columns=CANONICAL_COLUMNS)


@pytest.fixture
def fixture_configs(fixtures_dir: Path) -> dict[int, YearConfig]:
    return {
        2014: YearConfig(2014, str(fixtures_dir / "2014"), read_season_files),
        2017: YearConfig(2017, str(fixtures_dir / "2017"), read_monolithic, accumulated=True),
        2018: YearConfig(2018, str(fixtures_dir / "2018"), read_round_files, accumulated=True),
    }


def test_year_2014_pipeline_against_fixture(fixture_configs):
    df = _process_year(fixture_configs[2014], 2014)
    assert list(df.columns) == CANONICAL_COLUMNS
    assert len(df) == 4
    # Flamengo + Santos resolved from times.csv merge.
    assert set(df["id_clube"].dropna().tolist()) == {262, 277}
    # 2014 has no status data — column should be all NaN.
    assert df["status"].isna().all()


def test_year_2018_resolves_atl_to_atletico_mg(fixture_configs):
    df = _process_year(fixture_configs[2018], 2018)
    # nome_clube="Atlético-MG" → id_clube=282 (not the buggy "ATL" abbreviation).
    assert (df["id_clube"] == 282).all()
    # 2018 is accumulated → per-round FC delta from round 1 (cumulative=1) to round 2 (cumulative=2) is 1.
    fc_round_2 = df.loc[df["rodada"] == 2, "FC"].iloc[0]
    assert fc_round_2 == 1.0


def test_year_2017_pipeline_against_fixture(fixture_configs):
    df = _process_year(fixture_configs[2017], 2017)
    assert list(df.columns) == CANONICAL_COLUMNS
    assert len(df) == 2
    # Status was already a string label ("Provável") — should pass through.
    assert (df["status"] == "Provável").all()


def test_per_year_write_round_trip(tmp_path, fixture_configs, monkeypatch):
    """Write a per-year DataFrame to CSV and re-read it; columns must round-trip."""
    monkeypatch.setattr(driver, "PRIMARY_DIR", tmp_path / "03_primary")
    driver.PRIMARY_DIR.mkdir(parents=True, exist_ok=True)

    df = _process_year(fixture_configs[2014], 2014)
    out = driver.PRIMARY_DIR / "cartola_2014.csv"
    df.to_csv(out, index=False)

    reread = pd.read_csv(out)
    assert list(reread.columns) == CANONICAL_COLUMNS
    assert len(reread) == len(df)
```

- [ ] **Step 2: Run test to verify it fails (then passes once Phases 1–3 are in place)**

```bash
uv run pytest tests/integration/test_pipeline_end_to_end.py -v
```

Expected: 4 PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_pipeline_end_to_end.py
git commit -m "test(integration): end-to-end pipeline against synthetic fixtures"
```

---

### Task 6.2: Real-data smoke test

**Files:**
- Create: `tests/data_quality/test_real_data_smoke.py`

- [ ] **Step 1: Write the smoke test**

`tests/data_quality/test_real_data_smoke.py`:

```python
"""Smoke test: run the full pipeline on real raw data and assert sanity bounds.

Marked `slow` so contributors can skip it locally with `pytest -m "not slow"`.
The CI / manual full run executes it.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera as pa
import pytest

from cartola.aggregation import driver
from cartola.aggregation.catalog import YEAR_REGISTRY
from cartola.aggregation.schema import AggregatedSchema, SCOUTS

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def aggregated_df(tmp_path_factory) -> pd.DataFrame:
    out_dir = tmp_path_factory.mktemp("smoke")
    # Redirect the driver's outputs to a tmp dir so we don't clobber real data
    driver.PRIMARY_DIR = out_dir / "03_primary"
    driver.AGGREGATED_DIR = out_dir / "04_aggregated"
    return driver.run(years=None, track=False)


def test_pandera_schema_validates(aggregated_df):
    AggregatedSchema.validate(aggregated_df, lazy=True)


def test_all_years_present(aggregated_df):
    expected = set(YEAR_REGISTRY)
    got = set(aggregated_df["ano"].astype(int).unique())
    assert expected == got


@pytest.mark.parametrize("year", [y for y in range(2018, 2027) if y != 2025])
def test_2018_plus_row_count_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    assert 5_000 <= len(sub) <= 35_000, f"Unreasonable row count for {year}: {len(sub)}"


@pytest.mark.parametrize("year", [y for y in range(2018, 2027) if y != 2025])
def test_2018_plus_round_count_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    n_rounds = sub["rodada"].nunique()
    # Brasileirão has 38 rounds; tolerate a partial in-progress season at 30+.
    assert 30 <= n_rounds <= 38, f"Unreasonable round count for {year}: {n_rounds}"


@pytest.mark.parametrize("year", [y for y in range(2018, 2027) if y != 2025])
def test_2018_plus_total_goals_in_bounds(aggregated_df, year):
    sub = aggregated_df[aggregated_df["ano"] == year]
    total_g = sub["G"].sum(skipna=True)
    assert 100 <= total_g <= 1_500, f"Unreasonable total goals for {year}: {total_g}"


def test_2025_has_no_scouts(aggregated_df):
    sub = aggregated_df[aggregated_df["ano"] == 2025]
    for col in SCOUTS:
        assert sub[col].isna().all(), f"2025 should have NaN for scout {col}, got non-NaN"


def test_uniqueness_of_ano_rodada_id_atleta(aggregated_df):
    dups = aggregated_df.duplicated(subset=["ano", "rodada", "id_atleta"]).sum()
    assert dups == 0, f"{dups} duplicate (ano, rodada, id_atleta) tuples found"
```

- [ ] **Step 2: Register the `slow` marker in `pyproject.toml`**

Append under `[tool.pytest.ini_options]` (modify the existing block):

```toml
[tool.pytest.ini_options]
addopts = "--cov-report term-missing --cov src/cartola -ra"
testpaths = ["tests"]
markers = ["slow: real-data smoke tests; skip with -m 'not slow'"]
```

- [ ] **Step 3: Run all the fast tests first (sanity)**

```bash
uv run pytest -m "not slow" -v
```

Expected: every previously-added test passes; smoke test is skipped.

- [ ] **Step 4: Run the smoke test against real data**

```bash
uv run pytest tests/data_quality/test_real_data_smoke.py -v
```

Expected: all assertions pass. **If a year fails a bound**: the bounds may need tuning (or there's a real data issue). Either tighten the assertion or open an issue and adjust the bound, with a comment explaining why.

- [ ] **Step 5: Commit**

```bash
git add tests/data_quality/test_real_data_smoke.py pyproject.toml
git commit -m "test(smoke): full-pipeline run on real data with pandera + sanity bounds"
```

---

## Phase 7 — Polish: Makefile, README, final clean run

### Task 7.1: Rewrite the `Makefile`

**Files:**
- Modify: `Makefile` (full rewrite)

- [ ] **Step 1: Replace the Makefile**

```makefile
.PHONY: help install aggregate viz test test-fast test-slow lint format clean

help:
	@echo "Available targets:"
	@echo "  install      - uv sync with dev + ui extras"
	@echo "  aggregate    - run the full aggregation pipeline"
	@echo "  viz          - launch Hamilton UI"
	@echo "  test         - run all tests (slow ones included)"
	@echo "  test-fast    - run all tests except those marked slow"
	@echo "  test-slow    - run only slow (real-data smoke) tests"
	@echo "  lint         - ruff check + mypy"
	@echo "  format       - ruff format + ruff check --fix"
	@echo "  clean        - remove pycache and other build artifacts"

install:
	uv sync --extra ui --group dev

aggregate:
	uv run cartola aggregate

viz:
	uv run cartola viz

test:
	uv run pytest -v

test-fast:
	uv run pytest -m "not slow" -v

test-slow:
	uv run pytest -m slow -v

lint:
	uv run ruff check src/cartola tests
	uv run mypy --ignore-missing-imports src/cartola

format:
	uv run ruff format src/cartola tests
	uv run ruff check --fix src/cartola tests

clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
```

- [ ] **Step 2: Smoke check `make help`**

```bash
make help
```

Expected: prints the list of targets.

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "chore(make): replace Kedro/Docker targets with uv-based workflow"
```

---

### Task 7.2: Update `README.md`

**Files:**
- Modify: `README.md` (remove the "preparing a pipeline" line; add a "Pipeline" section)

- [ ] **Step 1: Remove the legacy line**

Search the README for "preparando um pipeline" (or similar) and delete that line.

```bash
grep -n "preparando" README.md || echo "Already gone"
```

If a match is found, edit it out via your editor.

- [ ] **Step 2: Append a new "Pipeline" section**

Add this section after the project description (adjust placement to fit the existing README flow):

```markdown
## Pipeline (Cartola Aggregation)

Local-only data pipeline that aggregates Cartola FC data from 2014 to 2026 into
a single harmonized CSV (38 columns: context + team + player info + game state
+ 21 scouts).

### Setup

```bash
uv sync --extra ui --dev
```

### Running

```bash
uv run cartola aggregate              # all years
uv run cartola aggregate --years 2024,2025,2026
uv run cartola aggregate --track      # send to Hamilton UI
uv run cartola viz                    # launch UI at http://localhost:8241
```

Outputs:
- `data/03_primary/cartola_<year>.csv` — one per year processed
- `data/04_aggregated/cartola_2014_2026.csv` — final concat (full run only)

### Tests

```bash
make test-fast    # unit + integration; ~seconds
make test-slow    # smoke test on real data; ~minute
make test         # both
```

See `docs/superpowers/specs/2026-04-27-cartola-aggregation-pipeline-design.md`
for the full design rationale.
```

- [ ] **Step 3: Verify the README renders cleanly**

```bash
grep -n "Pipeline (Cartola Aggregation)" README.md
```

Expected: a single match.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): document the new aggregation pipeline"
```

---

### Task 7.3: Final full-pipeline run + verification

**Files:** none (run + inspect)

- [ ] **Step 1: Run the full pipeline once for real**

```bash
uv run cartola aggregate
```

Expected: prints `Wrote data/03_primary/cartola_<year>.csv` 13 times, then `Wrote data/04_aggregated/cartola_2014_2026.csv (N rows)`.

- [ ] **Step 2: Verify the aggregated CSV looks sane**

```bash
uv run python -c "
import pandas as pd
df = pd.read_csv('data/04_aggregated/cartola_2014_2026.csv')
print('shape:', df.shape)
print('years:', sorted(df['ano'].dropna().unique()))
print('rounds-per-year:')
print(df.groupby('ano')['rodada'].nunique())
"
```

Expected: 38 columns; all 13 years present; rounds-per-year between 30 and 38 for 2018+.

- [ ] **Step 3: Run the full test suite, including smoke**

```bash
make test
```

Expected: all tests pass (or document any tuned bounds).

- [ ] **Step 4: Commit any tuning changes (if needed)**

```bash
git status                        # confirm what changed
git add -A
git commit -m "chore: tune smoke test bounds based on full-data run"
```

(If nothing changed, skip this step.)

---

## Self-Review Checklist (run before declaring the plan ready)

- [ ] **Spec coverage** — confirm each spec section maps to a task:
  - §1 Problem / §2 Goals / §3 Non-Goals → addressed by overall plan.
  - §4 Constraints → Python 3.10+ in `pyproject.toml` (Task 0.2), CSV-only (Tasks 1–3 and 7), no DB.
  - §5 Tooling → Hamilton (Task 3.2), uv (Task 0.2), Typer (Task 5), Pandera (Task 4), pytest (all test tasks), Hamilton UI (Tasks 3.3, 5.1, 7.1).
  - §6 Schema → Task 1.1 + Task 4.1 (Pandera).
  - §6.1 TEAM_NAME_TO_ID → Task 1.3.
  - §7.1 Architecture → matches Tasks 1.2–1.5 + 3.x.
  - §7.2 Module structure → Tasks 1.1–1.5, 2.2, 3.1–3.3.
  - §7.3 Catalog → Task 3.1.
  - §7.4 Hamilton nodes → Task 3.2.
  - §7.5 Disaccumulation → Task 1.5.
  - §7.6 NaN policy → Task 1.5 (`process()`).
  - §7.7 CLI → Task 5.1.
  - §8 Test strategy → all `tests/unit/test_*.py` tasks + Task 6.1 (integration) + Task 6.2 (smoke).
  - §9 Removal plan → Task 0.1 (delete) + Task 0.2 (rewrite pyproject) + Task 7.1 (rewrite Makefile) + Task 7.2 (README).
  - §10 Maintenance → documented in spec; plan adds catalog/parameterize that already supports it.
  - §11 Risks → addressed in Task 5/7 (UI optional dep) + Task 6.2 (smoke catches regressions).
- [ ] **Placeholder scan** — no "TBD/TODO/implement later" anywhere in the plan.
- [ ] **Type/name consistency** — `process` (not `process_scouts`), `resolve_id_clube`, `map_position`, `map_status`, `fill_missing_slug`, `harmonize_scout_names`, `disaccumulate_scouts`, `rename_columns`, `read_season_files`, `read_monolithic`, `read_round_files`, `YEAR_REGISTRY`, `YearConfig`, `CANONICAL_COLUMNS`, `DTYPES`, `SCOUTS`, `POSITION_MAP`, `STATUS_MAP`, `TEAM_NAME_TO_ID`, `AggregatedSchema`, `SCOUT_RENAME_MAP`, `COLUMN_RENAME_MAP`, `COLUMNS_TO_DROP`, `build_driver`, `run`, `launch_ui` — all consistent across plan and spec.

---

**End of plan.** Total tasks: **18**. Estimated effort: 6–10 focused hours.
