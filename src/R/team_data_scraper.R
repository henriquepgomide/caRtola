######################
# INFO ---------------
######################

# This script scrapes team data from the CBF website and writes it down to file tabela-times.csv
# XML 

library(XML)
library(httr)

page <- GET(
  "https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a/2018"
)

theurl <- htmlTreeParse(page, useInternal = TRUE)
tables <- readHTMLTable(theurl)
 n.rows <- unlist(lapply(tables, function(t) dim(t)[2]))
info <- tables[[which.max(n.rows)]]
info <- info[,1:18]
colnames(info) <- c("Pos","None","Clube", "P","J","V","E","D", "GP",	"GC",	"SG",	"VM",	"VV",	"DM",	"DV",	"CA",	"CV",	"%")
info[,4:18] <- sapply(info[,4:18], function(x) as.numeric(levels(x))[x])
info <- info[,-2]
info <- info[1:20,]
rm(n.rows,tables, theurl)

# Write data as csv file
write.csv(info, "data/2018/2018_tabelas.csv", row.names=FALSE)


# ---------------
# Retrieve all matches results from CBF website
# Recuperar dados das partidas para prever vitórias entre os times do campeonato brasileiro
# ---------------

page <- GET(
  "https://cbf.com.br/competicoes/brasileiro-serie-a/tabela/2018"
)

theurl <- htmlTreeParse(page, useInternal = TRUE)
tables <- readHTMLTable(theurl)
n.rows <- unlist(lapply(tables, function(t) dim(t)[1]))
info <- tables[[which.max(n.rows)]]
info <- info[,1:8]
colnames(info) <- c("game","round","date", "home_team","score","away_team","arena","X")
# Write file as csv - Gravar resultados das partidas
write.csv(info, "data/2018/2018_partidas.csv")
rm(n.rows,tables, theurl, info)
