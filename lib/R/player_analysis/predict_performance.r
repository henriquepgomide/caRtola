# Load libraries
# Carregar pacotes
library(caret)
library(dplyr)
library(parallel)
library(doParallel)

#%%%%%%%%%%%%%%%%%%%%%%%%%
# Subset Data Frame
#%%%%%%%%%%%%%%%%%%%%%%%%%
source("lib/R/merge_all_years.R")

# Remove cases with no data
cartola <- subset(cartola, cartola$Participou == TRUE | cartola$PrecoVariacao != 0)

treino <- cartola %>%
  filter(!(Rodada < 12 & ano != 2017))

validacao <- cartola %>%
  filter(Rodada == 12 & ano == 2017)

validacao <- validacao[complete.cases(validacao), ]

# Selecionar somente algumas variáveis
variaveis <- c("ClubeID", "Posicao", "media", "roll.media", "Pontos", "PontosMedia", "pred.home.score", "pred.away.score", "home.attack", "home.defend", "variable")

treino <- treino[, variaveis]
validacao <-  validacao[, variaveis]

# Controles para os modelos
## Regression Models
ctrl <- trainControl(method = "repeatedcv", number = 10, repeats = 10, allowParallel = TRUE, verboseIter = TRUE)
rfGrid <-  expand.grid(mtry = c(10,20,40,80))  

########### 
# Modeling
###########

###################
# GLM
###################
glmModel_0  <- train(Pontos ~ ., data = treino, 
                     method="glm", metric = "RMSE", preProcess = c("scale", "center"), na.action = na.pass,
                     trControl = ctrl)
glmModel_0

###################
# Partial Least Square
###################
pls_0  <- train(Pontos ~ ., data = treino,
                method="pls", metric = "RMSE", preProcess = c("scale", "center"), na.action = na.pass,
                trControl = ctrl, tuneLength = 20)
pls_0


###################################
# BLACKBOX - RANDOM FOREST
###################################
cluster <- makeCluster(detectCores())
registerDoParallel(cluster)
fit.raf <- train(Pontos ~.,
                 data=treino,
                 method="rf",
                 preProcess=c("center","scale"),
                 tunelength=15,
                 tuneGrid = rfGrid,
                 trControl=ctrl,
                 ntree = 1000,
                 metric="RMSE",
                 na.action = na.omit
)
stopCluster(cluster)

###################
# GBM
###################
boostModel  <- train(Pontos ~ ., data = treino,
                     method="gbm", metric = "RMSE", 
                     preProcess = c("scale", "center"), na.action = na.pass,
                     trControl = ctrl)


###################
# Neural Networks
###################
nnModel  <- train(Pontos ~ ., data = treino,
                     method="nnet", metric = "RMSE", 
                     preProcess = c("scale", "center"), na.action = na.pass,
                     trControl = ctrl)

###################
# eXtreme G Boosting
###################
eXModel  <- train(Pontos ~ . , data = treino, 
                  method="xgbTree", metric = "RMSE", 
                  preProcess = c("scale", "center"), na.action = na.pass,
                  trControl = ctrl)


###################
# COMPARE MODELS
###################

models <- list(eXB = eXModel, glm = glmModel_0, NeurN = nnModel, GBM = boostModel, 
               RF = fit.raf)

results <- resamples(models)
summary(results)
bwplot(results)
dotplot(results)

predictions_glm <- predict(glmModel_0, newdata = validacao)
postResample(pred = predictions_glm, obs = validacao$Pontos)

predictions_exb <- predict(eXModel, newdata = validacao)
postResample(pred = predictions_exb, obs = validacao$Pontos)

predictions_nn <- predict(nnModel, newdata = validacao)
postResample(pred = predictions_nn, obs = validacao$Pontos)

predictions_gbm <- predict(boostModel, newdata = validacao)
postResample(pred = predictions_gbm, obs = validacao$Pontos)

predictions_rf <- predict(fit.raf, newdata = validacao)
postResample(pred = predictions_rf, obs = validacao$Pontos)


summary(valicado$Pontos)
summary(predictions_glm)
summary(predictions_lasso)
summary(predictions_gbm)

