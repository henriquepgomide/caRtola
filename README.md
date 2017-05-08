[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/caRtola-R/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link)


# Introdução

Este repositório tem como objetivo oferecer para usuários do R e do Cartola FC uma forma fácil de recuperar e analisar os dados oferecidos da API.

# O que está feito?

## Dados

1. Importação dos dados da API do cartola através do script - *lib/caRtola_fetch.R*
2. Os dados de duas edições anteriores e das rodadas deste ano estão disponíveis na pasta *db*. Os dados dos anos anteriores foram retirados do repositório - (https://github.com/thevtm/CartolaFCDados).
3. Importação dos dados de classificação do campeonato brasileiro ano de 2016 através do script *lib/team_data_scraper.R*.

## Análises
1. Análise exploratória dos dados de 2015, arquivo *lib/model2015_data.R*
2. Análise explatório dos dados de 2016, aqruivo *select_16_players.R*

# O que ainda está por ser feito?

1. Analisar dados e criar modelos para predizer pontuação de jogadores
2. Criar um aplicativo shiny para criar visualizações uteis para jogadores do Cartola.

# Contato

henriquepgomide@gmail.com


# Introduction - ENGLISH

This repository aims to provide to R users an easy method to gather data from Cartola FC 2016.

# What has been done?

1. Now you can easily import data from players using lib/caRtola_fetch.R
2. Data from current and previous Cartola edition is organized in *db* folder. Data from previous season come from here(https://github.com/thevtm/CartolaFCDados).

# TODO

1. Analyze data from previous years '14 and '15
2. Create useful visualizations using shiny
3. Create models to predict player performance

# Contact

henriquepgomide@gmail.com


# Additional information
## List of API urls

1. "https://api.cartolafc.globo.com/partidas"
2. "https://api.cartolafc.globo.com/clubes"
3. "https://api.cartolafc.globo.com/mercado/destaques"
4. "https://api.cartolafc.globo.com/mercado/status"
5. "https://api.cartolafc.globo.com/atletas/mercado"
6. "https://api.cartolafc.globo.com/rodadas"
7. "https://api.cartolafc.globo.com/auth/time"


