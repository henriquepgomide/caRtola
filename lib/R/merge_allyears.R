library(dplyr)
library(car)
library(RcppRoll)
library(fbRanks)

# This code is stil experimental. Do not run it, unless you know what are you doing.

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Merge years 2014 to 2017
#%%%%%%%%%%%%%%%%%%%%%%%%%

# Open data frames
df_2014 <- read.csv("db/2014/Scouts.csv", stringsAsFactors = FALSE)
df_2015 <- read.csv("db/2015/Scouts.csv", stringsAsFactors = FALSE)
df_2016 <- read.csv("db/2016/Scouts.csv", stringsAsFactors = FALSE)

# Inser column year into data
df_2014$ano <- 2014; df_2015$ano <- 2015; df_2016$ano <- 2016

# Convert Participou into data frame
df_2014$Participou <- ifelse(df_2014$Participou == 1, TRUE, FALSE)

# Set same col names for all data frames
colnames(df_2014)[c(1,3)] <-  c("AtletaID", "ClubeID")

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
                    c(names(cartola)[16:37]))
cartola$ano <- 2017

temp1 <- read.csv("db/teamids-consolidated.csv", stringsAsFactors = FALSE)
cartola$ClubeID <- mapvalues(cartola$ClubeID, 
                             from = as.vector(temp1$nome.cartola), 
                             to = as.vector(temp1$id))
rm(df_2014, df_2015, df_2016, df_pred)

# Merge data frames
df <- bind_rows(df_3y, cartola)
rm(cartola, df_3y)
df <- df[, -c(11:15,16,36,38,39, 41:46)]

# Estimate mean by player
df <- df %>%
  arrange(AtletaID, ano, Rodada)

df <- df %>%
  group_by(AtletaID) %>%
  mutate(media = cummean(Pontos), 
         roll.media = roll_meanr(Pontos, n = 5, fill = 1))

df$Participou <- ifelse(df$PrecoVariacao == 0, FALSE, TRUE)


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
                             max.date="2017-07-08",
                             time.weight.eta = 0.01)

teamPredictions <- predict.fbRanks(team_features, 
                      newdata = matches[,c(3:4,7)], 
                      min.date= min(matches$date),
                      max.date = as.Date("2017-07-12"))

matches_fb <- left_join(matches, teamPredictions$scores, by = c("date","home.team", "away.team"))
matches_fb <- matches_fb[,-c(9,10,13,14,22,23)]

# Create goal differential
matches_fb$goals_dif <-  matches_fb$home.score.x - matches_fb$away.score.x

# Subset data until last round
matches_fb <- subset(matches_fb, matches_fb$round <= max(cartola$atletas.rodada_id) + 1)



# Create data.frame to merge to player data

teste <- melt(matches_fb, id = c("round", "date", "home.team", "away.team"), 
     measure.vars = c("home.score.x", "away.score.x", 
                      "pred.home.score", "pred.away.score",
                      "home.attack","home.defend"))

teste <- gather(matches_fb, casa, team, -home.score.x, -away.score.x, 
                -arena, -pred.home.score, -pred.away.score, -home.attack,
                -away.attack, -away_defend, -home.win, -away.win, -tie, -goals_dif) 


matches$goals_dif <-  matches$home.score - matches_fb$away.score
teste <- gather(matches, casa, team, -home.score, -away.score, -round, -goals_dif)

# Recode variable name
matches$casa <- ifelse(matches$casa == "home_team", "Casa", "Fora")

# Left join com cartola
cartola <- left_join(x = cartola, y = matches, by = c("atletas.clube.id.full.name" = "team", "atletas.rodada_id" = "round"))

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Subset Data Frame
#%%%%%%%%%%%%%%%%%%%%%%%%%

# Remove cases with no data
df <- subset(df, df$Participou == TRUE)


#### 
# Modeling
####

treino <- df %>%
  filter(!(Rodada < 11 & ano != 2017))

validacao <- df %>%
  filter(Rodada == 11 & ano == 2017)

# Selecionar somente algumas variáveis
variaveis <- c("ClubeID", "Posicao", "media", "roll.media", "Pontos", "PontosMedia")

treino <- treino[, variaveis]
variaveis <-  validacao[, variaveis]

# Controles para os modelos
## Regression Models
ctrl <- trainControl(method = "repeatedcv", number = 10, repeats = 10, allowParallel = TRUE, verboseIter = TRUE)

glmModel_0  <- train(Pontos ~ ., data = treino, 
                     method="glm", metric = "RMSE", preProcess = c("knnImpute","scale", "center"),
                     trControl = ctrl, na.action = na.pass)

glmModel_0 <- glm(data = treino, formula = Pontos ~ PontosMedia, family = gaussian, na.action = na.omit)

predictions <- predict(glmModel_0, newdata = validacao)
postResample(pred = predictions, obs = validacao$Pontos)
