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

# Read all round data for the year of 2018
setwd("~/caRtola/data/2018/")
df_list <- list()
files   <- list.files(pattern = "rodada-*.*csv")
data    <- aggregateCsv(files)

# Write 2018_jogadores.csv
players <- 
  data %>%
  distinct(atletas.atleta_id, .keep_all = TRUE) %>%
  select(atletas.atleta_id, atletas.apelido, atletas.clube.id.full.name, atletas.posicao_id)

# Convert id.full.name and posicao_id to cartola codes
temp1 <- read.csv("~/caRtola/data/times_ids.csv", stringsAsFactors = FALSE)
temp2 <- read.csv("~/caRtola/data/posicoes_ids.csv", stringsAsFactors = FALSE)

players$atletas.clube.id.full.name <- plyr::mapvalues(players$atletas.clube.id.full.name, 
                                                      from = as.vector(temp1$nome.cartola), 
                                                      to   = as.vector(temp1$id), warn_missing = FALSE)

players$atletas.posicao_id        <- plyr::mapvalues(players$atletas.posicao_id, 
                                                     from = as.vector(temp2$abbr), 
                                                     to   = as.vector(temp2$Cod), warn_missing = FALSE)

write.csv(players, "2018_jogadores.csv", row.names = FALSE)
