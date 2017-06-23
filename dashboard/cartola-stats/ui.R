library(shiny)
library(shinydashboard)
library(plotly)
cartola <- read.csv("data/cartola.csv", stringsAsFactors = FALSE)


ui <- dashboardPage(skin = "black",
                     
  # HEADER
  dashboardHeader(title = "CaRtola - STATS"),
  
  # SIDEBAR
  dashboardSidebar(
    sidebarMenu(
      menuItem("Jogador", tabName = "player", icon = icon("user")),
      menuItem("Time", tabName = "team", icon = icon("random")),
      menuItem("Dados", tabName = "data", icon = icon("dashboard"))
    )
  ),
  
  # BODY
  dashboardBody(
    tabItems(
    tabItem(tabName = "player",
      fluidRow(
        h2("Jogadores - Comparar"),
        box(title = "Comparar Jogadores", width = "50%", status = "danger", 
        selectizeInput("nome",
                              label = "Selecione seus jogadores",
                              choices = sort(unique(cartola$atletas.apelido)),
                              multiple = TRUE,
                              options = list(maxItems = 5, placeholder = "Selecione seus jogadores"),
                              selected = sort(unique(cartola$atletas.apelido))[1])
        )
      ),
      fluidRow(
        column(6,
         fluidRow(
         box(title = "Pontuação por rodada", solidHeader = FALSE, status = "primary", 
             width = "100%", height = "auto",
           # Show a plot of the generated distribution
           plotlyOutput("distPlot_1", height = "auto")
         )
         )
        ),
      
      column(6,
             fluidRow(
               box(title = "Cartoletas por rodada", solidHeader = FALSE, status = "info", 
                   width = "100%",  height = "auto",
                   # Show a plot of the generated distribution
                   plotlyOutput("distPlot_2", height = "auto")
               )
             )
      )
    )
      
    ),
  
    tabItem(tabName = "team",
        h2("Time - Análise"),
        selectInput("team_select", label="Selecione um time", choices=sort(unique(cartola$atletas.clube.id.full.name))),
        fluidRow(
        box(title = "Pontuação dos jogadores", solidHeader = FALSE, status = "danger", 
              width = "100%",
          column(6,
                plotlyOutput("teamPlot1")
          ),
          column(6,
                 plotlyOutput("teamPlot2")
           )
        )
        )
    ),
    
    tabItem(tabName = "data",
            h2("Dados dos Jogadores"),
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