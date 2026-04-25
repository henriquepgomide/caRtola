from typing import List

import pandas as pd


def get_disaccumulated_scouts_for_round(
    df: pd.DataFrame,
    round_: int,
    cols_scouts: List[str],
):
    df_round = df[df.rodada == round_]
    if round_ == 1:
        return df_round

    suffixes = ("_curr", "_prev")
    cols_current = [col + suffixes[0] for col in cols_scouts]
    cols_prev = [col + suffixes[1] for col in cols_scouts]

    df_round_prev = df[df.rodada < round_].groupby("id_atleta")[cols_scouts].max()
    df_players = df_round.merge(df_round_prev, how="left", on="id_atleta", suffixes=suffixes)

    # If this is the player's first round, the prev-scout columns are NaN. Fill
    # only the scout columns with 0 (filling everything would clobber strings).
    fill_cols = cols_current + cols_prev
    df_players[fill_cols] = df_players[fill_cols].fillna(0)

    df_players[cols_current] = df_players[cols_current].values - df_players[cols_prev].values

    df_players.drop(labels=cols_prev, axis=1, inplace=True)
    df_players = df_players.rename(columns=dict(zip(cols_current, cols_scouts)))
    # All scouts are by definition non-decreasing across rounds (you can't
    # un-score a goal), but Cartola's source data carries noise (corrections,
    # mid-season resets, duplicate rows with bad totals) that can produce
    # negative deltas. Per the spec, scouts must be >= 0 when present, so we
    # clip all negative deltas to zero.
    df_players[cols_scouts] = df_players[cols_scouts].clip(lower=0)

    return df_players


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
    cols_present = [c for c in cols_scouts if c in df.columns]
    if not cols_present:
        return df

    rounds = sorted(df["rodada"].dropna().unique().astype(int).tolist())
    df_result = pd.concat(
        [get_disaccumulated_scouts_for_round(df, int(r), cols_present) for r in rounds],
        ignore_index=True,
    )
    # SG (Saldo de Gols / clean sheet) is binary per round: a player either
    # kept a clean sheet that round or didn't. A delta > 1 here indicates
    # the player missed rounds and the cumulative jumped by N; for per-round
    # semantics we cap at 1.
    if "SG" in df_result.columns:
        df_result["SG"] = df_result["SG"].clip(upper=1)
    return df_result
