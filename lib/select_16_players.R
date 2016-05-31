# Select '16 Players
setwd("db/2016")

# Get the files names
files <-  list.files(pattern="rodada-*")
# Open data.frame
cartola_2016 <-  do.call(rbind, lapply(files, function(x) read.csv(x, stringsAsFactors = FALSE)))

rodada2 <- read.csv("rodada-2.csv")
rodada3 <- read.csv("rodada-3.csv")
rodada2 <- rodada2[,-15]


head(rodada3)
jogadores3 <- subset(rodada3, rodada3$atletas.status_id == "Provável" & rodada3$atletas.pontos_num > 0 & rodada3$atletas.jogos_num >2 )
jogadores3$ppp <- jogadores3$atletas.pontos_num / jogadores3$atletas.preco_num
jogadores3 <- jogadores3[order(jogadores3$ppp, jogadores3$atletas.posicao_id, jogadores3$atletas.clube_id, decreasing = TRUE),]

lista1 <- jogadores3[, c("atletas.apelido","atletas.clube_id","atletas.posicao_id","atletas.preco_num","atletas.pontos_num","ppp","atletas.jogos_num")]
head(lista1, 50)

GK <- subset(lista1, atletas.posicao_id == "gol")
defenders <- subset(lista1, atletas.posicao_id == "zag")
lateral <- subset(lista1, atletas.posicao_id == "lat")
mid <- subset(lista1, atletas.posicao_id == "mei")
strikers <- subset(lista1, atletas.posicao_id == "ata")
coach <- subset(lista1, atletas.posicao_id == "tec")

head(strikers,10)
