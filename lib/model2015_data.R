# Libraries
library(reshape2)
library(ggplot2)
library(plyr)

# model2015_data.R
setwd("db/2015/tidy/")

# Get the files names
files <-  list.files(pattern="CartolaFC*")

# Get clubs codes
club_names <- read.csv("Clubes.csv", stringsAsFactors = FALSE)
club_names <- club_names[, c(1,4)]

# Get position codes
position_codes <- read.csv("posicoes.csv", stringsAsFactors = FALSE)
position_codes <- position_codes[, c(2,4)]


# First apply read.csv, then rbind
cartola_2015 <-  do.call(rbind, lapply(files, function(x) read.csv(x, stringsAsFactors = FALSE)))

# Label clubnames
cartola_2015$Clube <- mapvalues(cartola_2015$Clube, from = as.vector(club_names$ID), to = as.vector(club_names$slug))

# Label position codes
cartola_2015$Posicao <- mapvalues(cartola_2015$Posicao, from = as.vector(position_codes$Cod), to = as.vector(position_codes$abbr))

# Create variable points per price
cartola_2015$ppp <- cartola_2015$Pontos/cartola_2015$Preco

# Estimate games played by player
a <- tapply(cartola_2015$Rodada, cartola_2015$Atleta, length)
# Averages - points and price during the season
b <- tapply(cartola_2015$Pontos, cartola_2015$Atleta, mean)
c <- tapply(cartola_2015$Preco, cartola_2015$Atleta, mean)
d <- tapply(cartola_2015$ppp, cartola_2015$Atleta, mean)
cartola_2015_Long <- data.frame(Atleta = names(a), gamesPlayed = a, points_pg = b, price_pg = c, points_per_price = d)
cols.num <- c(2:5)
cartola_2015_Long[cols.num] <- sapply(cartola_2015_Long[cols.num],as.numeric)
sapply(cartola_2015_Long, class)


# --------------------------------
# Melted data
# --------------------------------
# Remove players who acted less than 25 games
cartola_2015 <- merge(cartola_2015, cartola_2015_Long, by.x = "Atleta", by.y = "Atleta")
cartola_2015 <- subset(cartola_2015, cartola_2015$gamesPlayed >= 25)


#########################
# Exploratory analysis #
#########################

# Points
summary(cartola_2015_Long$points_pg)
quantile(cartola_2015_Long$points_pg, probs = c(0,.5,.7,.9,1))
summary(cartola_2015_Long$price_pg)
hist(cartola_2015_Long$points_pg)
hist(cartola_2015_Long$price_pg)
plot(cartola_2015_Long$points_pg, cartola_2015_Long$price_pg)
quantile(cartola_2015_Long$points_per_price, probs = c(0,.5,.7,.9,1))

# Home vs. Away Points
by(cartola_2015$Pontos, cartola_2015$Mando, mean)

# Points by field position
by(cartola_2015$Pontos, cartola_2015$Posicao, mean)

# Points by team
by(cartola_2015$Pontos, cartola_2015$Clube, mean)

# Sort top 30 by points_pg
sorted <- cartola_2015_Long[order(cartola_2015_Long$points_pg, decreasing = TRUE), ]
listPlayers <- as.vector(sorted[1:15, 1])

# Plot players points during competition
playerData <- cartola_2015
playerData <- subset(playerData, cartola_2015$points_per_price >= .3)
playerData <- playerData[, c("Rodada","Atleta","Apelido","Pontos","Posicao","Clube","points_per_price")]
playerData <- playerData[order(playerData$Atleta, playerData$Rodada), ]

playerDataMelted <- melt(playerData, id.vars=c("Apelido", "Atleta","Rodada","Posicao","Clube"), measure.vars = "Pontos", value.name = "Pontos")  

#########################
# Charts #
#########################

# Forwards
ggplot(data=subset(playerDataMelted, Posicao %in% "ata"), 
       aes(x=Rodada, y=Pontos, colour=Apelido)) +
geom_line(alpha=.5) + theme(legend.position="top")

# Midfielders
ggplot(data=subset(playerDataMelted, Posicao %in% "mei"), 
       aes(x=Rodada, y=Pontos, colour=Apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Defenders
ggplot(data=subset(playerDataMelted, Posicao %in% "zag"), 
       aes(x=Rodada, y=Pontos, colour=Apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Wingers
ggplot(data=subset(playerDataMelted, Posicao %in% "lat"), 
       aes(x=Rodada, y=Pontos, colour=Apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# Head Coaches
ggplot(data=subset(playerDataMelted, Posicao %in% "tec"), 
       aes(x=Rodada, y=Pontos, colour=Apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

# GKs
ggplot(data=subset(playerDataMelted, Posicao %in% "gol"), 
       aes(x=Rodada, y=Pontos, colour=Apelido)) +
  geom_line(alpha=.5) + theme(legend.position="top")

#########################
# Time Series
#########################

timeSeriesData <- cartola_2015[,c("Atleta","Rodada","Apelido","Clube","Posicao","Pontos","Preco","Mando")]
tsMelted <- melt(timeSeriesData, id.vars=c("Atleta","Rodada","Apelido","Clube","Posicao","Mando"), measure.vars = c("Pontos","Preco"))  
test <- dcast(tsMelted, Rodada ~ variable)


