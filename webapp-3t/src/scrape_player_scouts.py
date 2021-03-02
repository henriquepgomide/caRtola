# python3

import re 
import requests
from bs4 import BeautifulSoup
import pandas as pd


def read_cartola_data(year):
    '''
    Read data from a given year of the CaRtola repository and return a pd.DataFrame

    Parameters:
    year (int) - year inside the range 2018-2020.
    ''' 

    if year in [2018, 2019, 2020]:

        # URL para baixar os arquivos
        url = 'https://github.com/henriquepgomide/caRtola/tree/master/data/{}'.format(year)
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
    
        dict_of_files = {}
        for tag in soup.find_all('a', attrs={'href': re.compile('rodada-([0-9]|[0-9][0-9])\.csv')}):
            href_str = tag.get('href')
            file_name = re.sub('/henriquepgomide/caRtola/blob/master/data/{}/'.format(year), 
                            '', 
                            href_str)
            
            file_url = re.sub('/henriquepgomide/caRtola/blob/master/data/{}/'.format(year), 
                            'https://raw.githubusercontent.com/henriquepgomide/caRtola/master/data/{}/'.format(year), 
                            href_str)
            dict_of_files[file_name] = file_url
    
        list_of_dataframes = []
        for key, item in dict_of_files.items():
            df = pd.read_csv(item)
            df['rodada'] = key
            list_of_dataframes.append(df)
    
        df_cartola = pd.concat(list_of_dataframes)
    
        return df_cartola
    
    else:
        print('You need to add an year within the range: 2018 and 2020')


def main():
    df = read_cartola_data(2020)
    return print(df) 


if __name__ == "__main__":
    main()

