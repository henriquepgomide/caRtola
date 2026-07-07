"""Shared, hand-curated expectations about the real Cartola corpus.

Plain support module (not a test file itself) so multiple `data_quality`
test modules can assert against the same documented ground truth instead of
maintaining separate, potentially drifting copies.
"""

EXPECTED_ALL_NULL_SCOUTS: dict[int, set[str]] = {
    2014: {"PC", "PS", "V"},
    2015: {"PC", "PS", "V"},
    2016: {"PC", "PS", "V"},
    2017: {"PC", "PS", "V"},
    2018: {"PC", "PS", "V"},
    2019: {"PC", "PS", "V"},
    2020: {"PC", "PS", "V"},
    2021: {"V"},
    2022: {"V"},
    2023: set(),
    2024: set(),
    2025: {"PI"},
    2026: {"PI"},
}
"""Scouts the upstream Cartola API genuinely never published for a given
year (``PC``/``PS``/``V`` predate their introduction; ``PI`` stops being
published from 2025 on). Anything fully-null OUTSIDE this map indicates a
broken column mapping for that year (e.g. a renamed upstream field no
longer matching `COLUMN_RENAME_MAP`/`SCOUT_RENAME_MAP`), not a genuine
historical absence.
"""
