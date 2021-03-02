#python3

import pandas as pd
from scrape_player_scouts import read_cartola_data



# Read player scouts
df = read_cartola_data(2020)


# Read fixtures
matches = pd.read_csv('https://raw.githubusercontent.com/henriquepgomide/caRtola/master/data/2020/2020_partidas.csv')
