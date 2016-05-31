# Libraries
library(httr)
library(rjson)
library(jsonlite)
library(plyr)

# --------------------------------------------------
# Retrieve data from Cartola and store in R format
# --------------------------------------------------

# Fetch api
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

# Merge detailed scouts into df_1
df_2 <- athletes$atletas$scout
df_1 <- cbind(df_1, athletes$atletas$scout)
rm(df_2)

# Store data frame
write.csv(df_1, "db/2016/rodada-3.csv")




