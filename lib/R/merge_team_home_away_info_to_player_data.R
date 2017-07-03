# What? ----------------------------------------------
# This script proccesses data from CBF matches and
# add home and away information into cartola db
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Este script coleta as informaçoes de jogos em casa e
# fora de casa e insere no banco de dados do cartola
# ----------------------------------------------------

# Load libraries
# Carregar pacotes
library(tidyr)
library(dplyr)
library(plyr)

# Carregar banco de dados
teamCodes <- read.csv("db/teamids-consolidated.csv")
matches <- read.csv("db/2017/matches-brasileirao-2017.csv", stringsAsFactors = FALSE)
cartola <- read.csv("db/2017/cartola_2017.csv", stringsAsFactors = FALSE)

# Padronizar nomes dos times
matches$home_team <- mapvalues(matches$home_team, from = as.vector(teamCodes$nome.cbf), to = as.vector(teamCodes$nome.cartola))
matches$away_team <- mapvalues(matches$away_team, from = as.vector(teamCodes$nome.cbf), to = as.vector(teamCodes$nome.cartola))

# Separar resultado string em númerico
matches <- separate(matches, score, c("home_score","vs","away_score"), convert = TRUE)
matches$home_score <- as.integer(matches$home_score)


# Retirar variáveis inúteis
matches <- matches[,-c(1,7,11)]

# Criar diferencial de gols
matches$goals_dif <-  matches$home_score - matches$away_score

# Subset dados dos times até a última rodada do cartola
matches <- subset(matches, matches$round <= max(cartola$atletas.rodada_id))
matches <- matches[, c("round", "home_team", "home_score", "away_score", "away_team", "goals_dif")] 

# Criar banco de dados para concatenar com dados dos jogadores
matches <- gather(matches, casa, team, -home_score, -away_score, -round, -goals_dif)

# Transformar variável nome
matches$casa <- ifelse(matches$casa == "home_team", "Casa", "Fora")

# Left join com cartola
cartola <- left_join(x = cartola, y = matches, by = c("atletas.clube.id.full.name" = "team", "atletas.rodada_id" = "round"))

# Remover objetos desnecessários e sobrescrever cartola
write.csv(cartola, "db/2017/cartola_2017.csv", row.names = FALSE)
rm(teamCodes, matches, cartola)
