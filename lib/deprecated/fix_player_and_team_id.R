source("lib/merge_all_rounds_individual_stats_per_year.R")
setwd("~/caRtola/")

# Create index table
# Criar tabela de index
basic_info <- subset(cartola, !is.na(cartola$atletas.clube.id.full.name))
basic_info <- basic_info[, c("atletas.atleta_id", "atletas.clube.id.full.name")]
# Join info + cartola
cartola <- merge(cartola, basic_info, by = "atletas.atleta_id", all.x = TRUE)
# Remove temporary data frame
rm(basic_info)

cartola <- cartola[, -33]
colnames(cartola)[33] <- "atletas.clube.id.full.name"
cartola <- cartola[, c(2,1,3:7, 33, 8:32)]

write.csv(subset(cartola, cartola$atletas.rodada_id == 7), "db/2017/rodada-7.csv", row.names = FALSE)
