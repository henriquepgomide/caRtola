# What? ----------------------------------------------
# This script is intended to merge all rounds for a given year 
# into a single csv file
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Este script tem como objetivo combinar todos arquivos
# das estatísticas individuais dos jogadores para uma
# dada temporada
# ----------------------------------------------------

# Para usar esta função, você precisa definir o diretório de trabalho como .."caRtola"
# Em Unix, caso tenho baixado o repositório na sua pasta pessoal, use: 
# setwd("~/caRtola")

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

# Para usar a função, escolha o ano. No exemplo abaixo, escolhemos 2017.
cartola <- merge_cartola_data(2017)
