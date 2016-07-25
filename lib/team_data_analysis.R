# What? ----------------------------------------------
# This script is intended to run exploratory analysis
# on team performance in Brazil
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Este script tem como objetivo executar algumas
# análises exploratórias nos dados de partidas
# entre times no Brasil
# ----------------------------------------------------

# Load libraries - Carregar pacotes
library(dplyr)
library(tidyr)
library(ggplot2)

# Load data - carregar banco de dados
load("db/worldTeamData/partiteAll")

#####################
# Previous years ----
#####################

# Convert variables into factors - Converter variaveis para fator
partiteAll$country <- as.factor(partiteAll$country)
partiteAll$continent <- as.factor(partiteAll$continent)
partiteAll$FIFAregion <- as.factor(partiteAll$FIFAregion)

# Select data from Brazil - Selecionar dados do Brasil
brasil_df <- filter(partiteAll, country == "Brazil")

# Remove garbage variables - Remover variáveis inúteis
brasil_df <- select(brasil_df, -FIFAregion, -time, -region, -country, -teams, -score, -continent, -totalGoals, -deltaGoal, -year)
brasil_df$homeTeam <- iconv(brasil_df$homeTeam,to="ASCII//TRANSLIT")
brasil_df$visitingTeam <- iconv(brasil_df$visitingTeam,to="ASCII//TRANSLIT")

#####################
# 2016 ----
#####################

# Definir rodada do brasileiro
roundNumber <- 13

# Data from 2016 - Dados de 2016
matches_2016 <- read.csv("db/2016/matches-brasileirao-2016.csv", stringsAsFactors = FALSE)
matches_2016 <- separate(matches_2016, score, c("homeScore","vs","visitingScore"))
matches_2016 <- matches_2016[, -c(1,2,7,10,11)]
colnames(matches_2016) <- c("round", "date", "homeTeam", "homeScore", "visitingScore", "visitingTeam")

# Remove accents - Remover acentos das strings
matches_2016$homeTeam <- iconv(matches_2016$homeTeam,to="ASCII//TRANSLIT")
matches_2016$visitingTeam <- iconv(matches_2016$visitingTeam,to="ASCII//TRANSLIT")

# Create data.frame to predict results based on our model
matches_predict <- filter(matches_2016, round == roundNumber)

# Create data.frame with our current data
matches_2016 <- filter(matches_2016, round < roundNumber)

# Convert into numeric
matches_2016[,4:5] <- sapply(matches_2016[,4:5], function(x) as.numeric(x))

#--------
# EDA----
#--------

# Histogram of goals scored
#ggplot(matches_2016, aes(home_goals)) + geom_histogram()
#ggplot(matches_2016, aes(away_goals)) + geom_histogram()

#-----------------------
# Poision Regression----
#-----------------------

# Convert data to run regression
brasileirao_2016 <- gather(matches_2016, "homeScore", "visitingScore", 4:5)
colnames(brasileirao_2016) <- c("round","date", "team", "opponent", "home", "goals")
brasileirao_2016$home <- ifelse(brasileirao_2016$home == "homeScore", 1, 0)

# Create model
model0 <- glm(goals ~ home + team + opponent, family=poisson(link=log), data=brasileirao_2016)

# Print model
summary(model0)

#---------------------
# Predict Goals-------
#---------------------

round_predictions <- gather(matches_predict, "homeScore", "visitingScore", 4:5)
colnames(round_predictions) <- c("round","date", "team", "opponent", "home", "goals")
round_predictions$home <- ifelse(round_predictions$home == "homeScore", 1, 0)
round_predictions$goals <- predict(model0, newdata = round_predictions, type="response")
round_predictions <- spread(round_predictions, home, goals)

round_predictions$homeOdd <- NULL
round_predictions$drawOdd <- NULL
round_predictions$awayOdd <- NULL

nsim <- 10000

for (i in 1:length(round_predictions$round)){
  
  homeGoalsSim <- rpois(nsim, round_predictions$`1`[i])
  awayGoalsSim <- rpois(nsim,round_predictions$`0`[i])
  goalDiffSim <- homeGoalsSim - awayGoalsSim
  
  round_predictions$homeOdd[i] <- sum(goalDiffSim > 0) / nsim
  round_predictions$drawOdd[i] <- sum(goalDiffSim == 0) / nsim
  round_predictions$awayOdd[i] <- sum(goalDiffSim < 0) / nsim
  
}

colnames(round_predictions)[5] <- "awayGoals"
colnames(round_predictions)[6] <- "homeGoals"
round_predictions$goalsDiff <- round_predictions$homeGoals - round_predictions$awayGoals

# Print round predictions
# Goals diff
arrange(round_predictions, desc(goalsDiff))
# Most goals
arrange(round_predictions, desc(homeGoals))
# Less goals
arrange(round_predictions, homeGoals)

# Check model
# arrange(round_predictions, team)
# arrange(matches_predict, home_team)
