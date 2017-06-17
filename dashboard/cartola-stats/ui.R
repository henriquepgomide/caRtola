library(shiny)
library(shinydashboard)
cartola <- read.csv("data/cartola.csv", stringsAsFactors = FALSE)


ui <- dashboardPage( skin = "black",
                     
  # HEADER
  dashboardHeader(title = "CaRtola - STATS"),
  
  # SIDEBAR
  dashboardSidebar(
    sidebarMenu(
      menuItem("Jogador", tabName = "player", icon = icon("dashboard")),
      # menuItem("Time", tabName = "team", icon = icon("th")),
      menuItem("Dados", tabName = "data", icon = icon("th"))
    )
  ),
  
  # BODY
  dashboardBody(
    tabItems(
    tabItem(tabName = "player",
      fluidRow(
        column(6,
         
         fluidRow(
         box(title = "Pontuação e valorização por rodada", solidHeader = TRUE, status = "danger", 
             width = "100%",
             selectizeInput("nome",
                            label = "Selecione um jogador",
                            choices = unique(cartola$atletas.apelido),
                            multiple = FALSE,
                            options = list(maxItems = 1, placeholder = "Selecione seu jogador"),
                            selected = "Felipe Melo"),
           # Show a plot of the generated distribution
           plotOutput("distPlot")
         )
         )
        ),
      
      column(6
      )
    )
      
    ),
  
    tabItem(tabName = "team",
        h2("Team")
    ),
    
    tabItem(tabName = "data",
            h2("Dados da Planilha"),
            # Create a new Row in the UI for selectInputs
            fluidRow(
              column(4,
                     selectInput("club_id",
                                 "Time:",
                                 c("All",
                                   unique(as.character(cartola$atletas.clube.id.full.name))))
              ),
              column(4,
                     selectInput("status",
                                 "Status:",
                                 c("All",
                                   unique(as.character(cartola$atletas.status_id))))
              ),
              column(4,
                     selectInput("pos",
                                 "Posição:",
                                 c("All",
                                   unique(as.character(cartola$atletas.posicao_id))))
              )
            ),
            # Print Table
            fluidRow(
              DT::dataTableOutput("table")
            )
            
         
    )
  ))
)