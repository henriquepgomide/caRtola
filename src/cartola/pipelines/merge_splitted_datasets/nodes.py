"""
This is a boilerplate pipeline 'merge_splitted_datasets'
generated using Kedro 0.18.2
"""


def merge_datasets(df_scouts, df_players, df_teams, map_col_names):
    df_players = df_players.drop(columns="ClubeID")
    df_teams = df_teams.drop(columns="Abreviacao")
    return (
        df_scouts.merge(df_players, how="left", left_on="AtletaID", right_on="ID")
        .merge(df_teams, how="left", left_on="ClubeID", right_on="ID")
        .drop(columns=["ID_x", "ID_y", "Slug"])
        .rename(columns=map_col_names)
    )
