"""Tests for the scouts module: rename, disaccumulate, fill, process."""

import numpy as np
import pandas as pd

from cartola.aggregation import scouts


def test_harmonize_scout_names_renames_legacy():
    df = pd.DataFrame({"PE": [1.0], "RB": [2.0], "DD": [3.0], "G": [4.0]})
    out = scouts.harmonize_scout_names(df)
    assert set(out.columns) == {"PI", "DS", "DE", "G"}


def test_harmonize_scout_names_preserves_modern_columns():
    df = pd.DataFrame({"PI": [1.0], "G": [2.0]})
    out = scouts.harmonize_scout_names(df)
    assert list(out.columns) == ["PI", "G"]


def test_disaccumulate_basic_two_rounds():
    df = pd.DataFrame(
        {
            "id_atleta": [1, 1],
            "rodada": [1, 2],
            "G": [1.0, 3.0],  # cumulative: 1 then 3 → per-round 1, 2
            "SG": [0.0, 1.0],
        }
    )
    out = scouts.disaccumulate_scouts(df, scout_cols=["G", "SG"])
    assert out["G"].tolist() == [1.0, 2.0]
    assert out["SG"].tolist() == [0.0, 1.0]


def test_disaccumulate_skipped_round_is_zero():
    df = pd.DataFrame(
        {
            "id_atleta": [1, 1, 1],
            "rodada": [1, 2, 3],
            "G": [1.0, 1.0, 2.0],  # round 2 absent → diff=0; round 3 → 1
        }
    )
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].tolist() == [1.0, 0.0, 1.0]


def test_disaccumulate_first_appearance_mid_season_keeps_cumulative():
    df = pd.DataFrame(
        {
            "id_atleta": [1],
            "rodada": [5],
            "G": [3.0],
        }
    )
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].iloc[0] == 3.0


def test_disaccumulate_correction_drops_to_zero_no_negative():
    """Cartola lowers a cumulative scout retroactively → the current
    round's per-round value is 0 (not negative). A player cannot perform
    a negative number of actions; the correction is attributed to a past
    round we cannot identify forward-only."""
    df = pd.DataFrame(
        {
            "id_atleta": [1, 1, 1],
            "rodada": [1, 2, 3],
            "G": [2.0, 1.0, 1.0],
        }
    )
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].tolist() == [2.0, 0.0, 0.0]


def test_disaccumulate_resumes_against_running_max_after_correction():
    """Regression for the running-max baseline: when cumulative dips and
    later climbs back above the previous high, the new positive delta is
    computed against the high-water mark, not the corrected lower value
    (a naive ``.diff()`` would double-count events here)."""
    df = pd.DataFrame(
        {
            "id_atleta": [1, 1, 1, 1],
            "rodada": [1, 2, 3, 4],
            "G": [1.0, 2.0, 1.0, 3.0],  # cum dips at r3, recovers + 1 at r4
        }
    )
    out = scouts.disaccumulate_scouts(df, scout_cols=["G"])
    assert out["G"].tolist() == [1.0, 1.0, 0.0, 1.0]


def test_process_legacy_year_renames_and_fills_zero():
    df = pd.DataFrame(
        {
            "id_atleta": [1],
            "rodada": [1],
            "PE": [np.nan],
            "RB": [3.0],
            "G": [1.0],
        }
    )
    out = scouts.process(df, accumulated=False)
    assert out["PI"].iloc[0] == 0.0
    assert out["DS"].iloc[0] == 3.0
    assert out["G"].iloc[0] == 1.0


def test_process_accumulated_year_disaccumulates():
    df = pd.DataFrame(
        {
            "id_atleta": [1, 1],
            "rodada": [1, 2],
            "G": [1.0, 4.0],
        }
    )
    out = scouts.process(df, accumulated=True)
    assert out["G"].tolist() == [1.0, 3.0]


def test_process_returns_early_when_no_scout_columns_present():
    """A year whose raw files ship zero scout columns → short-circuit
    before fillna/disaccumulate; the caller's final reindex against
    ``CANONICAL_COLUMNS`` is what turns the absent columns into NaN."""
    df = pd.DataFrame({"id_atleta": [1, 2], "rodada": [1, 1]})
    out = scouts.process(df, accumulated=True)
    assert list(out.columns) == ["id_atleta", "rodada"]
    assert len(out) == 2
