# Retirar dados da rodada para uma série de vetores com nomes dos times 
# Author: Henrique Gomide
# License: MIT

library(httr)
library(rjson)

getTeamResults <- function(vector_teams, round, path){
  # Store team results as csv for a given round based on a vector of teams ids
  # vector_teams: vector of team ids to be passed on (e.g., outliers) 
  # round       : round to get data
  # Simple Use: getTeamResults(c("id1", "id2"), 1, "~/caRtola/data")
  # You can loop over the function too to get multiple rounds info at once:
  # for (i in 1:25){getTeamResults(c("id1", "id2"), i, "~/caRtola/data")}

  url <- "https://api.cartolafc.globo.com/time/id/%s/%s"
  team_ids_vector <- sapply(vector_teams, function(x) sprintf(url,x,round))
  
  team_round_info <- list()
  
  for (i in 1:length(team_ids_vector)){
    data <- fromJSON(paste(readLines(team_ids_vector[i]), collapse=""))
    
    team_id         <- vector_teams[i]
    patrimonio   <- ifelse(!is.null(data$patrimonio), data$patrimonio, NA)
    pontos       <- ifelse(!is.null(data$pontos),     data$pontos,     NA)
    rodada_atual <- data$rodada_atual
    
    df <- data.frame(team_id = team_id, patrimonio = patrimonio, pontos = pontos, rodada_atual = rodada_atual)
    team_round_info[[i]] <- df
    print(team_round_info[[i]])
    
    Sys.sleep(1) # It's a good practice to give the server a break while lopping.
  }
  
  team_round_info <- do.call(rbind.data.frame, team_round_info)
  write.csv(team_round_info,
            sprintf("%s/rodada-%s.csv", path, max(team_round_info$rodada_atual)), 
            row.names = FALSE)
  
}

