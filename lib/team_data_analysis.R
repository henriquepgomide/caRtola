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

# Convert variables into factors - Converter variaveis para fator
partiteAll$country <- as.factor(partiteAll$country)
partiteAll$continent <- as.factor(partiteAll$continent)
partiteAll$FIFAregion <- as.factor(partiteAll$FIFAregion)

# Select data from Brazil - Selecionar dados do Brasil
brasil_df <- filter(partiteAll, country == "Brazil")

# Remove garbage variables - Remover variáveis inúteis
brasil_df <- select(brasil_df, -FIFAregion, -region, -country, -continent)

# Definir rodada do brasileiro
roundNumber <- 10

# Data from 2016 - Dados de 2016
matches_2016 <- read.csv("db/2016/matches-brasileirao-2016.csv", stringsAsFactors = FALSE)
matches_2016 <- separate(matches_2016, score, c("home_goals","vs","away_goals"))
matches_2016 <- matches_2016[, -c(6,9,10)]

# Remove accents - Remover acentos das strings
matches_2016$home_team <- iconv(matches_2016$home_team,to="ASCII//TRANSLIT")
matches_2016$away_team <- iconv(matches_2016$away_team,to="ASCII//TRANSLIT")

# Create data.frame to predict results based on our model
matches_predict <- filter(matches_2016, round == roundNumber)

# Create data.frame with our current data
matches_2016 <- filter(matches_2016, round < roundNumber)

# Convert into numeric
matches_2016[,5:6] <- sapply(matches_2016[,5:6], function(x) as.numeric(x))

#--------
# EDA----
#--------

# Histogram of goals scored
ggplot(matches_2016, aes(home_goals)) + geom_histogram()
ggplot(matches_2016, aes(away_goals)) + geom_histogram()

#-----------------------
# Poision Regression----
#-----------------------

# Convert data to run regression
brasileirao_2016 <- gather(matches_2016, "home_goals", "away_goals", 5:6)
colnames(brasileirao_2016) <- c("game", "round","date", "team", "opponent", "home", "goals")
brasileirao_2016$home <- ifelse(brasileirao_2016$home == "home_goals", 1, 0)

# Create model
model0 <- glm(goals ~ home + team + opponent, family=poisson(link=log), data=brasileirao_2016)

# Print model
summary(model0)

#---------------------
# Predict Goals-------
#---------------------

round_predictions <- gather(matches_predict, "home_goals", "away_goals", 5:6)
colnames(round_predictions) <- c("game", "round","date", "team", "opponent", "home", "goals")
round_predictions$home <- ifelse(round_predictions$home == "home_goals", 1, 0)
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

colnames(round_predictions)[6] <- "awayGoals"
colnames(round_predictions)[7] <- "homeGoals"

