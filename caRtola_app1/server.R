library(shiny)
library(DT)

shinyServer(
  function(input, output) {
    
    output$text1 <- renderText({ 
      input$var
      
    })
    
    output$gp <- renderText({
      data <- cartola_2015_Long
      data <- data[data$Atleta == input$var,]
      paste("Jogos disputados: ", data$gamesPlayed)
    })
    
    output$table <- DT::renderDataTable(DT::datatable({
      data <- cartola_2015_Long
      if (input$points_pg != "All") {
        data <- data[data$manufacturer == input$points_pg,]
      }
      if (input$price_pg != "All") {
        data <- data[data$cyl == input$price_pg,]
      }
      if (input$points_per_price != "All") {
        data <- data[data$trans == input$points_per_price,]
      }
      data
    }))
    
    
  }
)