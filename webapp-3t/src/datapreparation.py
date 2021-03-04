#python3

import pandas as pd
from scrape_player_scouts import read_cartola_data


def preprocess_matches(path_to_match_file):
    """
    Preprocess matches files from a given file with Brasileirao info. 
    Returns a pd.DataFrame
    Parameters:
    path_to_match_files(str): csv file with match results with columns:
    date, home_team, away_team, home_score, away_score, round
    """
    matches = pd.read_csv(path_to_match_file)
    matches = matches[['home_team', 'away_team', 'round']]
    matches = matches.melt(id_vars='round', value_name='atletas.clube_id')
    matches = matches.rename(columns={'round': 'atletas.rodada_id', 
        'variable': 'home_away'})
    return matches


def compute_mean_home_away(player_id):
    """
    Compute mean and home scores averages for a given player:

    Keywords arguments: 
    player_id (id) -- player_id from cartola API (e.g., '90285')
    """

    def compute_mean(player, home_away):
        '''
        Compute home or away mean.

        Keyword arguments:
        player (pd.Dataframe) -- a DataFrame for a specific player
        home_away (str) -- a column in a dataframe to estimate mean.

        Example:

        home_mean = compute_mean(player_df, 'home_team')
        '''
        player = player[player['home_away'] == home_away]\
        .sort_values('atletas.rodada_id')
    
        player['status'] = player['atletas.status_id'].shift(1)
        
        player = player[(player['atletas.variacao_num'] != 0) & 
                                    (~player['status'].isin(['Nulo', 'Suspenso'])) &
                                    (player['atletas.pontos_num'] != 0)]
        
        player['media_movel'] = player['atletas.pontos_num'].expanding().mean()
        player['media_movel'] = player['media_movel'].shift(1)
        return player
    
    player = df[df['atletas.atleta_id'] == player_id]

    home_mean = compute_mean(player, 'home_team')
    away_mean = compute_mean(player, 'away_team')

    player = pd.concat([home_mean, away_mean])
    player = player.sort_values('atletas.rodada_id')

    return player


def create_n_matches_played(df):
    """
    Create atribute total number of matches played
    Parameters: 
    df(pd.DataFrame): dataFrame must contains the following
                      atletas.atleta_id, atletas.status_id
    """
    n_games = df.groupby(['atletas.atleta_id', 'atletas.status_id'])['atletas.status_id'].count()
    n_games = n_games.xs('Provável', level='atletas.status_id')
    data = df.join(pd.Series(n_games, name='n_games'), how='left', on='atletas.atleta_id')
    return data


def create_rolling_avg(player_df, scouts_columns):
    """
    Compute rolling averages for a given player:
        Parameters:
        player_df (Data.Frame): A dataframe with players
        scouts_columns (list): a list of columns
    """

    try:
        player_df = player_df.sort_values('atletas.rodada_id')

        for column in scouts_columns:
            player_df[column] = player_df[column].fillna(0)
            player_df[column + '_lag'] = player_df[column].shift(1).fillna(0)
            player_df[column + '_lag'] = player_df[column] - player_df[column + '_lag']
            player_df[column + '_avg'] = player_df[column + '_lag'].expanding().mean()

        return player_df

    except:
        print("Something went wrong when creating rolling mean scouts")



if __name__ == '__main__':
    df = read_cartola_data(2020)
    matches = preprocess_matches('https://raw.githubusercontent.com/henriquepgomide/caRtola/master/data/2020/2020_partidas.csv')
    df = df.merge(matches, how='left', 
                            on=['atletas.rodada_id', 'atletas.clube_id'])
    df = create_n_matches_played(df)

    list_of_players = df['atletas.atleta_id'].unique().tolist()
    list_of_players_df = []
    for player in list_of_players:
        player_df = compute_mean_home_away(player)
        list_of_players_df.append(player_df)
    home_away_avgs = pd.concat(list_of_players_df)

    scouts_columns = ['FF', 'FS', 'G', 'PI', 
            'CA', 'FC', 'DS', 'FT', 
            'DD', 'GS', 'FD', 
            'SG', 'A', 'I']

    list_of_players_df = []
    for player in list_of_players:
        player_df = df[df['atletas.atleta_id'] == player]
        player_df = create_rolling_avg(player_df, scouts_columns)
        list_of_players_df.append(player_df)

    df = pd.concat(list_of_players_df)
    df.to_json('../data/cartola_2020_scouts.json')

