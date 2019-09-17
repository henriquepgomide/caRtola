# Author - Henrique Gomide Copyright
library(tidyverse)
library(zoo)

setwd("~/caRtola")
source("~/caRtola/src/R/utils.R")

# 0. Dataprep -------------------------------------------------------------
data <- readCsvInsideFolder("~/caRtola/data/2019/",
                            "rodada",
                            "2019")

# Fix encoding
data$atletas.nome               <- fixEncodingIssues(data$atletas.nome)
data$atletas.clube.id.full.name <- fixEncodingIssues(data$atletas.clube.id.full.name)
data$atletas.status_id          <- fixEncodingIssues(data$atletas.status_id)

# Transform rodada_id into factor
data$atletas.rodada_id  <- factor(data$atletas.rodada_id,
                                  levels = c(1:max(data$atletas.rodada_id)),
                                  ordered = TRUE)

# Convert team names with universal team ids
mapTeamNames <- function(var) {
  # Map team names using all year dictionary
  temp1 <- read.csv("~/caRtola/data/times_ids.csv", stringsAsFactors = FALSE)
  var <- plyr::mapvalues(var, 
                         from = as.vector(temp1$nome.cartola), 
                         to = as.vector(temp1$id))
  rm(temp1)
  return(var)
}

data$atletas.clube.id.full.name <-  mapTeamNames(data$atletas.clube.id.full.name)

# Create column to flag players who really got into the game
#is_column_NA    <- sapply(data[, 16:33],  function(x) is.na(x))
#data$has.played <- apply(is_column_NA, 1, function(x) any(x == FALSE))
data$has.played <- ifelse(data$atletas.variacao_num == 0, FALSE, TRUE)
#rm(is_column_NA)

# Subset data
data <- 
  data %>%
  dplyr::arrange(atletas.atleta_id, atletas.rodada_id) %>%
  dplyr::filter(atletas.posicao_id != "tec" & has.played == TRUE)

# Create players list
player_info <- 
  data %>%
  dplyr::select(atletas.slug, atletas.atleta_id, atletas.clube.id.full.name, 
                atletas.posicao_id, atletas.rodada_id, atletas.pontos_num, 
                atletas.status_id, atletas.apelido, atletas.preco_num,
                atletas.variacao_num)

# Deaggregate scouts
deaggregateScouts <- function(data) {
  # Deaggregate scouts from Cartola Data - which is aggregated from the API
  # Helper function to lag over columns 
  lagScouts <- function(x) {
    return(x - lag(x, 1, default = NA))
  }
  
  # Create deaggregated scouts 
  scouts <-
    data %>%
    arrange(atletas.atleta_id, atletas.rodada_id) %>%
    dplyr::select(atletas.status_id, 
           atletas.rodada_id, atletas.atleta_id, 
           CA, FC, 
           FS, GC, I,
           PE, RB, SG,
           FF, FD, G, 
           DD, GS, A,
           FT, CV, DP,
           PP) 
  
  scouts[,4:21] <- sapply(scouts[,4:21], function(x) ifelse(is.na(x), 0, x))
  
  col_names <- names(scouts)[4:21]
  
  deaggragate_scouts <- 
    scouts %>%
    group_by(atletas.atleta_id) %>%
    mutate_at(.vars = col_names, .funs = lagScouts) %>%
    fill(col_names, .direction = "up") %>%
    filter(atletas.rodada_id != min(atletas.rodada_id))
  
  first_round_stats <- 
    scouts %>%
    group_by(atletas.atleta_id) %>%
    filter(atletas.rodada_id == min(atletas.rodada_id))
  
  scouts <- rbind(deaggragate_scouts, first_round_stats)
  scouts <- arrange(scouts, atletas.atleta_id, atletas.rodada_id)
  scouts <- dplyr::select(scouts, -atletas.status_id)
  scouts <- as.data.frame(scouts)
  return(scouts)
  
}

# Join with proper scouts
scouts <- deaggregateScouts(data)

data <- left_join(player_info, scouts, 
                  by = c("atletas.atleta_id", "atletas.rodada_id"))

# Validation  - Compute scores
#data$computed.score <- 
#   (data$CA * -2) + (data$FC * -0.5) + (data$RB * 1.5) +
#   (data$GC * -5) + (data$CV * -5)   + (data$SG * 5) +
#   (data$FS * .5) + (data$PE * -.3)  + (data$A * 5)  +
#   (data$FT * 3)  + (data$FD * 1.2)  + (data$FF * .8) +
#   (data$G * 8)   + (data$I * -.5)   + (data$PP * -4) +
#   (data$DD * 3)  + (data$DP * 7)    + (data$GS * -2)
## Plot scatter to check if scouts were properly handled
#ggplot(data, aes(x = computed.score, y = atletas.pontos_num)) +
#  geom_point()

# 1. Feature Engineering ---------------------------------------------------
# 2. Remove clean sheet bonus
data$score.no.cleansheets <- 
   (data$CA * -2) + (data$FC * -0.5) + (data$RB * 1.5) +
   (data$GC * -5) + (data$CV * -5)   + #(data$SG * 5) +
   (data$FS * .5) + (data$PE * -.3)  + (data$A * 5)  +
   (data$FT * 3)  + (data$FD * 1.2)  + (data$FF * .8) +
   (data$G * 8)   + (data$I * -.5)   + (data$PP * -4) +
   (data$DD * 3)  + (data$DP * 7)    + (data$GS * -2)

# Compute fouls for each round
data$faltas <- data$FC + data$CA + data$CV

# Compute shots on goal
data$shotsX <- data$G + data$FT + data$FD + data$FF

names(data)[1:6] <- c("slug", "atleta.id", "team", 
                      "posicao", "rodadaF", "pontuacao")

data$rodada <- as.integer(data$rodadaF)

matches <- read.csv("~/caRtola/data/2019/2019_partidas.csv", 
                    check.names = FALSE,
                    stringsAsFactors = FALSE)

convertMatchesToTidy <- function(dataframe) { 
  # Convert and preprocess matches dataframe 
  tidy_matches <- tidyr::gather(dataframe, `home_team`, `away_team`, 
                                value = "team_name", key = "home_away")
  
  tidy_matches <- dplyr::select(tidy_matches, date, home_away, team_name, round)
  tidy_matches$home_away <- gsub("_team", "", tidy_matches$home_away)
  tidy_matches$team_name <- as.character(tidy_matches$team_name)
  tidy_matches <- as.data.frame(tidy_matches)
  tidy_matches <- distinct(tidy_matches, team_name, round, .keep_all = TRUE)
  
  return(tidy_matches)
}

matches <- convertMatchesToTidy(matches)

# Merge matches and data frames to compute home and away scores
data <- left_join(data, matches, 
                   by = c("team" = "team_name",
                          "rodada" = "round"))


# Create scouts with mean
scouts.mean <- 
  data %>%
  dplyr::group_by(atleta.id) %>% 
  dplyr::arrange(rodadaF) %>%
  dplyr::mutate_at(.vars = c("shotsX", "faltas", "RB", 
                      "PE", "A", "I",
                      "FS", "FF", "G",
                      "DD", "DP", 
                      "score.no.cleansheets",
                      "pontuacao"), .funs = cummean) %>%
  dplyr::select(c("atleta.id", "rodada",
                  "shotsX", "faltas", "RB", 
                  "PE", "A", "I",
                  "FS", "FF", "G",
                  "DD", "DP",
                  "score.no.cleansheets",
                  "pontuacao"))

names(scouts.mean)[3:15] <- paste0(names(scouts.mean)[3:15], "_mean") 

data <- left_join(x = data, y = scouts.mean, by = c("rodada", "atleta.id"))

# Create home and away features
createHomeAndAwayScouts <- function(){
  scouts.home.away <- 
    data %>%
    dplyr::group_by(atleta.id, home_away) %>%
    dplyr::arrange(rodadaF) %>%
    dplyr::mutate_at(.vars = c("score.no.cleansheets", "pontuacao"), 
                     .funs = cummean) %>%
    dplyr::select("atleta.id", "home_away", "rodada", 
                  "score.no.cleansheets","pontuacao") 
  
  names(scouts.home.away)[4:5] <- paste0(names(scouts.home.away)[4:5], ".mean") 
  
  scouts.home.away <- tidyr::gather(scouts.home.away, 
                             key = vars,
                             value = "valores",
                             -home_away,
                             -rodada,
                             -atleta.id) 
  
  scouts.home.away <- tidyr::unite(scouts.home.away, 
                            col = "var",
                            "vars", "home_away",
                            sep = ".")
  
  scouts.home.away <- tidyr::spread(scouts.home.away,
                             key = var,
                             value = valores)
 
  scouts.home.away <- scouts.home.away %>%
    fill(pontuacao.mean.home, pontuacao.mean.away,
         score.no.cleansheets.mean.home, score.no.cleansheets.mean.away)
  
  return(scouts.home.away)
  
}
scouts.home.away <- createHomeAndAwayScouts()

# Create players list and estimate number of games played for each player
players.list <- 
  data %>%
  dplyr::group_by(atleta.id) %>%
  dplyr::summarise(n.jogos = n(),
                   rodada  = max(rodada)) # %>%
#  dplyr::filter(n.jogos >= 1)

n.games.scouts.home.away <- left_join(players.list, scouts.home.away,
                              by = c("atleta.id" = "atleta.id",
                                     "rodada" = "rodada"))

data <- left_join(data, n.games.scouts.home.away, 
                  by = c("atleta.id" = "atleta.id",
                         "rodada" = "rodada"))

# Create home and away diff to measure how stable each player at home and away
df.model <- 
  data %>%
  dplyr::filter(atleta.id %in% players.list$atleta.id) %>%
  dplyr::filter(rodada >= 1) %>%
  dplyr::mutate(diff.home.away = score.no.cleansheets.mean.home
                - score.no.cleansheets.mean.away)

df.model$diff.home.away.scalled <- scale(df.model$diff.home.away)

# Get last know stats for each player ---------------------------------------------------------
df.agg <- 
  df.model %>%
  dplyr::group_by(atleta.id) %>%
  dplyr::filter(rodadaF == max(rodadaF))

df.cartola.2019 <- 
  df.agg %>%
  dplyr::select(slug, atleta.id, atletas.apelido, 
         team, posicao, atletas.preco_num, 
         pontuacao_mean, score.no.cleansheets_mean, diff.home.away.scalled, n.jogos,
         pontuacao.mean.home, pontuacao.mean.away,
         shotsX_mean, faltas_mean, RB_mean,
         PE_mean, A_mean, I_mean, 
         FS_mean, FF_mean, G_mean,
         DD_mean, DP_mean,
         atletas.status_id, atletas.variacao_num, pontuacao)

names(df.cartola.2019) <- c("player_slug", "player_id", "player_nickname",
                            "player_team", "player_position", "price_cartoletas",
                            "score_mean", "score_no_cleansheets_mean", 
                            "diff_home_away_s", "n_games",
                            "score_mean_home", "score_mean_away",
                            "shots_x_mean", "fouls_mean",
                            "RB_mean", "PE_mean", "A_mean",
                            "I_mean", "FS_mean", "FF_mean",
                            "G_mean", "DD_mean", "DP_mean",
                            "status", "price_diff", "last_points")

write.csv(df.cartola.2019,
          "~/caRtola/data/2019/2019-medias-jogadores.csv", 
          row.names = FALSE,
          na = "0")
