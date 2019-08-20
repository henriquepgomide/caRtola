# Create team features based on previous matches
# Author - Henrique Gomide Copyright

library(tidyverse)
library(fbRanks)
library(lubridate)

# functions ---------------------------------------------------------------
process2018Matches <- function(data){
  
  # Process matches from 2018 and make it compatible with 2019 format 
  data$date       <- as.Date(data$date, format = "%d/%m/%Y - %H:%M")
  data            <- separate(data, score, c("home_score","vs","away_score"), 
                              convert = TRUE)
  data$home_score <- as.integer(data$home_score)
  data$away_score <- as.integer(data$away_score)
  
  # Open data dictionary
  team_dic <- read.csv("~/caRtola/data/times_ids.csv", 
                       stringsAsFactors = FALSE)
  # Look up values
  data$home_team <- plyr::mapvalues(data$home_team, 
                                    from = as.vector(team_dic$nome.cbf),
                                    to = as.vector(team_dic$id))
  
  data$away_team <- plyr::mapvalues(data$away_team, 
                                    from = as.vector(team_dic$nome.cbf),
                                    to = as.vector(team_dic$id))
  
  data <- 
    data %>%
    dplyr::select(date, home_team, away_team, 
                  home_score, away_score, round) %>%
    dplyr::mutate(year = 2018)
  
  return(data)
  
} 

createTeamRanks <- function(matches){
  
  date_range <- 
    matches %>%
    filter(year == 2019) %>%
    group_by(round) %>%
    summarise(min.date = min(date, na.rm = TRUE),
              max.date = max(date, na.rm = TRUE)) %>%
    filter(round == max(round))
  
  team_features <- rank.teams(scores          = matches, 
                              family          = "poisson",
                              fun             = "speedglm",
                              max.date        = Sys.Date(),
                              time.weight.eta = 0.01)
  
  return(team_features)
 
}

createRanksDataFrame <- function(team_features){
  
  data_frame_ranks <- data.frame(print.fbRanks(team_features, header = FALSE))
  data_frame_ranks <- 
    data_frame_ranks %>%
    dplyr::select(ranks.team, ranks.total, ranks.attack,
                  ranks.defense, ranks.n.games.Freq)
  names(data_frame_ranks) <- c("team_name", "strength", "attack",
                               "defense", "n_games")
  
  return(data_frame_ranks)
  
}

predictCleanSheets <- function(team_features){
  
  date_range <- 
    matches %>%
    dplyr::filter(year == last(year) & round == last(round))
 
  teamPredictions <- predict.fbRanks(team_ranks, 
                                     newdata  = matches_to_predict[, c(2,3)],
                                     min.date = min(date_range$date),
                                     max.date = max(date_range$date),
                                     show.matches = TRUE)
  
  home.team.names   <- names(teamPredictions$home.score)
  away.team.names   <- names(teamPredictions$away.score)
  home.goals.vector <- rep(NA,10)
  away.goals.vector <- rep(NA,10)
  
  for (i in 1:10) {
    home.goals.vector[i] <- round(prop.table(table(teamPredictions$home.goals[i,] > 0))[2],2)
    away.goals.vector[i] <- round(prop.table(table(teamPredictions$away.goals[i,] > 0))[2],2)
  }
  
  team.names   <- c(home.team.names, away.team.names)
  scoring.odds <- c(home.goals.vector, away.goals.vector)
  
  scoring.odds.df <- data.frame(team.names = team.names, 
                                scoring.odds = scoring.odds*100)
  
  scoring.odds.df <- arrange(scoring.odds.df, scoring.odds)
  
  return(scoring.odds.df)
}

# Open and merge data -----------------------------------------------------
## Open '18 and '19 datasets
matches_18 <- read.csv("~/caRtola/data/2018/2018_partidas.csv",
                       stringsAsFactors = FALSE)

matches_18 <- process2018Matches(matches_18)

matches_19 <- read.csv("~/caRtola/data/2019/2019_partidas.csv",
                       stringsAsFactors = FALSE) 

matches_19 <- dplyr::mutate(matches_19, year = 2019)

matches <- rbind(matches_18, matches_19)
rm(matches_18, matches_19)


# Data munging ---------------------------------------------------------------
names(matches) <- c("date", "home.team", "away.team",
                    "home.score", "away.score", 
                    "round", "year")

# Create data frame to matches to predict
matches_to_predict <- 
  matches %>%
  filter(year == max(year)) %>%
  filter(round == max(round))

team_ranks      <- createTeamRanks(matches)
df_ranks        <- createRanksDataFrame(team_ranks)
df_clean_sheets <- predictCleanSheets(team_ranks)


# Combine data and export -------------------------------------------------

df_matches <- 
  matches_to_predict %>%
  dplyr::select(round, home.team, away.team)

df_matches$id <- seq.int(nrow(df_matches))

df_matches <- gather(df_matches, `home.team`, `away.team`, key = "home.away", value = "team_name")
df_matches$home.away <- gsub("\\.team", "", df_matches$home.away)

df_to_export <- left_join(df_matches, df_ranks, by = "team_name")
df_to_export <- left_join(df_to_export, df_clean_sheets, by = c("team_name" = "team.names"))
df_to_export <- dplyr::select(df_to_export, -n_games, -round)

df_to_export <- gather(df_to_export, 
                       key = vars,
                       value = value,
                       -id, -home.away)

df_to_export <- unite(df_to_export, 
                      col = "vars",
                      "home.away","vars", 
                      sep = "_")

df_to_export <- spread(df_to_export,
                       key = vars,
                       value = value)

df_to_export <- dplyr::select(df_to_export, 
                              away_defense, away_attack, away_strength, 
                              away_team_name, away_scoring.odds, home_scoring.odds,
                              home_team_name, home_strength, home_attack, home_defense)

names(df_to_export)[c(5,6)] <- c("away_scoring_odds", "home_scoring_odds")

write.csv(df_to_export,
          sprintf("~/caRtola/data/2019/team-features/2019-team-features-round-%s.csv",
                  max(matches_to_predict$round)), 
          row.names = FALSE,
          na = "0")

first_tier_2019 <- unique(c(df_to_export$away_team_name,
                            df_to_export$home_team_name))
  
df_rank_to_export <- 
  df_ranks %>%
  filter(team_name %in% first_tier_2019)

write.csv(df_rank_to_export,
          sprintf("~/caRtola/data/2019/team-rankings/2019-team-rankings-round-%s.csv", 
                  max(matches_to_predict$round)),
          row.names = FALSE,
          na = "0")
