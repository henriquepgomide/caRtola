## 2014_jogadores.csv

| coluna    | descrição               | observações                                                     |
|-----------|-------------------------|-----------------------------------------------------------------|
| ID        | id do jogador           |                                                                 |
| Apelido   | nome/apelido do jogador |                                                                 |
| ClubeID   | id do clube do jogador  | ver arquivo 2014_times.csv                                      |
| PosiçãoID | posição do jogador      | 1:Goleiro, 2:Lateral, 3:Zagueiro, 4:Meia, 5:Atacante, 6:Técnico |

## 2014_lances.csv

| coluna    | descrição                            | observações                                                                                  |
|-----------|--------------------------------------|----------------------------------------------------------------------------------------------|
| ID        | id do lance                          |                                                                                              |
| PartidaID | id da partida                        | ver arquivo 2014_partidas_ids.csv                                                            |
| ClubeID   | id do clube                          | ver arquivo 2014_times.csv                                                                   |
| AtletaID  | id do jogador                        | ver arquivo 2014_jogadores.csv                                                               |
| Periodo   | indica o período do lance            | 1tr: 1º tempo, 2tr: 2º tempo, itr: intervalo, fnj: final do jogo (após o término da partida) |
| Momento   | tempo em minutos que o lance ocorreu | nulo quando período = 'itr' ou 'fnj'                                                         |
| Tipo      | tipo de scout                        |                                                                                              |

## 2014_partidas_ids.csv

| coluna          | descrição                                                    | observações                     |
|-----------------|--------------------------------------------------------------|---------------------------------|
| ID              | id da partida                                                |                                 |
| Rodada          | número da rodada do Brasileirão                              | número da rodada do Brasileirão |
| Casa            | id do time mandante                                          | ver arquivo 2014_times.csv      |
| Visitante       | id do time visitante                                         | ver arquivo 2014_times.csv      |
| PlacarCasa      | placar do time mandante                                      |                                 |
| PlacarVisitante | placar do time visitante                                     |                                 |
| Resultado       | indica o time vencedor (casa ou mandante) ou se houve empate |                                 |

## 2014_partidas.csv

| coluna    | descrição                     | observações          |
|-----------|-------------------------------|----------------------|
| game      | ordem da partida              |                      |
| round     | rodada do brasileirão         |                      |
| date      | data e hora da partida        |                      |
| home_team | time mandante e seu estado    |                      |
| score     | placar da partida             | mandante x visitante |
| away_team | time visitante e seu estado   |                      |
| arena     | nome e localização do estádio |                      |

## 2014_scouts_raw.csv

| coluna        | descrição                                                 | observações                                                     |
|---------------|-----------------------------------------------------------|-----------------------------------------------------------------|
| Atleta        | id do jogador                                             | ver arquivo 2014_jogadores.csv                                  |
| Rodada        | número da rodada do Brasileirão                           |                                                                 |
| Clube         | clube do jogador                                          | ver arquivo 2014_times.csv                                                                 |
| Participou    | indica se o jogador participou ou não                     | 1:Sim, 0:Não                                                    |
| Posição       | posição do jogador                                        | 1:Goleiro, 2:Lateral, 3:Zagueiro, 4:Meia, 5:Atacante, 6:Técnico |
| Jogos         | quantidade de jogos que o jogador participou até aquela rodada             |                                                                 |
| Pontos        | pontuação do jogador                                      |                                                                 |
| PontosMedia   | média da pontuação do jogador                             |                                                                 |
| Preco         | preço do jogador                                          |                                                                 |
| PrecoVariacao | variação de preço                                         |                                                                 |
| Partida       | id da partida                                             | ver arquivo 2014_partidas_ids.csv                               |
| Mando         | indica se o jogador era do time com mando de campo ou não | 1:Sim, 0:Não                                                    |
| Titular       | indica se o jogador foi titular ou não                    | 1:Sim, 0:Não                                                    |
| Substituido   | indica se o jogador foi substituído ou não                | 1:Sim, 0:Não                                                    |
| TempoJogado   | indica a fração de tempo (90 minutos) jogado pelo jogador | [0-1]                                                           |
| Nota          | indica a nota do jogador pela crítica especializada       |                                                                 |
| FS            | faltas sofridas                                           |                                                                 |
| PE            | passes errados                                            |                                                                 |
| A             | assistências                                              |                                                                 |
| FT            | finalizações na trave                                     |                                                                 |
| FD            | finalizações defendidas                                   |                                                                 |
| FF            | finalizações para fora                                    |                                                                 |
| G             | gols                                                      |                                                                 |
| I             | impedimentos                                              |                                                                 |
| PP            | pênaltis perdidos                                         |                                                                 |
| RB            | roubadas de bola                                          |                                                                 |
| FC            | faltas cometidas                                          |                                                                 |
| GC            | gols contra                                               |                                                                 |
| CA            | cartões amarelo                                           |                                                                 |
| CV            | cartões vermelho                                          |                                                                 |
| SG            | jogos sem sofrer gols                                     |                                                                 |
| DD            | defesas difíceis                                          |                                                                 |
| DP            | defesas de pênalti                                        |                                                                 |
| GS            | gols sofridos                                             |                                                                 |

## 2014_times.csv

| coluna     | descrição    | observações                      |
|------------|--------------|----------------------------------|
| ID         | id do time   | ver arquivo 2014_times.csv       |
| Nome       | nome do time |                                  |
| Abreviacao | abreviação   |                                  |
| Slug       | nome do time | lower-case, sem espaço e acentos |
