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

    # if is the first round of a player, the scouts of previous rounds will be NaNs. Thus, set them to zero
    df_players.fillna(value=0, inplace=True)

    # compute the scouts
    df_players[cols_current] = df_players[cols_current].values - df_players[cols_prev].values

    # update the columns
    df_players.drop(labels=cols_prev, axis=1, inplace=True)
    df_players = df_players.rename(columns=dict(zip(cols_current, cols_scouts)))
    df_players.SG = df_players.SG.clip(lower=0)

    return df_players
