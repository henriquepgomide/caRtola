# What does this code do?
# It runs multiple models to predict scores for the next Cartola round.

# O que esse script faz?
# Você rodará vários modelos para tentar predizer a próxima rodada do cartola.
# Ele é muito experimental. Vários modelos *demoram* tempo para convergir e parte do código pode estar quebrada.
# Uai, cadê o banco de dados? O banco de dados é gerado a partir da execução do script 'merge_all_years.R'. Leia os comentários do script para gerá-lo.

# Set the last cartola round
# Definir a rodada que quer prever
round <- 33

# Load libraries
# Carregar pacotes
library(caret)
library(dplyr)
library(parallel)
library(doParallel)


#%%%%%%%%%%%%%%%%%%%%%%%%%
# Subset Data Frame
#%%%%%%%%%%%%%%%%%%%%%%%%%
# source("lib/R/merge_all_years.R")

# Remove cases with no data
# Remover casos de jogadores que não participaram de partidas
df <- subset(cartola, cartola$Participou == TRUE | cartola$PrecoVariacao != 0)

# Pick only a subset of variables
# Selecionar somente variáveis que são candidatas a preditores
variaveis <- c(2, 3, 5, 7, 8, 29, 32:67, 73:77)
df <- df[, variaveis]

# Remove nearzero variance predictors
# Remover preditores com pouca informação
nzv <- nearZeroVar(df)
df <- df[, -nzv]

# Split training and validation
# Separar banco de dados de treino e validação
treino <- df %>%
  filter(!(Rodada == (round - 1) & ano == 2017))

validacao <- df %>%
  filter(Rodada == (round - 1) & ano == 2017)

# Selecionar somente resultados completos para validação
validacao <- validacao[complete.cases(validacao), ]

# Controles para os modelos
# Definir uma semente para garantir replicabilidade dos resultados
set.seed(123)
## Regression Models
ctrl <- trainControl(method = "repeatedcv", number = 10, allowParallel = TRUE, verboseIter = TRUE)
rfGrid <-  expand.grid(mtry = c(8))
rfGrid_1 <-  expand.grid(mtry = c(5:15))
rfGrid_2 <-  expand.grid(mtry = c(10,15,20,25,30))
rfGrid_final <-  expand.grid(mtry = 30)
eXGBGrid <-  expand.grid(nrounds = 150, 
                         max_depth = c(3:5),
                         colsample_bytree = .8,
                         eta = .4,
                         subsample = .8, 
                         gamma = 0,
                         min_child_weight = 1
                         )

########### 
# Modeling
###########

###################
# Baseline
###################
glmModel_0  <- train(Pontos ~ PontosMedia, data = treino, 
                     method="glm", metric = "RMSE", preProcess = c("scale", "center"), na.action = na.pass,
                     trControl = ctrl)
glmModel_0

###################
# GLM
###################
glmModel_1  <- train(Pontos ~ ., data = treino, 
                     method="glm", metric = "RMSE", preProcess = c("scale", "center"), na.action = na.pass,
                     trControl = ctrl)
glmModel_1

###################
# Partial Least Square
###################
pls_0  <- train(Pontos ~ ., data = treino,
                method="pls", metric = "RMSE", preProcess = c("scale", "center"), na.action = na.pass,
                trControl = ctrl, tuneLength = 20)
pls_0


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

# Tune model with better parameters based on prior experience
eXModel_v1  <- train(Pontos ~ . , data = treino, 
                  method="xgbTree", metric = "RMSE", 
                  preProcess = c("scale", "center"), na.action = na.pass,
                  tuneGrid = eXGBGrid, trControl = ctrl)

# Transform data to deal with outliers before running model
eXModel_v1_out  <- train(Pontos ~ . , data = treino, 
                     method="xgbTree", metric = "RMSE", 
                     preProcess = c("scale", "center", "spatialSign"), na.action = na.omit,
                     tuneGrid = eXGBGrid, trControl = ctrl)


###################
# SVM
###################
svmModel  <- train(Pontos ~ . , data = treino, 
                  method="svmRadial", metric = "RMSE", 
                  preProcess = c("scale", "center"), na.action = na.pass,
                  trControl = ctrl)

###################################
# RANDOM FOREST
###################################
ptm <- proc.time()
fit.raf_1 <- train(Pontos ~.,
                 data=treino,
                 method="ranger",
                 preProcess=c("center","scale"),
                 tuneGrid = rfGrid_1,
                 trControl=ctrl,
                 metric="RMSE",
                 na.action = na.omit,
                 verbose = TRUE
)
proc.time() - ptm

ptm <- proc.time()
modellist <- list()
for (ntree in c(1000,1500,2000)) {
  fit.raf_2 <- train(Pontos ~.,
                     data=treino,
                     method="ranger",
                     preProcess=c("center","scale"),
                     tuneGrid = rfGrid_2,
                     trControl=ctrl,
                     metric="RMSE",
                     na.action = na.omit,
                     verbose = TRUE)
  key <- toString(ntree)
  modellist[[key]] <- fit.raf_2
}
proc.time() - ptm

fit.raf_final <- train(Pontos ~.,
                   data=treino,
                   method="ranger",
                   preProcess=c("center","scale"),
                   tuneGrid = rfGrid_final,
                   trControl=ctrl,
                   metric="RMSE",
                   na.action = na.omit,
                   verbose = TRUE
)

fit.raf_f_out <- train(Pontos ~.,
                       data=treino,
                       method="ranger",
                       preProcess=c("center","scale", "spatialSign"),
                       tuneGrid = rfGrid_final,
                       trControl=ctrl,
                       metric="RMSE",
                       na.action = na.omit,
                       verbose = TRUE
)

#stopCluster(cluster)

###################
# COMPARE MODELS
###################

# Random Forest models
rf_results <- resamples(modellist)
summary(rf_results)
# From this model we can assume the number of tree is equal to 1000, mtry = 30, RMSE = 3.05.

models <- list(eXB = eXModel, glm = glmModel_0, pls = pls_0, NeurN = nnModel, GBM = boostModel, 
               SVM = svmModel)

predictions_rf <- predict(fit.raf, newdata = validacao)
postResample(pred = predictions_rf, obs = validacao$Pontos)

predictions_raf_1 <- predict(fit.raf_1, newdata = validacao)
postResample(pred = predictions_raf_1, obs = validacao$Pontos)

predictions_raf_2 <- predict(modellist[[1]], newdata = validacao)
postResample(pred = predictions_raf_2, obs = validacao$Pontos)

predictions_rf_final <- predict(fit.raf_final, newdata = validacao)
postResample(pred = predictions_rf_final, obs = validacao$Pontos)


# Other models
results <- resamples(models)
summary(results)
bwplot(results)
dotplot(results)

predictions_glm <- predict(glmModel_0, newdata = validacao)
postResample(pred = predictions_glm, obs = validacao$Pontos)

predictions_pls <- predict(pls_0, newdata = validacao)
postResample(pred = predictions_pls, obs = validacao$Pontos)

predictions_exb <- predict(eXModel, newdata = validacao)
postResample(pred = predictions_exb, obs = validacao$Pontos)

predictions_nn <- predict(nnModel, newdata = validacao)
postResample(pred = predictions_nn, obs = validacao$Pontos)

predictions_gbm <- predict(boostModel, newdata = validacao)
postResample(pred = predictions_gbm, obs = validacao$Pontos)

predictions_svm <- predict(svmModel, newdata = validacao)
postResample(pred = predictions_svm, obs = validacao$Pontos)

# Best EGB Models
predictions_exb1 <- predict(eXModel_v1, newdata = validacao)
postResample(pred = predictions_exb1, obs = validacao$Pontos)

predictions_exb1_out <- predict(eXModel_v1_out, newdata = validacao)
postResample(pred = predictions_exb1_out, obs = validacao$Pontos)

summary(validacao$Pontos)
summary(predictions_glm)
summary(predictions_pls)
summary(predictions_exb1)
summary(predictions_rf_final)
summary(predictions_nn)
summary(predictions_gbm)
summary(predictions_svm)

# Remove home.score and away.score variables
df_pred_r <- df_pred
df_pred_r2 <- df_pred_r[complete.cases(df_pred_r), ]

# Create predictions based on specific model
df_pred_r2$next_round <- predict(eXModel_v1_out, df_pred_r2)
df_pred_r2 <- arrange(df_pred_r2, - next_round)

# Subset by position
ata <- subset(df_pred_r2, df_pred_r2$Posicao == "ata")
mei <- subset(df_pred_r2, df_pred_r2$Posicao == "mei")
zag <- subset(df_pred_r2, df_pred_r2$Posicao == "zag")
lat <- subset(df_pred_r2, df_pred_r2$Posicao == "lat")
gol <- subset(df_pred_r2, df_pred_r2$Posicao == "gol")
tec <- subset(df_pred_r2, df_pred_r2$Posicao == "tec")

# Write predictions as csv
write.csv(df_pred_r2[, c("Apelido","ClubeID","Posicao", "Preco", "risk_points", "next_round", "pred.home.score", "pred.away.score", "variable")], "~/rodada22.csv", row.names = FALSE)

# Create tables to select players
ata[,c("Apelido","ClubeID","Posicao", "Preco", "risk_points", "next_round", "pred.home.score", "pred.away.score", "variable")]
