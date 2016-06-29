# What? ----------------------------------------------
# This script is intended to run exploratory analysis
# and run some models to predict player fantasy 
# performance
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Este script tem como objetivo executar algumas
# análises exploratórias e criar modelos para prever
# os resultados dos jogadores do cartola
# ----------------------------------------------------


# Load libraries
# Carregar pacotes
library(ggplot2)
library(reshape2)
library(caret)
library(plyr)
library(dplyr)
library(parallel)
library(doParallel)
library(forecast)

# Run script to fetch latest data
# Executar script para recuperar dados da API do cartola
#source("lib/caRtola_fetch.R")
#source("lib/team_data_scraper.R")

# Set working directory
# Configurar diretório de trabalho
setwd("db/2016")

# Get teams names, codes and position
# Recuperar nome dos times, códigos e posições
temp1 <- read.csv("teams_ids.csv", stringsAsFactors = FALSE)
classification  <- read.csv("tabela-times.csv", stringsAsFactors = FALSE)
teamData <- cbind(arrange(temp1, nome.completo), arrange(classification, Clube))
teamData <- teamData[,-1]
teamData <- select(teamData, Cod, nome, Clube, P, J, V, E, D, GP, GC, SG, VM, VV, DM, DV, CA, CV)
teamData <- arrange(teamData, desc(P), desc(SG))

# Get the files names
files <-  list.files(pattern="rodada*")
# Open data.frame
cartola_2016 <-  do.call(rbind, lapply(files, function(x) read.csv(x, stringsAsFactors = FALSE)))
cartola_2016$atletas.clube_id <- mapvalues(cartola_2016$atletas.clube_id, from = as.vector(teamData$Cod), to = as.vector(teamData$nome))

# Remove unecessary objects
rm(temp1, classification, files)

# Replace NA's with zeroes
cartola_2016[,15:32] <- sapply(cartola_2016[,15:32], function(x) ifelse(is.na(x), 0,x)) 

# Keep useful variables
cartola_2016 <- cartola_2016[, -c(1,2,4,12,13)]

# Subset players who mean score is diferent from 0
b <- tapply(cartola_2016$atletas.pontos_num, cartola_2016$atletas.atleta_id, mean)
c <- tapply(cartola_2016$atletas.jogos_num, cartola_2016$atletas.atleta_id, max)
gamesPlayed <- data.frame(atletas.atleta_id = names(b), avg = b, played_games = c)
cartola_2016 <- merge(cartola_2016, gamesPlayed, by = "atletas.atleta_id")

cartola_2016 <- subset(cartola_2016, cartola_2016$avg != 0 & cartola_2016$played_games > 6)
rm(gamesPlayed,c,b)

##########################
## EXPLORATORY ANALYSIS ##
##########################

# Histogram of points by position
ggplot(data = cartola_2016, aes(x = atletas.pontos_num, fill = atletas.posicao_id, colour = atletas.posicao_id)) +
  stat_density(alpha = .7) + scale_fill_brewer(palette = "Paired", type = "qual") + scale_colour_brewer(palette = "Paired", type = "qual") + theme(legend.position = "top")

# Boxplot of points by position
ggplot(data = cartola_2016, aes(atletas.posicao_id,atletas.pontos_num)) + geom_boxplot() + geom_jitter(width = .5, alpha = .15)

# Boxplot of point by team
ggplot(data = cartola_2016, aes(x = reorder(atletas.posicao_id, atletas.pontos_num, FUN = median), y = atletas.pontos_num)) + geom_boxplot() + facet_wrap(~atletas.clube_id)

# Boxplot of point by team ~ posicao_id
ggplot(data = cartola_2016, aes(x = reorder(atletas.clube_id, atletas.pontos_num, FUN = median), y = atletas.pontos_num)) + geom_boxplot() + facet_wrap(~atletas.posicao_id, ncol = 2)

# Scatterplot of points by diferent variables
for (i in 15:32){
print(ggplot(data = cartola_2016, aes(atletas.pontos_num, cartola_2016[,i], color = atletas.posicao_id)) + geom_point() + ylab(names(cartola_2016[i])))
}

# Boxplot of points by position for different variables
for (i in 15:32){
  print(
    ggplot(data = cartola_2016, aes(atletas.posicao_id,cartola_2016[,i])) + geom_boxplot() + geom_jitter(width = .5, alpha = .3) + ylab(names(cartola_2016[i]))
  )
}

# --------------------------
# BIVARIATE ANALYSIS
# --------------------------
 
# Reshape
cartola_Wide <- cartola_2016[, c("atletas.apelido", "atletas.rodada_id", "atletas.pontos_num", "CA", "FC","FD","FS","PE","RB","SG","FF","I","A","DD","GS","G","PP","FT","CV","DP","GC")]
cartola_Wide <- as.data.frame(cartola_Wide)
cartola_Wide <- reshape(cartola_Wide, idvar = "atletas.apelido", timevar = "atletas.rodada_id", direction = "wide")

# Check correlations among predictors over rounds
cor(select(cartola_Wide, contains("atletas.pontos_num")), use = "complete.obs") # Almost not correlated
cor(select(cartola_Wide, contains("CA.")), use = "complete.obs")   # Yellow card - Weak
cor(select(cartola_Wide, contains("FC.")), use = "complete.obs")   # Fouls made - High
cor(select(cartola_Wide, contains("FD.")), use = "complete.obs")   # Shots on goal - Somewhat
cor(select(cartola_Wide, contains("FS.")), use = "complete.obs")   # Fouls received - Strong
cor(select(cartola_Wide, contains("PE.")), use = "complete.obs")   # Bad passes - Strong
cor(select(cartola_Wide, contains("RB.")), use = "complete.obs")   # Steals - Somewhat
cor(select(cartola_Wide, contains("SG.")), use = "complete.obs")   # Somewhat
cor(select(cartola_Wide, contains("FF.")), use = "complete.obs")   # Shots off - Somewhat
cor(select(cartola_Wide, contains("I.")), use = "complete.obs")    # Offsides - Strong
cor(select(cartola_Wide, contains("A.")), use = "complete.obs")    # Assists - Weak
cor(select(cartola_Wide, contains("DD.")), use = "complete.obs")   # Hard saves - Somewhat   
cor(select(cartola_Wide, contains("GS.")), use = "complete.obs")   # Goals allowed - Strong
cor(select(cartola_Wide, contains("G.")), use = "complete.obs")    # Goals - None
cor(select(cartola_Wide, contains("PP.")), use = "complete.obs")   # Penalties lost - None
cor(select(cartola_Wide, contains("FT.")), use = "complete.obs")   # Shots on the post - None  
cor(select(cartola_Wide, contains("DP.")), use = "complete.obs")   # Penalties defended
cor(select(cartola_Wide, contains("GC.")), use = "complete.obs")   # Own goals - None
cor(select(cartola_Wide, contains("PPP.")), use = "complete.obs")  # Points per price - Weak 

# CONCLUSIONS
# Negative impact - Yellow card, fouls made, bad passes, offsides, goals allowed*
# Positive impact - Shons goal, fouls received, steals, shots off, assists, hard saves*, goals saved, shots on the post

##########################
## MODELING ##
##########################

#####################################
## GROUP 1 - Each observation as row
#####################################

# SPLIT DATA
## Bind data for modeling
test <- subset(cartola_2016, cartola_2016$atletas.rodada_id == 8)
train <- subset(cartola_2016, cartola_2016$atletas.rodada_id != 8)

train <- train[, -c(3,6,8,9,28,29)]
test <-  test[,  -c(3,6,8,9,28,29)]

colnames(train)[5] <- "outcome"
colnames(test)[5] <- "outcome"

## CONTROLS
ctrl <- trainControl(method = "repeatedcv", number = 10, repeats = 10, allowParallel = TRUE, verboseIter = TRUE) # Regression Models
rfGrid <-  expand.grid(mtry = c(10,20,40,80))                                                                    # Random Forest

## Find highly correlated predictors
predCor1 <- cor(cartola_2016[,4:21])
highlyCorPred <- findCorrelation(predCor1, cutoff = 0.75)


###################################
# MEAN MODEL - AVAILABLE AT GLOBO
###################################

avgData <- train[,c("atletas.atleta_id","outcome")]
avgDataTest <- test[,c("atletas.atleta_id","outcome")]

avgData <- tbl_df(avgData)
avgDataTest <- tbl_df(avgDataTest)
avgData <- avgData %>% group_by(atletas.atleta_id) %>% summarise(avg = mean(outcome))

meanModel <- left_join(avgData, avgDataTest, by = "atletas.atleta_id")
meanModel <- filter(meanModel, outcome != 0)

cor(meanModel$avg, meanModel$outcome, use = "complete.obs", method = "kendall")
RMSE(meanModel$avg, meanModel$outcome, na.rm = TRUE)

ggplot(meanModel, aes(avg, outcome)) + geom_point()

# Remove atletas.apelido variable
train <- train[, -1]
test <-  test[, -1]


###################################
# BLACKBOX - RANDOM FOREST
###################################
cluster <- makeCluster(detectCores())
registerDoParallel(cluster)
fit.raf <- train(outcome~.,
                 data=train,
                 method="rf",
                 preProcess=c("center","scale"),
                 tunelength=15,
                 tuneGrid = rfGrid,
                 trControl=ctrl,
                 ntree = 1000,
                 metric="RMSE"
)
stopCluster(cluster)

###################
# GLM
###################
glmModel_0  <- train(outcome ~ ., data = train, 
                     method="glm", metric = "RMSE", preProcess = c("scale", "center"),
                     trControl = ctrl)
glmModel_0

###################
# Partial Least Square
###################
pls_0  <- train(outcome ~ ., data = train, 
                     method="pls", metric = "RMSE", preProcess = c("scale", "center"),
                     trControl = ctrl, tuneLength = 20)
pls_0

###################
# LASSO
###################
lassoModel_0  <- train(outcome ~ ., data = train, 
                     method="lasso", metric = "RMSE", preProcess = c("scale", "center"),
                     trControl = ctrl)

###################
# GBM
###################
boostModel  <- train(outcome ~ . , data = train, 
                     method="gbm", metric = "RMSE", 
                     preProcess = c("center","scale"),
                     trControl = ctrl)



###################
# COMPARE MODELS
###################

models <- list(lasso = lassoModel_0, glm = glmModel_0, gbm = boostModel)

predictions_lasso <- predict(lassoModel_0, test)
RMSE(predictions_lasso, test$outcome)
R2(predictions_lasso, test$outcome)

predictions_glm <- predict(glmModel_0, test)
RMSE(predictions_glm, test$outcome)
R2(predictions_glm, test$outcome)


predictions_gbm <- predict(boostModel, test)
RMSE(predictions_gbm, test$outcome)
R2(predictions_gbm, test$outcome)

results <- resamples(models)
summary(results)
bwplot(results)
dotplot(results)

summary(test$outcome)
summary(predictions_glm)
summary(predictions_lasso)
summary(predictions_gbm)

plot(predictions_gbm, test$outcome)

#####################################
## GROUP 2 - Time Series Analysis
#####################################

cartola_2016 <- tbl_df(cartola_2016)
cartola_2016 <- arrange(cartola_2016, atletas.apelido, atletas.rodada_id)

ids <- unique(cartola_2016$atletas.atleta_id)
predictions <- data.frame(id = ids, prediction = NA, avg = NA, naive = NA, drift = NA, acForecast = NA, acMean = NA, acnaiveModel = NA, acDriftModel = NA)

for (i in 1: length(ids)){
  atleta <- filter(cartola_2016, atletas.atleta_id == ids[i])
  myTs <- ts(atleta$atletas.pontos_num, start = min(atleta$atletas.rodada_id), end = max(atleta$atletas.rodada_id), frequency = 1)
  etsfit <- ets(myTs)
  fcast <- forecast(etsfit, h = 1)
  predictions$prediction[i] <- fcast$mean
  meanModel <- meanf(myTs, h = 1)
  predictions$avg[i] <- meanModel$mean
  acnaiveModel <- naive(myTs, h = 1)
  predictions$naive[i] <- acnaiveModel$mean
  driftModel <- rwf(myTs, drift = TRUE, h = 1)
  predictions$drift[i] <- driftModel$mean
  
  # Predictions values
  predictions$acForecast[i] <- accuracy(fcast)[2]
  predictions$acMean[i] <- accuracy(meanModel)[2]
  predictions$acnaiveModel[i] <- accuracy(acnaiveModel)[2]
  predictions$acDriftModel[i] <- accuracy(driftModel)[2]
}

rm(driftModel, etsfit, fcast, i, ids, meanModel, myTs, acnaiveModel)

#####################################
## GROUP 3 - Wide Data
#####################################

# cartola_2016 <- cartola_2016 %>% group_by(atletas.apelido) %>% mutate(l_outcome = lag(atletas.pontos_num))

# --------------------------
# INDIVIDUAL PLAYER ANALYSIS
# --------------------------


playerData <- scores[, c("atletas.rodada_id","atletas.apelido","atletas.pontos_num","atletas.posicao_id","PPP")]
playerData <- playerData[order(playerData$atletas.apelido, playerData$atletas.rodada_id), ]
playerDataMelted <- melt(playerData, id.vars=c("atletas.rodada_id","atletas.apelido","atletas.posicao_id"), measure.vars = "atletas.pontos_num", value.name = "Pontos")  

# Forwards
ggplot(data=subset(playerDataMelted, atletas.posicao_id %in% "ata"), 
       aes(x=atletas.rodada_id, y=Pontos, colour=atletas.apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Midfielders
ggplot(data=subset(playerDataMelted, atletas.posicao_id %in% "mei"), 
       aes(x=atletas.rodada_id, y=Pontos, colour=atletas.apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Defenders
ggplot(data=subset(playerDataMelted, atletas.posicao_id %in% "zag"), 
       aes(x=atletas.rodada_id, y=Pontos, colour=atletas.apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Wingers
ggplot(data=subset(playerDataMelted, atletas.posicao_id %in% "lat"), 
       aes(x=atletas.rodada_id, y=Pontos, colour=atletas.apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Head Coaches
ggplot(data=subset(playerDataMelted, atletas.posicao_id %in% "tec"), 
       aes(x=atletas.rodada_id, y=Pontos, colour=atletas.apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# GKs
ggplot(data=subset(playerDataMelted, atletas.posicao_id %in% "gol"), 
       aes(x=atletas.rodada_id, y=Pontos, colour=atletas.apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")
  
# Multiple predictors
melt.scores <- melt(scores)
ggplot(data = melt.scores, aes(x = value)) +
  stat_density() +
  facet_wrap(~variable, scales = "free")

# ...

ggplot(melt.scores, aes(x = value)) + geom_point() + facet_grid(.)



##########################
## SELECT PLAYERS ##
##########################

playerPrediction <- read.csv("rodada-11.csv", stringsAsFactors = FALSE)
playerPrediction <- playerPrediction[, -c(1,2,4,6,12,13)]
playerPrediction <- subset(playerPrediction, playerPrediction$atletas.status_id == "Provável" & playerPrediction$atletas.jogos_num >= 7)

playerPrediction <- merge(playerPrediction, predictions, by.x = "atletas.atleta_id", by.y = "id")

lista1 <- playerPrediction[, c("atletas.apelido","atletas.clube_id","atletas.posicao_id","atletas.preco_num","atletas.pontos_num","atletas.jogos_num","prediction","acForecast")]

GK <- subset(lista1, atletas.posicao_id == "gol")
defenders <- subset(lista1, atletas.posicao_id == "zag")
lateral <- subset(lista1, atletas.posicao_id == "lat")
mid <- subset(lista1, atletas.posicao_id == "mei")
strikers <- subset(lista1, atletas.posicao_id == "ata")
coach <- subset(lista1, atletas.posicao_id == "tec")

# Print list of athletes
head(arrange(GK, desc(acForecast)),10)
head(arrange(defenders, desc(acForecast)),20)
head(arrange(lateral, desc(acForecast)),15)
head(arrange(mid, desc(acForecast)),20)
head(arrange(strikers, desc(acForecast)),25)
head(arrange(coach, desc(acForecast)),25)


#-------------------
## GA Selection ----
#-------------------

library(genalg)

pontosCartola <- 90

chromosome <-  as.vector(c(rep(1,12), rep(0, (nrow(lista1)-12))))

lista1[chromosome == 1, ]

cat(chromosome %*% lista1$acForecast)

evalFunc <- function(x) {
  current_solution_acForecast <- x %*% lista1$acForecast
  current_solution_weight <- x %*% lista1$atletas.preco_num
  
  if (current_solution_weight > pontosCartola) 
    return(0) else return(-current_solution_acForecast)
}

iter = 100
GAmodel <- rbga.bin(size = 138, popSize = 200, iters = iter, mutationChance = 0.01, 
                    elitism = T, evalFunc = evalFunc)

cat(summary(GAmodel))


solution = c(1, 1, 1, 1, 1, 0, 1)
dataset[solution == 1, ]
GAmodel$population

# solution vs available
cat(paste(solution %*% dataset$survivalpoints, "/", sum(dataset$survivalpoints)))





### BIN ####

cartola_Wide$CA_01 <- lag(cartola_Wide$CA.2)
cartola_Wide$CA_02 <- lag(cartola_Wide$CA.3,1)
cartola_Wide$CA_03 <- lag(cartola_Wide$CA.4,2)
cartola_Wide$CA_04 <- lag(cartola_Wide$CA.5,3)
cartola_Wide$CA_05 <- lag(cartola_Wide$CA.6,4)

cartola_Wide$FC_01 <- lag(cartola_Wide$FC.2)
cartola_Wide$FC_02 <- lag(cartola_Wide$FC.3,1)
cartola_Wide$FC_03 <- lag(cartola_Wide$FC.4,2)
cartola_Wide$FC_04 <- lag(cartola_Wide$FC.5,3)
cartola_Wide$FC_05 <- lag(cartola_Wide$FC.6,4)

cartola_Wide$FD_01 <- lag(cartola_Wide$FD.2)
cartola_Wide$FD_02 <- lag(cartola_Wide$FD.3,1)
cartola_Wide$FD_03 <- lag(cartola_Wide$FD.4,2)
cartola_Wide$FD_04 <- lag(cartola_Wide$FD.5,3)
cartola_Wide$FD_05 <- lag(cartola_Wide$FD.6,4)

cartola_Wide$FS_01 <- lag(cartola_Wide$FS.2)
cartola_Wide$FS_02 <- lag(cartola_Wide$FS.3,1)
cartola_Wide$FS_03 <- lag(cartola_Wide$FS.4,2)
cartola_Wide$FS_04 <- lag(cartola_Wide$FS.5,3)
cartola_Wide$FS_05 <- lag(cartola_Wide$FS.6,4)

cartola_Wide$PE_01 <- lag(cartola_Wide$PE.2)
cartola_Wide$PE_02 <- lag(cartola_Wide$PE.3,1)
cartola_Wide$PE_03 <- lag(cartola_Wide$PE.4,2)
cartola_Wide$PE_04 <- lag(cartola_Wide$PE.5,3)
cartola_Wide$PE_05 <- lag(cartola_Wide$PE.6,4)

cartola_Wide$RB_01 <- lag(cartola_Wide$RB.2)
cartola_Wide$RB_02 <- lag(cartola_Wide$RB.3,1)
cartola_Wide$RB_03 <- lag(cartola_Wide$RB.4,2)
cartola_Wide$RB_04 <- lag(cartola_Wide$RB.5,3)
cartola_Wide$RB_05 <- lag(cartola_Wide$RB.6,4)

cartola_Wide$SG_01 <- lag(cartola_Wide$SG.2)
cartola_Wide$SG_02 <- lag(cartola_Wide$SG.3,1)
cartola_Wide$SG_03 <- lag(cartola_Wide$SG.4,2)
cartola_Wide$SG_04 <- lag(cartola_Wide$SG.5,3)
cartola_Wide$SG_05 <- lag(cartola_Wide$SG.6,4)

cartola_Wide$FF_01 <- lag(cartola_Wide$FF.2)
cartola_Wide$FF_02 <- lag(cartola_Wide$FF.3,1)
cartola_Wide$FF_03 <- lag(cartola_Wide$FF.4,2)
cartola_Wide$FF_04 <- lag(cartola_Wide$FF.5,3)
cartola_Wide$FF_05 <- lag(cartola_Wide$FF.6,4)

cartola_Wide$I_01 <- lag(cartola_Wide$I.2)
cartola_Wide$I_02 <- lag(cartola_Wide$I.3,1)
cartola_Wide$I_03 <- lag(cartola_Wide$I.4,2)
cartola_Wide$I_04 <- lag(cartola_Wide$I.5,3)
cartola_Wide$I_05 <- lag(cartola_Wide$I.6,4)

cartola_Wide$A_01 <- lag(cartola_Wide$A.2)
cartola_Wide$A_02 <- lag(cartola_Wide$A.3,1)
cartola_Wide$A_03 <- lag(cartola_Wide$A.4,2)
cartola_Wide$A_04 <- lag(cartola_Wide$A.5,3)
cartola_Wide$A_05 <- lag(cartola_Wide$A.6,4)

cartola_Wide$DD_01 <- lag(cartola_Wide$DD.2)
cartola_Wide$DD_02 <- lag(cartola_Wide$DD.3,1)
cartola_Wide$DD_03 <- lag(cartola_Wide$DD.4,2)
cartola_Wide$DD_04 <- lag(cartola_Wide$DD.5,3)
cartola_Wide$DD_05 <- lag(cartola_Wide$DD.6,4)

cartola_Wide$GS_01 <- lag(cartola_Wide$GS.2)
cartola_Wide$GS_02 <- lag(cartola_Wide$GS.3,1)
cartola_Wide$GS_03 <- lag(cartola_Wide$GS.4,2)
cartola_Wide$GS_04 <- lag(cartola_Wide$GS.5,3)
cartola_Wide$GS_05 <- lag(cartola_Wide$GS.6,4)

cartola_Wide$G_01 <- lag(cartola_Wide$G.2)
cartola_Wide$G_02 <- lag(cartola_Wide$G.3,1)
cartola_Wide$G_03 <- lag(cartola_Wide$G.4,2)
cartola_Wide$G_04 <- lag(cartola_Wide$G.5,3)
cartola_Wide$G_05 <- lag(cartola_Wide$G.6,4)

cartola_Wide$PP_01 <- lag(cartola_Wide$PP.2)
cartola_Wide$PP_02 <- lag(cartola_Wide$PP.3,1)
cartola_Wide$PP_03 <- lag(cartola_Wide$PP.4,2)
cartola_Wide$PP_04 <- lag(cartola_Wide$PP.5,3)
cartola_Wide$PP_05 <- lag(cartola_Wide$PP.6,4)

cartola_Wide$FT_01 <- lag(cartola_Wide$FT.2)
cartola_Wide$FT_02 <- lag(cartola_Wide$FT.3,1)
cartola_Wide$FT_03 <- lag(cartola_Wide$FT.4,2)
cartola_Wide$FT_04 <- lag(cartola_Wide$FT.5,3)
cartola_Wide$FT_05 <- lag(cartola_Wide$FT.6,4)

cartola_Wide$CV_01 <- lag(cartola_Wide$CV.2)
cartola_Wide$CV_02 <- lag(cartola_Wide$CV.3,1)
cartola_Wide$CV_03 <- lag(cartola_Wide$CV.4,2)
cartola_Wide$CV_04 <- lag(cartola_Wide$CV.5,3)
cartola_Wide$CV_05 <- lag(cartola_Wide$CV.6,4)

cartola_Wide$DP_01 <- lag(cartola_Wide$DP.2)
cartola_Wide$DP_02 <- lag(cartola_Wide$DP.3,1)
cartola_Wide$DP_03 <- lag(cartola_Wide$DP.4,2)
cartola_Wide$DP_04 <- lag(cartola_Wide$DP.5,3)
cartola_Wide$DP_05 <- lag(cartola_Wide$DP.6,4)

cartola_Wide$GC_01 <- lag(cartola_Wide$GC.2)
cartola_Wide$GC_02 <- lag(cartola_Wide$GC.3,1)
cartola_Wide$GC_03 <- lag(cartola_Wide$GC.4,2)
cartola_Wide$GC_04 <- lag(cartola_Wide$GC.5,3)
cartola_Wide$GC_05 <- lag(cartola_Wide$GC.6,4)

cartola_Wide$outcome <- lag(cartola_Wide$atletas.pontos_num.2)
cartola_Wide$outcome_02 <- lag(cartola_Wide$atletas.pontos_num.3,1)
cartola_Wide$outcome_03 <- lag(cartola_Wide$atletas.pontos_num.4,2)
cartola_Wide$outcome_04 <- lag(cartola_Wide$atletas.pontos_num.5,3)
cartola_Wide$outcome_05 <- lag(cartola_Wide$atletas.pontos_num.6,4)

