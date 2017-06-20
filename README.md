[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/caRtola-R/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link) | README in [English](https://github.com/henriquepgomide/caRtola/blob/master/README.en.md)

*Novidade* - Acesse o protótipo da dashboard (caRtola - STATS)[https://henriquepgomide.shinyapps.io/cartola-stats/]. 

# Introdução

Este repositório tem como objetivo oferecer para usuários do R e do Cartola FC uma forma fácil de recuperar e analisar os dados oferecidos da API.

* Para executar os scripts contidos, você precisará instalar o [R](https://www.r-project.org/) e eu fortemente recomendo a instalação da [IDE RStudio](https://www.rstudio.com/products/rstudio/download/). 
* Para acessar os dados, use qualquer programa. Está tudo disponível em arquivos separados por vírgulas. Até o Excel abre :)

# O que está feito?

## Dashboard

* Aplicativo shiny para escolher seu jogador. Protótipo disponível no link (caRtola - STATS)[https://henriquepgomide.shinyapps.io/cartola-stats/]


## Dados

1. Importação dos dados da API do cartola através do script - *lib/caRtola_fetch.R*
2. Os dados de três edições anteriores e das rodadas deste ano estão disponíveis na pasta *db* em formato 'CSV'. Os dados dos anos 2014 e 2015 foram retirados do repositório - (https://github.com/thevtm/CartolaFCDados). Os dados de 2016 estão _incompletos_ e cobrem até a 19 rodada.
3. Importação dos dados de classificação do campeonato brasileiro ano de 2016 e 2017 através do script *lib/team_data_scraper.R*.

## Análise
1. Análise exploratória dos dados de 2015, arquivo *lib/model2015_data.R*
2. Análise exploratória dos dados de 2016, arquivo *select_16_players.R*

# O que ainda está por ser feito?

1. Analisar dados e criar modelos para predizer pontuação de jogadores

# Contato

* henriquepgomide@gmail.com
* [@hpgomide](https://twitter.com/hpgomide) - Siga meu twitter para atualizações.
