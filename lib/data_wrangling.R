#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# DATA WRANGLING ----
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 1. Merge data from different rounds                   
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# This function merges data from different rounds and merge them into
# a single data.frame for a give year.

merge_cartola_data <- function(year){
  year <- as.character(year)
  require(dplyr)
  setwd(paste0("db/", year))
  files <- list.files(pattern = "rodada")
  
  list_of_data_frames <- lapply(files, function(x){
    read.csv(x, header = TRUE, stringsAsFactors = FALSE)
  })
  
  df <- do.call(bind_rows, list_of_data_frames)
  return(df)
}

# Let's open 2017's data
cartola <- merge_cartola_data(2017)
setwd("../../")
# Remove useless variable
cartola <- cartola[, -c(33)]

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 2. Wrange scouts from Cartola API, which is aggregated ----
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Carregar pacotes
library(dplyr)
library(tidyr)

# Sort data by id and round 
cartola <- 
  cartola %>%
  arrange(atletas.atleta_id, - atletas.rodada_id)

df <- cartola

# Create a data.frame to manipulate scouts
df <- df[, c(2,16:33)]

# Convert NA values into zeroes
df[,2:19] <- sapply(df[,2:19], function(x) ifelse(is.na(x), 0, x))

df <- df %>%
      group_by(atletas.atleta_id) %>%
      mutate_all(funs(abs(diff(c(.,0)))))
df$atletas.rodada_id <- cartola$atletas.rodada_id

# Remove aggregated scouts statistics
cartola <- cartola[, -c(16:33)]

# Join with proper scouts
df <- left_join(df, cartola, by = c("atletas.atleta_id", "atletas.rodada_id"))

# Arrange variable columns
df <- df[, c(1, 20:33, 2:19)]

cartola <- df
rm(df)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 3. Add team features into data ----
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# What?
# This script proccesses data from CBF matches and
# add home and away information into cartola data.frame

# Load libraries
library(plyr)

# Load team codes and match data
teamCodes <- read.csv("db/teamids-consolidated.csv")
matches <- read.csv("db/2017/matches-brasileirao-2017.csv", stringsAsFactors = FALSE)

# Standardize team names
matches$home_team <- plyr::mapvalues(matches$home_team, from = as.vector(teamCodes$nome.cbf), to = as.vector(teamCodes$nome.cartola))
matches$away_team <- plyr::mapvalues(matches$away_team, from = as.vector(teamCodes$nome.cbf), to = as.vector(teamCodes$nome.cartola))

# Split string into numeric values
matches <- separate(matches, score, c("home_score","vs","away_score"), convert = TRUE)
matches$home_score <- as.integer(matches$home_score)

# Remove useless variables
matches <- matches[,-c(1,7,11)]

# Create goal differential
matches$goals_dif <-  matches$home_score - matches$away_score

# Subset data until last round
matches <- subset(matches, matches$round <= max(cartola$atletas.rodada_id) + 1)
matches <- matches[, c("round", "home_team", "home_score", "away_score", "away_team", "goals_dif")] 

# Create data.frame to merge to player data
matches <- gather(matches, casa, team, -home_score, -away_score, -round, -goals_dif)

# Recode variable name
matches$casa <- ifelse(matches$casa == "home_team", "Casa", "Fora")

# Left join com cartola
cartola <- left_join(x = cartola, y = matches, by = c("atletas.clube.id.full.name" = "team", "atletas.rodada_id" = "round"))

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 3. Create data.frame for predicting next round stats ----
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

df_pred <- cartola[!duplicated(cartola$atletas.atleta_id), 
                   c("atletas.atleta_id", "atletas.apelido", "atletas.clube.id.full.name", 
                       "atletas.posicao_id", "atletas.media_num", "atletas.status_id", 'atletas.jogos_num', "PE",
                       "SG", "FC", "FS", "I", "RB", "FD", "A", "G", "FF","DD","CA", "GS",
                       "FT","CV","PP","DP","GC")]

df_pred$atletas.rodada_id <- max(matches$round)
df_pred <- left_join(x = df_pred,
                   y = subset(matches, matches$round == max(matches$round)), 
                              by = c("atletas.clube.id.full.name" = "team", "atletas.rodada_id" = "round"))

df_pred[, 8:25] <- sapply(df_pred[, 8:25], function(x) as.numeric(NA))

# Replace data from the last round with the average values
df <-
  cartola %>%
  group_by(atletas.atleta_id) %>%
  summarize_at(c(11,15:32),
            funs(mean(., na.rm=TRUE)))

df_pred <- df_pred[, -c(8:25)]
df_pred <- left_join(df_pred, df, by = "atletas.atleta_id")
rm(df)