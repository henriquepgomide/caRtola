# Retirar dados da rodada para uma série de vetores com nomes dos times 
# Author: Henrique Gomide
# License: MIT

library(httr)
library(rjson)

getTeamResults <- function(vector_teams, round){
  # Store team results as csv for a given round based on a vector of teams slugs
  # vector_teams: vector of team slugs to be passed on (e.g., outliers) 
  # round       : round to get data
  # Simple Use: getTeamResults(c("afinco", "outliers"), 1)
  # You can loop over the function too to get multiple rounds info at once:
  # for (i in 1:25){getTeamResults(c("afinco", "outliers"), i)}

  url <- "https://api.cartolafc.globo.com/time/slug/%s/%s"
  slugs_vector <- sapply(vector_teams, function(x) sprintf(url,x,round))
  
  team_round_info <- list()
  
  for (i in 1:length(slugs_vector)){
    data <- fromJSON(paste(readLines(slugs_vector[i]), collapse=""))
    
    slug         <- vector_teams[i]
    patrimonio   <- ifelse(!is.null(data$patrimonio), data$patrimonio, NA)
    pontos       <- ifelse(!is.null(data$pontos),     data$pontos,     NA)
    rodada_atual <- data$rodada_atual
    
    df <- data.frame(slug = slug, patrimonio = patrimonio, pontos = pontos, rodada_atual = rodada_atual)
    team_round_info[[i]] <- df
    print(team_round_info[[i]])
    
    Sys.sleep(2) # It's a dood practice to give the server a break while lopping.
  }
  
  team_round_info <- do.call(rbind.data.frame, team_round_info)
  write.csv(team_round_info,
            sprintf("rodada-%s.csv", max(team_round_info$rodada_atual)), 
            row.names = FALSE)
  
}

