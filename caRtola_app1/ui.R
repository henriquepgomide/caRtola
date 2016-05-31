library(shiny)


shinyUI(
  
  fluidPage(
    titlePanel("Cartola - \'15"),
    
    fluidRow(
      fluidRow(
        column(4,
               selectInput("points_pg", 
                           "Pontos por jogo:",
                           c("All", unique(as.character(cartola_2015_Long$points_pg))))
        ),
        column(4,
               selectInput("price_pg", 
                           "Preço por jogo:",
                           c("All", unique(as.character(cartola_2015_Long$price_pg))))
        ),
        column(4,
               selectInput("points_per_price", 
                           "Pontos por cartoleta:",
                           c("All", unique(as.character(cartola_2015_Long$points_per_price))))
        )
        
      ),
      fluidRow(
        DT::dataTableOutput("table")
      )
    ),
    
    fluidRow(
      sidebarLayout(
        sidebarPanel(
          p("O objetivo deste webapp é explorar as estatísticas dos jogadores do Cartola FC, temporada 2015."),
          selectInput("var", 
                      label = "Escolha ou digite um jogador",
                      choices = cartola_2015_Long$Atleta,
                      selected = ""),
          
          hr(),
          p("Desenvolvido por Henrique Gomide")
          
        ),
        
        mainPanel(
          h1(textOutput("text1")),
          p(textOutput("gp"))
        )
      )
    )
  
  
  )
)