library(shiny)
library(shinydashboard)
library(DT)
library(ggplot2)
library(plotly)
library(dplyr)

# Open data
cartola <- read.csv("data/cartola.csv", stringsAsFactors = FALSE)

# Define shinyServer
shinyServer(function(input, output, session) {
  
  # Player Page #
  output$distPlot_1 <- renderPlotly({
    if (length(input$nome) == 0) {
      print("Selecione um jogador")
    } else {
      player <- cartola[cartola$atletas.apelido == input$nome, ]
      ggplot(data = player, aes(x = atletas.rodada_id, y = c(atletas.pontos_num), color = atletas.apelido), by = atletas.apelido) +
        geom_line(size = 1.2) + xlim(min(cartola$atletas.rodada_id)+1,max(cartola$atletas.rodada_id)) + 
        ylim(min(cartola$atletas.pontos_num),max(cartola$atletas.pontos_num)) + ylab("Pontuação") + 
        xlab("Rodada") + theme_minimal() + 
        theme(legend.title=element_blank(), legend.position = "none", text = element_text(size = 10), axis.text = element_text(size = 12))
    }
    
  })
  
  output$distPlot_2 <- renderPlotly({
    if (length(input$nome) == 0) {
      print("Selecione um jogador")
    } else {
      player <- cartola[cartola$atletas.apelido == input$nome, ]
      ggplot(data = player, aes(x = atletas.rodada_id, y = atletas.preco_num, color = atletas.apelido)) + 
        geom_line(size = 1.2) + xlim(min(cartola$atletas.rodada_id),max(cartola$atletas.rodada_id)) + 
        ylim(min(cartola$atletas.pontos_num),max(cartola$atletas.pontos_num)) + ylab("Cartoletas") + xlab("Rodada") + 
        theme_minimal() + theme(legend.title=element_blank(), legend.position = "none", text = element_text(size = 12), legend.text = element_text(size = 10), axis.text = element_text(size = 12))
    }
    
  })
  
  # Team Data
  select <- reactive({
    input$team_select
  })
  
  filter_team <- reactive({
    cartola %>%
      filter(atletas.clube.id.full.name==select() & atletas.status_id == "Provável")
  })
  
  output$teamPlot1 <- renderPlotly({
    df <- filter_team()
    ggplot(data = df, aes(x = casa , y = atletas.pontos_num)) + geom_boxplot(notch = TRUE) +  geom_point(position = position_jitter(width = 0.2))
  })
    
  output$teamPlot2 <- renderPlotly({
    df <- filter_team()
    ggplot(data = df, aes(x = atletas.posicao_id , y = atletas.pontos_num)) + geom_boxplot(notch = TRUE) +  geom_point(position = position_jitter(width = 0.2))
  })
  
  # Table Data 
  output$table <- DT::renderDataTable(DT::datatable({
    data <- cartola[, c("atletas.apelido", "atletas.clube.id.full.name", "atletas.rodada_id", "atletas.posicao_id", "atletas.status_id", "atletas.pontos_num", "atletas.preco_num" )]
    if (input$club_id != "All") {
      data <- data[data$atletas.clube.id.full.name == input$club_id,]
    }
    if (input$status != "All") {
      data <- data[data$atletas.status_id == input$status,]
    }
    if (input$pos != "All") {
      data <- data[data$atletas.posicao_id == input$pos,]
    }
    data
  },colnames = c("Nome","Clube", "Rodada", "Posição", "Status", "Pontos", "Preço"),
  filter = "top"))

}
)
  
