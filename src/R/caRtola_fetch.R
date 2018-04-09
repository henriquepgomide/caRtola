# What? ----------------------------------------------
# Retrieve data from Cartola and store as a csv file
# Every round, you need to gather and store data into
# data/2018 folder
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Recuperar os dados da API do cartola e salvar num
# em csv. Toda rodada, é necessário executar
# o script. Os dados são armazenados em um arquivo
# csv na pasta data/2018.
# ----------------------------------------------------

# Remind yourself to install packages before loading them
# Lembre-se de instalar os pacotes abaixo antes de carregá-los

# Load Libraries
# Carregar pacotes R
library(httr)
library(rjson)
library(jsonlite)
library(plyr)

###################
# Fetch Player Data 
# Recuperar dados da API
###################

json_athletes <- "https://api.cartolafc.globo.com/atletas/mercado"
athletes <- fromJSON(paste(readLines(json_athletes), collapse="")) # Get data from Cartola API
df_1 <- data.frame(athletes[1]) # Convert List format into DataFrame
df_1 <- df_1[, 1:13] # Select useful vars

# Label variable atletas.posicao_id 
df_3 <- athletes$posicoes
temp1 <- t(matrix(unlist(df_3),3,6))
temp1 <- data.frame(temp1, stringsAsFactors = FALSE)
colnames(temp1) <- c("Cod", "Position", "abbr")
temp1$Cod <- as.integer(temp1$Cod)
df_1$atletas.posicao_id <- mapvalues(df_1$atletas.posicao_id, from = as.vector(temp1$Cod), to = as.vector(temp1$abbr))
rm(temp1)

# Label variable 
df_3 <- athletes$status
temp1 <- t(matrix(unlist(df_3),2,5))
temp1 <- data.frame(temp1, stringsAsFactors = FALSE)
colnames(temp1) <- c("Cod", "status")
temp1$Cod <- as.integer(temp1$Cod)
df_1$atletas.status_id <- mapvalues(df_1$atletas.status_id, from = as.vector(temp1$Cod), to = as.vector(temp1$status))
rm(temp1)

# Label team
teams <- athletes[2]
temp1 <- t(matrix(unlist(teams),7,20))
temp1 <- data.frame(temp1, stringsAsFactors = FALSE)
temp1 <- temp1[,1:4]
colnames(temp1) <- c("Cod", "nome.completo","nome","pos")
temp1$Cod <- as.integer(temp1$Cod)
df_1$atletas.clube.id.full.name <- mapvalues(df_1$atletas.clube_id, from = as.vector(temp1$Cod), to = as.vector(temp1$nome.completo))
df_1$atletas.clube_id <- mapvalues(df_1$atletas.clube_id, from = as.vector(temp1$Cod), to = as.vector(temp1$nome))
rm(teams);rm(temp1)

# Merge detailed scouts into df_1
df_2 <- athletes$atletas$scout
df_1 <- cbind(df_1, athletes$atletas$scout)
rm(df_2,df_3, athletes, json_athletes)

# Store data frame
write.csv(df_1, paste0("data/2018/rodada-", df_1$atletas.rodada_id[1],".csv"))
rm(df_1)
