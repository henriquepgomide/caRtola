# TODO
  # 1. Fix scouts
  # 2. Create features
      # ((Number of goals scored) / (N of matches))  ## full schedule; last 3 rounds;
      # ((Number of goals against) / (N of matches))

library(dplyr)
library(tidyr)


# Fix scouts statistics
cartola <- read.csv("db/2017/cartola_2017.csv", stringsAsFactors = FALSE)

# What I have to do?
temp.df <- data.frame(atletas.atleta_id = sort(rep(unique(cartola$atletas.atleta_id), length(unique(cartola$atletas.rodada_id)))),
                      atletas.rodada_id = rep(0:(length(unique(cartola$atletas.rodada_id)) - 1)))



# Create a data.frame to manipulate variables
df <- cartola[, c(2,5,16:33)]

# Convert NA values into zeroes
df[,3:20] <- sapply(df[,3:20], function(x) ifelse(is.na(x), 0, x))

  

teste %>%
  group_by(atletas.atleta_id) %>%
  
  

df <- df %>%
      arrange(atletas.atleta_id, - atletas.rodada_id) %>%
      group_by(atletas.atleta_id) %>%
      mutate_all(funs(abs(diff(c(0,.)))))


df %>%
  filter(atletas.atleta_id == "36540")
    


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
