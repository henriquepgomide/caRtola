# What? ----------------------------------------------
# Retrieve data from cartola 2018  and store data into
# data/2018 folder
# ----------------------------------------------------
library(plyr)
library(tidyverse)

# Return a single dataframe from a list of dataframes imported as xls files
aggregateCsv <- function(files){
  for (i in 1:length(files)){
    data         <- read.csv(files[i], stringsAsFactors = FALSE)
    df_list[[i]] <- data
  }
  
  df <- ldply(df_list, data.frame)
  return(df)
}

fixEncodingIssues <- function(vector){
  vector <- gsub("<e1>", "á", vector)
  vector <- gsub("<e3>", "ã", vector)
  vector <- gsub("<e2>", "ã", vector)
  vector <- gsub("<c1>", "Á", vector)
  vector <- gsub("<c2>", "Â", vector)
  vector <- gsub("<e9>", "é", vector)
  vector <- gsub("<ea>", "ê", vector)
  vector <- gsub("<ed>", "í", vector)
  vector <- gsub("<f3>", "ó", vector)
  vector <- gsub("<f4>", "ô", vector)
  vector <- gsub("<e7>", "ç", vector)
  vector <- gsub("<fa>", "ú", vector)
  vector <- gsub("<f1>", "ñ", vector)
  vector <- gsub("<c9>", "É", vector)
  vector <- gsub("<cd>", "Í", vector)

  return(vector)
}

# Read all round data for the year of 2018
setwd("~/caRtola/data/2018/")
df_list <- list()
files   <- list.files(pattern = "rodada-*.*csv")
data    <- aggregateCsv(files)

# Fix weird characters
data$atletas.nome <- fixEncodingIssues(data$atletas.nome)
data$atletas.clube.id.full.name <- fixEncodingIssues(data$atletas.clube.id.full.name)

# Fix photos
data$atletas.foto <- gsub("FORMATO", "140x140", data$atletas.foto)

# Write 2018_jogadores.csv
players <- 
  data %>%
  dplyr::distinct(atletas.atleta_id, .keep_all = TRUE) %>%
  dplyr::select(atletas.atleta_id, atletas.apelido, atletas.clube.id.full.name, atletas.posicao_id, atletas.foto)

# Convert id.full.name and posicao_id to cartola codes
temp1 <- read.csv("~/caRtola/data/times_ids.csv", stringsAsFactors = FALSE)
temp2 <- read.csv("~/caRtola/data/posicoes_ids.csv", stringsAsFactors = FALSE)

# players$atletas.clube.id.full.name <- plyr::mapvalues(players$atletas.clube.id.full.name, 
#                                                       from = as.vector(temp1$nome.cartola), 
#                                                       to   = as.vector(temp1$id), warn_missing = FALSE)

players$atletas.posicao_id        <- plyr::mapvalues(players$atletas.posicao_id, 
                                                     from = as.vector(temp2$abbr), 
                                                     to   = as.vector(temp2$Position), warn_missing = FALSE)

write.csv(players, "2018_jogadores.csv", row.names = FALSE)
