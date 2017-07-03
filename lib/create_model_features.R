# TODO
  # 1. Fix scouts
  # 2. Create features
      # ((Number of goals scored) / (N of matches))  ## full schedule; last 3 rounds;
      # ((Number of goals against) / (N of matches))

library(dplyr)
library(tidyr)

# Fix scouts statistics
cartola <- read.csv("db/2017/cartola_2017.csv", stringsAsFactors = FALSE)

# Sort data by id and round 
df <- 
  cartola %>%
  arrange(atletas.atleta_id, - atletas.rodada_id)

# Create a data.frame to manipulate variables
df <- df[, c(2,16:33)]

# Convert NA values into zeroes
df[,2:19] <- sapply(df[,2:19], function(x) ifelse(is.na(x), 0, x))

df <- df %>%
      group_by(atletas.atleta_id) %>%
      mutate_all(funs(abs(diff(c(0,.)))))
df$atletas.rodada_id <- cartola$atletas.rodada_id

# Remove aggregated scouts statistics
cartola <- cartola[, -c(16:33)]
df <- left_join(df, cartola, by = c("atletas.atleta_id", "atletas.rodada_id"))


