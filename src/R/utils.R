library(plyr)
library(tidyverse)
library(zoo)

readCsvInsideFolder <- function(path,
                                pattern,
                                year){
  # Return a single dataframe from a list of dataframes imported as xls files
  files <- list.files(path = path, pattern = pattern)
  df_list <- list()
  
  for (i in 1:length(files)){
    data         <- read.csv(paste0("data/", year, "/", files[i]), stringsAsFactors = FALSE)
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
