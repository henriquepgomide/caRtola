Essa pasta contém os dados de todo o histórico do Cartola organizados por ano. __Cada pasta contém os dados sobre jogadores, partidas, times, scouts e uma descrição dos dados em cada arquivo__. Na raiz dessa pasta, você vai encontrar os seguintes arquivos:

### :star: dados_agregados.csv :star:

__Esse é o principal arquivo desse repositório__. Ele tem todos os dados, de todos os anos, de todas as rodadas, e de todos os jogadores (ufa!). Cada linha representa os scouts de um jogador para uma rodada de um certo ano. Esses dados estão em formato bruto, ou seja, precisam ser limpos antes de serem utilizados. __Há erros de inconsistência, presença de NANs, entre outras coisas, que já vêm da API do _Cartola FC___.

Porém, não se preocupe! Já fizemos o trabalho sujo para você! :muscle: Temos um arquivo com os dados bem limpinhos só esperando suas análises. Lê aqui embaixo :point_down: e não esquece de ler as observações desse README também.

### dados_agregados_limpos.csv

Contém os dados agregados de forma limpa, isto é, dados prontos para você utilizar em suas análises. __Nesse arquivo, nós garantimos que NÃO há erros de inconsistência nem dados sujos__! ~~A menos que você encontre. Nesse caso, avise a gente, tá?~~ :wink:

Quer saber como essa limpeza foi feita? [Dá uma olhada aqui](../src/python/Análise%20dos%20Dados.ipynb).

### dados_agregados_amostras.csv

Contém as amostras utilizadas para o treinamento do modelo preditor de scores. __Essas amostras já estão prontas para serem utilizadas para o treinamento de qualquer modelo de *Machine Learning* sem nenhum esforço adicional__.

### times_ids.csv

Contém os nomes e os _ids_ de todos os times que já jogaram o brasileirão desde 2014. Você pode obter os dados do time que participaram do brasileirão em um determinado ano na sua pasta correspondente no arquivo [ANO]\_times. __Repare que em 2017, os ids de alguns times foram alterados__. Mas não se preocupe, esse arquivo diz tudo para você.

## Observações:

- __Todos os arquivos [ANO]\_scouts\_raw.csv dentro de cada pasta são arquivos brutos__, que vêm diretamente da API do _Cartola FC_.
- __Os scouts de 2015 são cumulativos__, ou seja, os scouts dos jogadores vão sendo somados a cada rodada. Entretanto, a pontuação não é. Isso também causa o repetimento de dados. O arquivo *dados_agregados_limpos.csv* nessa pasta já corrige esse problema para você.

## Créditos:

* Os dados de 2014 e 2015 foram obtidos do repositório [CartolaFCDados](https://github.com/thevtm/CartolaFCDados)
* Os dados de 2016 foram disponibilizados por [Arnaldo Gualberto](https://github.com/arnaldog12).
* Os dados dos times são extraídos do [site da CBF](https://www.cbf.com.br/competicoes/brasileiro-serie-a#.WiqMZbbOpTY).

## Descrição dos arquivos dessa pasta

### dados_agregados.csv & dados_agregados_limpos.csv

| coluna          | descrição                                                 | observações                                                                                        |
|-----------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Rodada          | número da rodada do Brasileirão                           |                                                                                                    |
| ClubeID         | clube do jogador                                          | ver arquivo times_ids.csv                                                                          |
| AtletaID        | id do jogador                                             |                                                                                                    |
| Participou      | indica se o jogador participou daquela rodada             | FALSE:Não, TRUE:Sim                                                                                |
| Posicao         | posição do jogador                                        | gol:goleiro, zag:zagueiro, lat:lateral, mei:meia, ata:atacante, tec:técnico                        |
| Jogos           | qtde. de jogos que o jogador participou até aquela rodada |                                                                                                    |
| Pontos          | pontuação do jogador                                      |                                                                                                    |
| PontosMedia     | média da pontuação do jogador                             |                                                                                                    |
| Preco           | preço do jogador                                          |                                                                                                    |
| PrecoVariacao   | variação de preço                                         |                                                                                                    |
| FS              | faltas sofridas                                           |                                                                                                    |
| PE              | passes errados                                            |                                                                                                    |
| A               | assistências                                              |                                                                                                    |
| FT              | finalizações na trave                                     |                                                                                                    |
| FD              | finalizações defendidas                                   |                                                                                                    |
| FF              | finalizações para fora                                    |                                                                                                    |
| G               | gols                                                      |                                                                                                    |
| I               | impedimentos                                              |                                                                                                    |
| PP              | pênaltis perdidos                                         |                                                                                                    |
| RB              | roubadas de bola                                          |                                                                                                    |
| FC              | faltas cometidas                                          |                                                                                                    |
| GC              | gols contra                                               |                                                                                                    |
| CA              | cartões amarelo                                           |                                                                                                    |
| CV              | cartões vermelho                                          |                                                                                                    |
| SG              | jogos sem sofrer gols                                     |                                                                                                    |
| DD              | defesas difíceis                                          |                                                                                                    |
| DP              | defesas de pênalti                                        |                                                                                                    |
| GS              | gols sofridos                                             |                                                                                                    |
| ano             | ano dos dados                                             |                                                                                                    |
| Apelido         | nome/apelido do jogador                                   |                                                                                                    |
| Status          | status do jogador                                         | Provável, Dúvida, Suspenso, Nulo, ...                                                              |
| avg.Points      | média de pontos do jogador                                |                                                                                                    |
| avg.last05      | média de pontos do jogador nas últimas 5 rodadas          |                                                                                                    |
| avg.FS          | média de faltas sofridas                                  |                                                                                                    |
| avg.FS.l05      | média de faltas sofridas nas últimas 5 rodadas            |                                                                                                    |
| avg.PE          | média de passes errados                                   |                                                                                                    |
| avg.PE.l05      | média de passes errados nas últimas 5 rodadas             |                                                                                                    |
| avg.A           | média de assistências                                     |                                                                                                    |
| avg.A.l05       | média de assistências nas últimas 5 rodadas               |                                                                                                    |
| avg.FT          | média de finalizações na trave                            |                                                                                                    |
| avg.FT.l05      | média de finalizações na trave nas últimas 5 rodadas      |                                                                                                    |
| avg.FD          | média de finalizações defendidas                          |                                                                                                    |
| avg.FD.l05      | média de finalizações defendidas nas últimas 5 rodadas    |                                                                                                    |
| avg.FF          | média de finalizações para fora                           |                                                                                                    |
| avg.FF.l05      | média de finalizações para fora nas últimas 5 rodadas     |                                                                                                    |
| avg.G           | média de gols                                             |                                                                                                    |
| avg.G.l05       | média de gols nas últimas 5 rodadas                       |                                                                                                    |
| avg.I           | média de impedimentos                                     |                                                                                                    |
| avg.I.l05       | média de impedimentos nas últimas 5 rodadas               |                                                                                                    |
| avg.PP          | média de pênaltis perdidos                                |                                                                                                    |
| avg.PP.l05      | média de pênaltis perdidos nas últimas 5 rodadas          |                                                                                                    |
| avg.RB          | média de roubadas de bola                                 |                                                                                                    |
| avg.RB.l05      | média de roubadas de bola nas últimas 5 rodadas           |                                                                                                    |
| avg.FC          | média de faltas cometidas                                 |                                                                                                    |
| avg.FC.l05      | média de faltas cometidas nas últimas 5 rodadas           |                                                                                                    |
| avg.GC          | média de gols contra                                      |                                                                                                    |
| avg.GC.l05      | média de gols contra nas últimas 5 rodadas                |                                                                                                    |
| avg.CA          | média de cartões amarelos                                 |                                                                                                    |
| avg.CV          | média de cartões vermelhos nas últimas 5 rodadas          |                                                                                                    |
| avg.SG          | média de jogos sem sofrer gols                            |                                                                                                    |
| avg.SG.l05      | média de jogos sem sofrer gols nas últimas 5 rodadas      |                                                                                                    |
| avg.DD          | média de defesas difíceis                                 |                                                                                                    |
| avg.DD.l05      | média de defesas difíceis nas últimas 5 rodadas           |                                                                                                    |
| avg.DP          | média de defesas de pênalti                               |                                                                                                    |
| avg.DP.l05      | média de defesas de pênalti nas últimas 5 rodadas         |                                                                                                    |
| avg.GS          | média de gols sofridos                                    |                                                                                                    |
| avg.GS.l05      | média de gols sofridos nas últimas 5 rodadas              |                                                                                                    |
| risk_points     | desvio-padrão da pontuação do jogador                     |                                                                                                    |
| mes             | mês que a partida ocorreu                                 |                                                                                                    |
| dia             | dia que a partida ocorreu                                 |                                                                                                    |
| away.score.x    | placar to time visitante                                  |                                                                                                    |
| home.score.x    | placar do time da casa                                    |                                                                                                    |
| home.attack     | estimativa de força de ataque do time do jogador          | estimada a partir de uma regressão de Poisson com base no histórico de confrontos entre os times   |
| home.defend     | estimativa de força de defesa do time do jogador          | estimada a partir de uma regressão de Poisson com base no histórico de confrontos entre os times   |
| pred.home.score | estimativa de gols para o time da casa                    | estimada a partir de 10000 simulações  de confronto entre os times usando distribuições de Poisson |
| pred.away.score | estimativa de gols para o time visitante                  | estimada a partir de 10000 simulações,de confronto entre os times usando distribuições de Poisson  |
| variable        | indica se o jogador é do time da casa ou visitante        | home.team: casa, away.team: visitante                                                              |

### dados_agregados_amostras.csv

Contém as mesmas colunas que os arquivos *dados_agregados.csv* e *dados_agregados_limpos.csv*, exceto **Apelido, Status, Participou, dia e mes** - uma vez que esses dados não são necessários para o treinamento do modelo.

### times_ids.csv

| coluna        | descrição                                     | observações                                            |
|---------------|-----------------------------------------------|--------------------------------------------------------|
| nome.cbf      | nome do time no site da CBF                   | camel-case, com espaços, com acentos e com abreviações |
| nome.cartola  | nome do time no Cartola FC                    | camel-case, sem espaços, com acentos e com abreviações |
| nome.completo | nome do time completo                         | camel-case, com espaços, sem acentos e sem abreviações |
| cod.older     | código do time no Cartola FC até 2017         |                                                        |
| cod.2017      | código do time no Cartola FC a partir de 2017 | ler esse README                                        |
| id            | id do time                                    | id = cod.2017                                          |
