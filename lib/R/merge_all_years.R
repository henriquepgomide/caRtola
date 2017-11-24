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
df_2014 <- read.csv("db/2014/Scouts.csv", stringsAsFactors = FALSE)
df_2015 <- read.csv("db/2015/Scouts.csv", stringsAsFactors = FALSE)
df_2016 <- read.csv("db/2016/Scouts.csv", stringsAsFactors = FALSE)

# Inser column year into data
df_2014$ano <- 2014; df_2015$ano <- 2015; df_2016$ano <- 2016

# Convert Participou into logic
df_2014$Participou <- ifelse(df_2014$Participou == 1, TRUE, FALSE)

# Set same col names for all data frames
colnames(df_2014)[c(1,3)] <-  c("AtletaID", "ClubeID")

# Fix 2015 scouts - they are aggregated, wrong format.
# Sort data by id and round 
df_2015 <- 
  df_2015 %>%
  arrange(AtletaID, - Rodada)

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
df_3y <- bind_rows(df_2014, df_2015, df_2016)
df_3y$Posicao <- Recode(df_3y$Posicao, "1 = 'gol'; 2 = 'lat'; 3 = 'zag'; 
                     4 = 'mei'; 5 = 'ata'; 6 = 'tec'")
df_3y$ClubeID <- as.character(df_3y$ClubeID) 

# Get 2017 cartola data
source("lib/R/data_wrangling.R")

# Set better names for Cartola data.frame
names(cartola) <- c("AtletaID", "Rodada", "Nome", 
                    "Apelido", "foto","Clube_id", 
                    "Posicao","ClubeID", "Status", 
                    "Pontos", "Preco", "PrecoVariacao",
                    "PontosMedia", "Jogos","scout",
                    c(names(cartola)[16:33]))
cartola$ano <- 2017

temp1 <- read.csv("db/teamids-consolidated.csv", stringsAsFactors = FALSE)
cartola$ClubeID <- mapvalues(cartola$ClubeID, 
                             from = as.vector(temp1$nome.cartola), 
                             to = as.vector(temp1$id))
rm(df_2014, df_2015, df_2016)

# Merge data frames
df <- bind_rows(df_3y, cartola)
rm(cartola, df_3y)
df <- df[, -c(11:15,16,36,38,39, 41)]

# Estimate mean by player
df <- df %>%
  arrange(AtletaID, ano, Rodada)

df <- df %>%
  group_by(AtletaID) %>%
  mutate(avg.Points = cummean(Pontos), 
         avg.last05 = roll_meanr(Pontos, n = 5, fill = 1),
         avg.FS = cummean(FS),
         avg.FS.l05 = roll_meanr(FS, n = 5, fill = 1),
         avg.PE = cummean(PE),
         avg.PE.l05 = roll_meanr(PE, n = 5, fill = 1),
         avg.A = cummean(A),
         avg.A.l05 = roll_meanr(A, n = 5, fill = 1),
         avg.FT = cummean(FT),
         avg.FT.l05 = roll_meanr(FT, n = 5, fill = 1),
         avg.FD = cummean(FD),
         avg.FD.l05 = roll_meanr(FD, n = 5, fill = 1),
         avg.FF = cummean(FF),
         avg.FF.l05 = roll_meanr(FF, n = 5, fill = 1),
         avg.G = cummean(G),
         avg.G.l05 = roll_meanr(G, n = 5, fill = 1),
         avg.I = cummean(I),
         avg.I.l05 = roll_meanr(I, n = 5, fill = 1),
         avg.PP = cummean(PP),
         avg.PP.l05 = roll_meanr(PP, n = 5, fill = 1),
         avg.RB = cummean(RB),
         avg.RB.l05 = roll_meanr(RB, n = 5, fill = 1),
         avg.FC = cummean(FC),
         avg.FC.l05 = roll_meanr(FC, n = 5, fill = 1),
         avg.GC = cummean(GC),
         avg.GC.l05 = roll_meanr(GC, n = 5, fill = 1),
         avg.CA = cummean(CA),
         avg.CV.l05 = roll_meanr(CV, n = 5, fill = 1),
         avg.SG = cummean(SG),
         avg.SG.l05 = roll_meanr(SG, n = 5, fill = 1),
         avg.DD = cummean(DD),
         avg.DD.l05 = roll_meanr(DD, n = 5, fill = 1),
         avg.DP = cummean(DP),
         avg.DP.l05 = roll_meanr(DP, n = 5, fill = 1),
         avg.GS = cummean(GS),
         avg.GS.l05 = roll_meanr(GS, n = 5, fill = 1),
         risk_points = roll_sdr(Pontos, n = 10, fill = 1)
         ) %>%
  ungroup

df$Participou <- ifelse(df$PrecoVariacao == 0, FALSE, TRUE)

df <- df %>% 
  group_by(AtletaID) %>% 
  mutate_all(funs(na.locf(., na.rm = FALSE))) %>% 
  ungroup

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Create Team Features
#%%%%%%%%%%%%%%%%%%%%%%%%%

# Open data frames
df_2014 <- read.csv("db/2014/matches-brasileirao-2014.csv", stringsAsFactors = FALSE)
df_2015 <- read.csv("db/2015/matches-brasileirao-2015.csv", stringsAsFactors = FALSE)
df_2016 <- read.csv("db/2016/matches-brasileirao-2016.csv", stringsAsFactors = FALSE)
df_2017 <- read.csv("db/2017/matches-brasileirao-2017.csv", stringsAsFactors = FALSE)

# Merge data frames
matches <- bind_rows(df_2014, df_2015, df_2016, df_2017)
rm(df_2014, df_2015, df_2016, df_2017)

# Standardize team names
matches$home_team <- plyr::mapvalues(matches$home_team, from = as.vector(temp1$nome.cbf), to = as.vector(temp1$id))
matches$away_team <- plyr::mapvalues(matches$away_team, from = as.vector(temp1$nome.cbf), to = as.vector(temp1$id))
rm(temp1)

# Split string into numeric values
matches <- separate(matches, score, c("home_score","vs","away_score"), convert = TRUE)
matches$home_score <- as.integer(matches$home_score)

# Remove useless variables
matches <- matches[,-c(1,7,11)]

# Convert character to date format
matches$date <- as.Date(matches$date, format = "%d/%m/%Y")
colnames(matches) <- c("game","round","date", "home.team","home.score",
                       "away.score","away.team","arena")


# Rank teams
team_features <- rank.teams(scores = matches, 
                             family = "poisson",
                             fun = "speedglm",
                             max.date="2017-11-17",
                             time.weight.eta = 0.01)

teamPredictions <- predict.fbRanks(team_features, 
                      newdata = matches[,c(3:4,7)], 
                      min.date= as.Date("2017-11-24"),
                      max.date = as.Date("2017-11-27"))

matches_fb <- left_join(matches, teamPredictions$scores, by = c("date","home.team", "away.team"))
matches_fb <- matches_fb[,-c(9,10,13,14,22,23)]
rm(teamPredictions, team_features)

# Subset data until last round
matches_fb <- subset(matches_fb, matches_fb$date <= "2017-11-27")

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
df_pred <- subset(cartola, cartola$ano == 2017 & cartola$Rodada == 36 & cartola$Status == "Provável")
variaveis <- c(2, 3, 5, 7, 8, 9, 29,30, 32:70, 73:77)
df_pred <- df_pred[, variaveis]

df_pred$Rodada <- 37
df_pred <- left_join(x = df_pred[, -c(46:52)],
                     y = subset(temp2, temp2$round == 37 & temp2$ano == 2017), 
                     by = c("ClubeID" = "value", "Rodada" = "round", "ano" = "ano"))
df_pred$home.score.x <- ifelse(is.na(df_pred$home.score.x), df_pred$pred.home.score, df_pred$home.score.x)
df_pred$away.score.x <- ifelse(is.na(df_pred$away.score.x), df_pred$pred.away.score, df_pred$away.score.x)

# rm(matches, matches_fb, temp2)
