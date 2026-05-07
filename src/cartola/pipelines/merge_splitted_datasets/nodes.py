"""
This is a boilerplate pipeline 'merge_splitted_datasets'
generated using Kedro 0.18.2
"""
import pandas as pd


def merge_datasets(df_scouts: pd.DataFrame, df_players: pd.DataFrame, df_teams: pd.DataFrame) -> pd.DataFrame:
    df_players = df_players.drop(columns="ClubeID")
    df_teams = df_teams.drop(columns="Abreviacao")
    return {
        "concat": (
            df_scouts.merge(df_players, how="left", left_on="AtletaID", right_on="ID")
            .merge(df_teams, how="left", left_on="ClubeID", right_on="ID")
            .drop(columns=["ID_x", "ID_y", "Slug"])
        )
    }
