library(dplyr)
library(plyr)
library(car)
library(RcppRoll)
library(fbRanks)
library(reshape2)
library(zoo)

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Merge years 2014 to 2017
#%%%%%%%%%%%%%%%%%%%%%%%%%

# Open data frames
df_2014 <- read.csv("data/2014/2014_scouts_raw.csv", stringsAsFactors = FALSE)
df_2015 <- read.csv("data/2015/2015_scouts_raw.csv", stringsAsFactors = FALSE)
df_2016 <- read.csv("data/2016/2016_scouts_raw.csv", stringsAsFactors = FALSE)
df_2017 <- read.csv("data/2017/2017_scouts_raw.csv", stringsAsFactors = FALSE)

# Inser column year into data
df_2014$ano <- 2014
df_2015$ano <- 2015
df_2016$ano <- 2016
df_2017$ano <- 2017

# Convert Participou into logic
df_2014$Participou <- ifelse(df_2014$Participou == 1, 
                             TRUE, 
                             FALSE)

# Set same col names for all data frames
colnames(df_2014)[c(1,3)] <-  c("AtletaID", "ClubeID")

# Fix 2015 scouts - they are aggregated, wrong format.
# Sort data by id and round 
df_2015 <- 
  df_2015 %>%
  arrange(AtletaID, -Rodada)

df_temp <- df_2015

# Create a data.frame to manipulate scouts
df_temp <- df_temp[, c(3,9:26)]

df_temp <- df_temp %>%
  group_by(AtletaID) %>%
  mutate_all(funs(abs(diff(c(.,0))))) %>%
  ungroup

df_temp$Rodada <- df_2015$Rodada

# Remove aggregated scouts statistics
df_2015 <- df_2015[, -c(9:26)]

# Join with proper scouts
df_2015 <- left_join(df_2015, df_temp, by = c("AtletaID", "Rodada"))
rm(df_temp)

# Merge data frames            
df_4y <- bind_rows(df_2014, df_2015, df_2016, df_2017)
df_4y$Posicao <- Recode(df_4y$Posicao, "1 = 'gol'; 2 = 'lat'; 3 = 'zag'; 
                                       4 = 'mei'; 5 = 'ata'; 6 = 'tec'")
df_4y$ClubeID <- as.character(df_4y$ClubeID) 

# Get 2018 cartola data
source("src/R/data_wrangling.R")

# Set better names for Cartola data.frame
names(cartola) <- c("AtletaID", "Rodada", "Nome", 
                    "slug", "Apelido", "foto",
                    "Clube_id", "Posicao", "Status", 
                    "Pontos", "Preco", "PrecoVariacao",
                    "PontosMedia", "ClubeID",
                    c(names(cartola)[15:30]))
cartola$ano <- 2018

temp1 <- read.csv("data/times_ids.csv", stringsAsFactors = FALSE)
cartola$ClubeID <- mapvalues(cartola$ClubeID, 
                             from = as.vector(temp1$nome.cartola), 
                             to = as.vector(temp1$id))
rm(df_2014, df_2015, df_2016, df_2017)

# Merge data frames
df <- bind_rows(df_4y, cartola)
rm(cartola, df_4y)
df <- df[, -c(11:15,16,36:56)]

# Estimate mean by player
df <- df %>%
  arrange(AtletaID, ano, Rodada)

df$Participou <- ifelse(df$PrecoVariacao == 0, FALSE, TRUE)

df <- df %>% 
  group_by(AtletaID) %>% 
  mutate_all(funs(na.locf(., na.rm = FALSE))) %>% 
  ungroup

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Create Team Features
#%%%%%%%%%%%%%%%%%%%%%%%%%

round_start_date <- as.Date("2018-05-18") # Start round date you want to predict
round_max_date   <- as.Date("2018-05-21") # Max date round you want to predict

# Open team codes
temp1 <- read.csv("~/caRtola/data/times_ids.csv", stringsAsFactors = FALSE)

# Open data frames
df_2014 <- read.csv("~/caRtola/data/2014/2014_partidas.csv", stringsAsFactors = FALSE)
df_2015 <- read.csv("~/caRtola/data/2015/2015_partidas.csv", stringsAsFactors = FALSE)
df_2016 <- read.csv("~/caRtola/data/2016/2016_partidas.csv", stringsAsFactors = FALSE)
df_2017 <- read.csv("~/caRtola/data/2017/2017_partidas.csv", stringsAsFactors = FALSE)
df_2018 <- read.csv("~/caRtola/data/2018/2018_partidas.csv", stringsAsFactors = FALSE)

# Merge data frames
matches <- bind_rows(df_2014, df_2015, df_2016, df_2017, df_2018)
rm(df_2014, df_2015, df_2016, df_2017, df_2018)

# Standardize team names
matches$home_team <- plyr::mapvalues(matches$home_team, from = as.vector(temp1$nome.cbf), to = as.vector(temp1$id), warn_missing = FALSE)
matches$away_team <- plyr::mapvalues(matches$away_team, from = as.vector(temp1$nome.cbf), to = as.vector(temp1$id), warn_missing = FALSE)

# Split string into numeric values
matches            <- separate(matches, score, c("home_score","vs","away_score"), convert = TRUE)
matches$home_score <- as.integer(matches$home_score)

# Remove games that don't have a defined date
matches <- 
  matches %>%
  filter(date != "A definir")

# Remove useless variables X, vs, X.1
matches <- matches[, -c(1, 7, 11)]

# Convert character to date format
matches$date      <- as.Date(matches$date, format = "%d/%m/%Y")
colnames(matches) <- c("game","round","date", 
                       "home.team","home.score", "away.score",
                       "away.team","arena")


# Rank teams
team_features <- rank.teams(scores          = matches, 
                            family          = "poisson",
                            fun             = "speedglm",
                            max.date        = round_start_date,
                            time.weight.eta = 0.01)

teamPredictions <- predict.fbRanks(team_features, 
                                   newdata  = matches[, c(3,4,7)],
                                   min.date = round_start_date,
                                   max.date = round_max_date)

matches_fb <- dplyr::left_join(matches, teamPredictions$scores, by = c("date","home.team", "away.team"))
matches_fb <- subset(matches_fb, matches$date >= round_start_date & matches$date <= round_max_date)
matches_fb <- matches_fb[,-c(9,10,13,14,22,23)]

# Remove temp dataframes
rm(teamPredictions, team_features)

#matches_fb$home.team <- plyr::mapvalues(matches_fb$home.team, from = as.vector(temp1$id), to = as.vector(temp1$nome.cartola), warn_missing = FALSE)
#matches_fb$away.team <- plyr::mapvalues(matches_fb$away.team, from = as.vector(temp1$id), to = as.vector(temp1$nome.cartola), warn_missing = FALSE)

matches_fb <- 
  matches_fb %>%
  dplyr::select(home.team, home.attack, home.defend, away.team, away.attack, away.defend, home.win, away.win, tie)

matches_fb$id <- 1:nrow(matches_fb)
matches_fb[,c("home.attack","home.defend", "away.attack", "away.defend", "home.win", "away.win", "tie")] <- round(matches_fb[,c("home.attack","home.defend", "away.attack", "away.defend", "home.win", "away.win", "tie")],2)

colnames(matches_fb) <- c("time_casa", "ataque_casa","defesa_casa",
                          "time_fora", "ataque_fora","defesa_fora",
                          "vitoria_casa", "vitoria_fora", "empate")
matches_fb$id <- 1:nrow(matches_fb)


# Subset data until last round
matches_fb <- subset(matches_fb, matches_fb$date <= "2018-05-21")

# Create data.frame to merge to player data
temp2 <- melt(matches_fb, id = c("round", "date", "home.score.x", "away.score.x", 
                                 "pred.home.score", "pred.away.score",
                                 "home.attack","home.defend"), 
              measure.vars = c("home.team", "away.team"))

# Recode date variable into year
temp2 <- separate(temp2, date, c("ano", "mes","dia"))
temp2$value <- as.integer(temp2$value)
temp2$ano <- as.integer(temp2$ano)
df$ClubeID <- as.integer(df$ClubeID)
df$Rodada <- as.integer(df$Rodada)
df$ano <- as.integer(df$ano)

# Left join com cartola
cartola <- left_join(x = data.frame(df), y = temp2, by = c("ClubeID" = "value", "Rodada" = "round", "ano" = "ano"))

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Create data.frame with aggregated data
#%%%%%%%%%%%%%%%%%%%%%%%%%
write.csv(subset(cartola, cartola$Participou == TRUE | cartola$PrecoVariacao != 0), 
          "db/cartola_aggregated.csv", row.names = FALSE)

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Create data.frame for predicting next round stats
#%%%%%%%%%%%%%%%%%%%%%%%%%
df_pred <- subset(cartola, cartola$ano == 2017 & cartola$Rodada == 37 & cartola$Status == "Provável")
variaveis <- c(2, 3, 5, 7, 8, 9, 29,30, 32:70, 73:77)
df_pred <- df_pred[, variaveis]

df_pred$Rodada <- 38
df_pred <- left_join(x = df_pred[, -c(46:52)],
                     y = subset(temp2, temp2$round == 38 & temp2$ano == 2017), 
                     by = c("ClubeID" = "value", "Rodada" = "round", "ano" = "ano"))
df_pred$home.score.x <- ifelse(is.na(df_pred$home.score.x), df_pred$pred.home.score, df_pred$home.score.x)
df_pred$away.score.x <- ifelse(is.na(df_pred$away.score.x), df_pred$pred.away.score, df_pred$away.score.x)

# rm(matches, matches_fb, temp2)
