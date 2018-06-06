#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# DATA WRANGLING ----
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 1. Merge data from different rounds                   
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# This function merges data from different rounds and merge them into
# a single data.frame for a given year.

merge_cartola_data <- function(year){
  year <- as.character(year)
  require(dplyr)
  setwd(paste0("data/", year))
  files <- list.files(pattern = "rodada")
  
  list_of_data_frames <- lapply(files, function(x){
    read.csv(x, header = TRUE, stringsAsFactors = FALSE)
  })
  
  df <- do.call(bind_rows, list_of_data_frames)
  return(df)
}

# Let's open 2018's data
cartola <- merge_cartola_data(2018)
setwd("../../")

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 2. Wrangle scouts from Cartola API, aggregated format  ----
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## Carregar pacotes
library(dplyr)
library(tidyr)

# Sort data by id and round 
cartola <- 
  cartola %>%
  arrange(atletas.atleta_id, - atletas.rodada_id)

df <- cartola

# Create a data.frame to manipulate scouts
df <- df[, c(6,16:31)]

# Convert NA values into zeroes
df[,2:17] <- sapply(df[,2:17], function(x) ifelse(is.na(x), 0, x))

df <- df %>%
      group_by(atletas.atleta_id) %>%
      mutate_all(funs(abs(diff(c(.,0)))))

df$atletas.rodada_id <- cartola$atletas.rodada_id

# Remove aggregated scouts statistics
cartola <- cartola[, -c(16:33)]

# Join with proper scouts
df <- left_join(df, cartola, by = c("atletas.atleta_id", "atletas.rodada_id"))

# Arrange variable columns
df <- df[, c(1, 18, 20:31, 2:17)]

cartola <- df
rm(df)
