## 2016_jogadores.csv

| coluna    | descrição               | observações                                                     |
|-----------|-------------------------|-----------------------------------------------------------------|
| ID        | id do jogador           |                                                                 |
| Apelido   | nome/apelido do jogador |                                                                 |
| ClubeID   | id do clube do jogador  | ver arquivo 2016_times.csv                                      |
| PosiçãoID | posição do jogador      | 1:Goleiro, 2:Lateral, 3:Zagueiro, 4:Meia, 5:Atacante, 6:Técnico |

## 2016_partidas_ids.csv

| coluna          | descrição                                                    | observações                     |
|-----------------|--------------------------------------------------------------|---------------------------------|
| ID              | id da partida                                                |                                 |
| Rodada          | número da rodada do Brasileirão                              | número da rodada do Brasileirão |
| CasaID          | id do time mandante                                          | ver arquivo 2016_times.csv      |
| VisitanteID     | id do time visitante                                         | ver arquivo 2016_times.csv      |
| PlacarCasa      | placar do time mandante                                      |                                 |
| PlacarVisitante | placar do time visitante                                     |                                 |
| Resultado       | indica o time vencedor (casa ou mandante) ou se houve empate |                                 |

## 2016_partidas.csv

| coluna    | descrição                     | observações          |
|-----------|-------------------------------|----------------------|
| game      | ordem da partida              |                      |
| round     | rodada do brasileirão         |                      |
| date      | data e hora da partida        |                      |
| home_team | time mandante e seu estado    |                      |
| score     | placar da partida             | mandante x visitante |
| away_team | time visitante e seu estado   |                      |
| arena     | nome e localização do estádio |                      |

## 2016_scouts_raw.csv

| coluna        | descrição                                     | observações                    |
|---------------|-----------------------------------------------|--------------------------------|
| Rodada        | número da rodada do Brasileirão               |                                |
| ClubeID       | clube do jogador                              | ver arquivo 2016_times.csv     |
| AtletaID      | id do jogador                                 | ver arquivo 2016_jogadores.csv |
| Participou    | indica se o jogador participou daquela rodada | FALSE:Não, TRUE:Sim            |
| Pontos        | pontuação do jogador                          |                                |
| PontosMedia   | média da pontuação do jogador                 |                                |
| Preco         | preço do jogador                              |                                |
| PrecoVariacao | variação de preço                             |                                |
| FS            | faltas sofridas                               |                                |
| PE            | passes errados                                |                                |
| A             | assistências                                  |                                |
| FT            | finalizações na trave                         |                                |
| FD            | finalizações defendidas                       |                                |
| FF            | finalizações para fora                        |                                |
| G             | gols                                          |                                |
| I             | impedimentos                                  |                                |
| PP            | pênaltis perdidos                             |                                |
| RB            | roubadas de bola                              |                                |
| FC            | faltas cometidas                              |                                |
| GC            | gols contra                                   |                                |
| CA            | cartões amarelo                               |                                |
| CV            | cartões vermelho                              |                                |
| SG            | jogos sem sofrer gols                         |                                |
| DD            | defesas difíceis                              |                                |
| DP            | defesas de pênalti                            |                                |
| GS            | gols sofridos                                 |                                |

## 2016_times.csv

| coluna     | descrição    | observações                      |
|------------|--------------|----------------------------------|
| ID         | id do time   |                                  |
| Nome       | nome do time | camel-case                       |
| Abreviacao | abreviação   | upper-case                       |
| Slug       | nome do time | camel-case, sem espaço e acentos |
