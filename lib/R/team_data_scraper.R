######################
# INFO ---------------
######################

# This script scrapes team data from the CBF website and writes it down to file tabela-times.csv
# XML 

require(XML)
theurl <- htmlTreeParse("http://www.cbf.com.br/competicoes/brasileiro-serie-a/classificacao/2017", useInternal = TRUE)
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
write.csv(info, "db/2017/tabela-times.csv", row.names=FALSE)


# ---------------
# Retrieve all matches results from CBF website
# Recuperar dados das partidas para prever vitórias entre os times do campeonato brasileiro
# ---------------

library(XML)
theurl <- htmlTreeParse("http://www.cbf.com.br/competicoes/brasileiro-serie-a/tabela/2014", useInternal = TRUE)
tables <- readHTMLTable(theurl)
n.rows <- unlist(lapply(tables, function(t) dim(t)[1]))
info <- tables[[which.max(n.rows)]]
info <- info[,1:8]
colnames(info) <- c("game","round","date", "home_team","score","away_team","arena","X")
# Write file as csv - Gravar resultados das partidas
write.csv(info, "db/2014/matches-brasileirao-2014.csv")
rm(n.rows,tables, theurl, info)
