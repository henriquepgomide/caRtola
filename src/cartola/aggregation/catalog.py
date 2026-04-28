"""Single source of truth for per-year metadata.

Adding year ``N+1`` is a single new entry in :data:`YEAR_REGISTRY` (and one
extra parameter in :func:`cartola.aggregation.nodes.aggregated`).
"""

from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from cartola.aggregation.readers import (
    read_mercado_json,
    read_monolithic,
    read_round_files,
    read_season_files,
)


@dataclass(frozen=True)
class YearConfig:
    """Per-year configuration for the aggregation pipeline.

    Attributes:
        year: Season year (e.g. ``2018``).
        raw_dir: Directory holding the raw inputs for ``year``.
        reader: One of the readers in :mod:`cartola.aggregation.readers`.
        accumulated: ``True`` when the source year ships season-cumulative
            scouts that need disaccumulation.
        has_scouts: ``True`` when the source year publishes scout columns.
    """

    year: int
    raw_dir: str
    reader: Callable[[str, int], pd.DataFrame]
    accumulated: bool = False
    has_scouts: bool = True


YEAR_REGISTRY: dict[int, YearConfig] = {
    2014: YearConfig(2014, "data/01_raw/2014", read_season_files, accumulated=False),
    2015: YearConfig(2015, "data/01_raw/2015", read_season_files, accumulated=True),
    2016: YearConfig(2016, "data/01_raw/2016", read_season_files, accumulated=False),
    2017: YearConfig(2017, "data/01_raw/2017", read_monolithic, accumulated=True),
    2018: YearConfig(2018, "data/01_raw/2018", read_round_files, accumulated=True),
    2019: YearConfig(2019, "data/01_raw/2019", read_round_files, accumulated=True),
    2020: YearConfig(2020, "data/01_raw/2020", read_round_files, accumulated=True),
    2021: YearConfig(2021, "data/01_raw/2021", read_mercado_json, accumulated=True),
    2022: YearConfig(2022, "data/01_raw/2022", read_round_files, accumulated=True),
    2023: YearConfig(2023, "data/01_raw/2023", read_round_files, accumulated=True),
    2024: YearConfig(2024, "data/01_raw/2024", read_round_files, accumulated=True),
    2025: YearConfig(2025, "data/01_raw/2025", read_round_files, accumulated=False, has_scouts=False),
    2026: YearConfig(2026, "data/01_raw/2026", read_round_files, accumulated=True),
}
