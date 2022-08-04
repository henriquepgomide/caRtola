# Create team features based on player performance
# Author: @henriquepgomide
# License: MIT

library(tidyverse)

# Get and process data
source("src/R/create_players_stats.R")

matches_19 <- read.csv("~/caRtola/data/2019/2019_partidas.csv",
                       stringsAsFactors = FALSE) 
matches_19 <- 
  matches_19 %>%
  select(home_team, away_team, round) %>%
  mutate(match_number = 1:nrow(matches_19))

matches_19g <- gather(matches_19, 
                       key = home_away,
                       value = team,
                       -round, -match_number)
matches_19g$round <- factor(matches_19g$round, ordered = TRUE)
matches_19g$team <- as.character(matches_19g$team)
matches_19g$home_away <- gsub("_team", "", matches_19g$home_away)

# Select variables for scouts
data <- 
  df.model %>%
  select(slug, team, rodadaF, posicao, 
         pontuacao, score.no.cleansheets,
         FC, FS, 
         PE, RB, SG, 
         shotsX, faltas, G, 
         GS, A, CA,
         CV,  home_away)
pontos <- 
  data %>%
  dplyr::group_by(team) %>%
  dplyr::summarize(pontuacao = sum(pontuacao) / max(as.integer(rodadaF)))


# EDA ---------------------------------------------------------------------

# Check how points from a given team stay around the mean and are quite stable
# Therefore, we can model and try to predict matches

ggplot(pontos_homeaway_f, 
       aes(x = rodadaF, y = pontuacao_mean, color = home_away, group = team)) + 
  geom_point() + 
  geom_smooth(aes(color = home_away, group = team)) + 
  facet_wrap(~ team)


# TODO --------------------------------------------------------------------

# 1. Create team features using cummean
pontos_homeaway_f <- 
  data %>%
  dplyr::group_by(team, home_away, rodadaF) %>%
  dplyr::arrange(team, home_away, rodadaF) %>%
  dplyr::summarize(pontuacao = sum(pontuacao)) %>%
  dplyr::mutate(pontuacao_mean = cummean(pontuacao)) %>%
  ungroup()
 
pontos_homeaway_f$rodadaF <- as.character(pontos_homeaway_f$rodadaF)
matches_19g$round <- as.character(matches_19g$round)

test <- 
  left_join(matches_19g, pontos_homeaway_f, 
            by = c("home_away" = "home_away",
                   "team"      = "team",
                   "round"     = "rodadaF"))
test <- 
  test %>%
  dplyr::select(-round)
  
teste <- 
  gather(test,
         key = "vars",
         value = "value",
         -home_away, -match_number)

teste_2 <- unite(teste, 
                 col = "vars",
                 "home_away","vars", 
                 sep = "_")

teste_3 <- spread(teste_2, 
                  key = "vars",
                  value = "value",
                  sep = "_", 
                  convert = TRUE)


# 2. Try to predict scores from a given round 
#    based on team features

ggplot(data = test, aes(x = pontuacao, color = home_away, fill = home_away)) + geom_density() + facet_wrap(~ team)