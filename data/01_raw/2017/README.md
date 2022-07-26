## 2017_jogadores.csv

| coluna    | descrição               | observações                                                     |
|-----------|-------------------------|-----------------------------------------------------------------|
| ID        | id do jogador           |                                                                 |
| Apelido   | nome/apelido do jogador |                                                                 |
| ClubeID   | id do clube do jogador  | ver arquivo 2017_times.csv                                      |
| PosiçãoID | posição do jogador      | 1:Goleiro, 2:Lateral, 3:Zagueiro, 4:Meia, 5:Atacante, 6:Técnico |

## 2017_partidas.csv

| coluna    | descrição                     | observações          |
|-----------|-------------------------------|----------------------|
| game      | ordem da partida              |                      |
| round     | rodada do brasileirão         |                      |
| date      | data e hora da partida        |                      |
| home_team | time mandante e seu estado    |                      |
| score     | placar da partida             | mandante x visitante |
| away_team | time visitante e seu estado   |                      |
| arena     | nome e localização do estádio |                      |

## 2017_scouts_raw.csv

| coluna                     | descrição                                        | observações                                                                 |
|----------------------------|--------------------------------------------------|-----------------------------------------------------------------------------|
| atletas.nome               | nome completo do jogador                         |                                                                             |
| atletas.atleta_id          | id do jogador                                    | ver arquivo 2017_jogadores.csv                                              |
| atletas.apelido            | nome/apelido do jogador                          |                                                                             |
| atletas.foto               | url para foto do jogador                         |                                                                             |
| atletas.rodada_id          | número da rodada do Brasileirão                  |                                                                             |
| atletas.clube_id           | abreviação do clube do jogador                   |                                                                             |
| atletas.posicao_id         | posição do jogador                               | gol:goleiro, zag:zagueiro, lat:lateral, mei:meia, ata:atacante, tec:técnico |
| atletas.clube.id.full_name | clube do jogador                                 |                                                                             |
| atletas.status_id          | status do jogador na rodada                      |                                                                             |
| atletas.pontos_num         | pontuação dos scouts                             |                                                                             |
| atletas.preco_num          | preço do jogador                                 |                                                                             |
| atletas.variacao_num       | variação do preço do jogador                     |                                                                             |
| atletas.media_num          | média do jogador                                 |                                                                             |
| atletas.jogos_num          | quantidade de jogos disputados até aquela rodada |                                                                             |
| atletas.atletas.scout      | quantidade de scouts que o jogador obteve        |                                                                             |
| PE                         | passes errados                                   |                                                                             |
| SG                         | jogos sem sofrer gols                            |                                                                             |
| FC                         | faltas cometidas                                 |                                                                             |
| FS                         | faltas sofridas                                  |                                                                             |
| I                          | impedimentos                                     |                                                                             |
| RB                         | roubadas de bola                                 |                                                                             |
| FD                         | finalizações defendidas                          |                                                                             |
| A                          | assistências                                     |                                                                             |
| G                          | gols                                             |                                                                             |
| FF                         | finalizações para fora                           |                                                                             |
| DD                         | defesas difícies                                 |                                                                             |
| CA                         | cartões amarelo                                  |                                                                             |
| GS                         | gols sofridos                                    |                                                                             |
| FT                         | finalizações na trave                            |                                                                             |
| CV                         | cartões vermelho                                 |                                                                             |
| PP                         | pênaltis perdidos                                |                                                                             |
| DP                         | defesas de pênalti                               |                                                                             |

## 2017_tabela.csv

| coluna | descrição                     | observações  |
|--------|-------------------------------|--------------|
| Pos    | posição do time no campeonato |              |
| Clube  | nome do time - estado         |              |
| P      | pontos ganhos                 |              |
| J      | jogos                         |              |
| V      | vitórias                      |              |
| E      | empates                       |              |
| D      | derrotas                      |              |
| GP     | gols pro                      |              |
| GC     | gols sofridos                 |              |
| SG     | saldo de gols                 | SG = GP - GC |
| VM     | vitórias como mandante        |              |
| VV     | vitórias como visitante       |              |
| DM     | derrotas como mandante        |              |
| DV     | derrotas como visitante       |              |
| CA     | cartões amarelos              |              |
| CV     | cartões vermelhos             |              |
| %      | aproveitamento                |              |

## 2017_times.csv

| coluna     | descrição    | observações |
|------------|--------------|-------------|
| ID         | id do time   |             |
| Nome       | nome do time | camel-case  |
| Abreviacao | abreviação   | upper-case  |
| Slug       | nome do time | camel-case  |
