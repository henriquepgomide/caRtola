# What? ----------------------------------------------
# This script is intended to export a cartola dataframe
# into a SQL database
# ----------------------------------------------------

# Objetivo--------------------------------------------
# Este script tem como objetivo exportar o dataframe
# para uma base de dados tipo SQL para o localhost
# ----------------------------------------------------

cartola <- read.csv("db/2017/cartola_2017.csv", stringsAsFactors = FALSE)
colnames(cartola) <- gsub("\\.", "_", colnames(cartola))
colnames(cartola) <- gsub("atletas_", "", colnames(cartola))

user_sql <- "seu_usuario_sql"
password_sql <- "sua_senha_sql"

library(RMySQL)
conn <- dbConnect(MySQL(), user = user_sql, password = password_sql, dbname = "cartola", host = "localhost")
dbWriteTable(conn, name='cartola', value=cartola, row.names = FALSE)
dbSendQuery(conn, "ALTER TABLE cartola MODIFY nome VARCHAR(256);")
dbSendQuery(conn, "ALTER TABLE cartola MODIFY apelido VARCHAR(256);")
dbSendQuery(conn, "ALTER TABLE cartola MODIFY foto VARCHAR(256);")
dbSendQuery(conn, "ALTER TABLE cartola MODIFY clube_id VARCHAR(256);")
dbSendQuery(conn, "ALTER TABLE cartola MODIFY clube_id_full_name VARCHAR(256);")
dbSendQuery(conn, "ALTER TABLE cartola MODIFY posicao_id VARCHAR(256);")
dbSendQuery(conn, "ALTER TABLE cartola MODIFY status_id VARCHAR(256);")
