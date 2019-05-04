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

fetchMatchData <- function(url, path) {
  # Returns match results from us.soccerway website and store them as csv file
  # url - url to fetch data
  # path - where to save data
  GET(url) 
  theurl <- htmlTreeParse(page, useInternal = TRUE)
  tables <- readHTMLTable(theurl)
  n.rows <- unlist(lapply(tables, function(t) dim(t)[1]))
  info <- tables[[which.max(n.rows)]]
  info <- info[, 2:5]
  colnames(info) <- c("date", "home_team", "score", "away_team")
  write.csv(info, path)
}

fetchMatchData("https://us.soccerway.com/national/brazil/serie-a/2019/regular-season/r51143/matches/",
               "data/2019/2019_partidas.csv")

