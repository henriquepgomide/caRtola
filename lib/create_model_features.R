# TODO
# Create variables for each round:
  # ((Number of goals scored) / (N of matches))  ## full schedule; last 3 rounds;
  # ((Number of goals against) / (N of matches))

library(dplyr)
library(tidyr)

matches <- read.csv("db/2017/matches-brasileirao-2017.csv", stringsAsFactors = FALSE)

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

df <- 

df %>%
  filter(df, round <= 2) %>%
  group_by(team) %>%
  mutate(expected_goals = sum(goals.scored)/ length(unique(round)))
