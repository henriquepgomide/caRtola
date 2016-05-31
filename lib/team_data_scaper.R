# This script scrapes data from clubs from the CBF page
# EXTRACT ID'S INFO - NAME, ID, EMAIL
# XML 
library(XML)
theurl <- htmlTreeParse("http://www.cbf.com.br/competicoes/brasileiro-serie-a/classificacao/2015#.V0erKnUrLeQ", useInternal = TRUE)
tables <- readHTMLTable(theurl)
n.rows <- unlist(lapply(tables, function(t) dim(t)[1]))
info <- tables[[which.max(n.rows)]]
info <- info[, 1:18]
colnames(info) <- c("Pos","None","Clube", "P","J","V","E","D", "GP",	"GC",	"SG",	"VM",	"VV",	"DM",	"DV",	"CA",	"CV",	"%")

sapply(info[,4:18], function(x) as.numeric(x))
