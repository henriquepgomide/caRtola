source("lib/merge_all_rounds_individual_stats_per_year.R")
setwd("~/caRtola/")

# Create index table
# Criar tabela de index
basic_info <- subset(cartola, !is.na(cartola$atletas.clube.id.full.name))
basic_info <- basic_info[, c("atletas.atleta_id", "atletas.clube.id.full.name")]
basic_info <- basic_info[!duplicated(basic_info$atletas.atleta_id),]

# Join info + cartola
cartola <- merge(cartola, basic_info, by = "atletas.atleta_id", all.x = TRUE)
rm(basic_info)

# Remove temporary data frame
cartola <- cartola[, c(-14, -15)]

colnames(cartola)[32] <- "atletas.clube.id.full.name"
cartola <- cartola[, c(2,1,3:7, 32, 8:31)]

write.csv(subset(cartola, cartola$atletas.rodada_id == 0), "db/2017/rodada-0.csv", row.names = FALSE)
