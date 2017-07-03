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
library(tidyr)

# Load team codes and match data
teamCodes <- read.csv("db/teamids-consolidated.csv")
matches <- read.csv("db/2017/matches-brasileirao-2017.csv", stringsAsFactors = FALSE)

# Standardize team names
matches$home_team <- mapvalues(matches$home_team, from = as.vector(teamCodes$nome.cbf), to = as.vector(teamCodes$nome.cartola))
matches$away_team <- mapvalues(matches$away_team, from = as.vector(teamCodes$nome.cbf), to = as.vector(teamCodes$nome.cartola))

# Split string into numeric values
matches <- separate(matches, score, c("home_score","vs","away_score"), convert = TRUE)
matches$home_score <- as.integer(matches$home_score)

# Remove useless variables
matches <- matches[,-c(1,7,11)]

# Create goal differential
matches$goals_dif <-  matches$home_score - matches$away_score

# Subset data until last round
matches <- subset(matches, matches$round <= max(cartola$atletas.rodada_id))
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

# YET TO BE DONE
# Replace data from the last round with the average values
# df <- 
#   df %>%
#   group_by(atletas.atleta_id) %>%
#   mutate_at(16:32, 
#             funs(ifelse(atletas.rodada_id == max(df$atletas.rodada_id), mean(., na.rm=TRUE), .)))
# df <- cartola