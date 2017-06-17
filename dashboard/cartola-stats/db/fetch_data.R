# Read data from repository
cartola <- read.csv("db/2017/cartola_2017.csv", stringsAsFactors = FALSE)
cartola$atletas.apelido <- paste(cartola$atletas.apelido, " (", cartola$atletas.clube_id,")")
dir.create("dashboard/cartola-stats/db/rds")
saveRDS(cartola[, -1], "dashboard/cartola-stats/db/rds/cartola.rds")
write.csv(cartola[, -1], "dashboard/cartola-stats/db/cartola.csv", row.names = FALSE)
