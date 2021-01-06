cases_avg_score_plot = function(scored_cases_backlog) {
  scored_cases_backlog <- scored_cases_backlog %>% filter(Stage == 'production')
  scored_cases_backlog$week <- floor_date(scored_cases_backlog$pqc_timestamp, 'week')
  #scored_cases_backlog$pqc <- as.numeric(as.character(scored_cases_backlog$pqc))
  cases_sent_to_qc = scored_cases_backlog[scored_cases_backlog$Should_be_send_to_QC == "1", ]
  
  avg_score <- aggregate(scored_cases_backlog$pqc,
                         by=list(Category=scored_cases_backlog$week), FUN=mean) # date of join to project
  cases_scored <- data.frame(table(scored_cases_backlog$week))
  cases_qc <- data.frame(table(cases_sent_to_qc$week))
  
  avg_score$cases_scored <- cases_scored$Freq
  avg_score$cases_qc <- cases_qc$Freq
  
  plot_data <- avg_score
  colnames(plot_data) <- c('week', 'avg_score', 'cases_scored', 'cases_qc')
  
  #plot_data <- plot_data[which(as.Date(plot_data$week) > as.Date("2020-03-30")),]
  plot_data['sent_qc_percentage'] <- plot_data['cases_qc'] / plot_data['cases_scored']
  results = plot_ly(x = plot_data$week,
                    y = plot_data$avg_score,
                    name = 'Weekly average score',
                    type = 'scatter',
                    mode = 'lines',
                    line = list(color='#ffb366')) %>%

  add_trace(x = plot_data$week,
            y = plot_data$sent_qc_percentage, 
            name = '[%] of cases sent to QC',
            type = 'scatter',
            mode = 'lines',
            line = list(color='#266EDE')) %>%
  
  add_trace(yaxis='y2',
            x = plot_data$week,
            y = plot_data$cases_scored, 
            name = 'Number of scored cases', 
            type = 'bar') %>%
  
  # added
  add_trace(yaxis='y2',
            x = plot_data$week,
            y = plot_data$cases_qc,
            name = 'Number of cases sent to QC',
            type = 'bar') %>%
    
  layout(legend = list(y = -0.05,orientation = "h",   # show entries horizontally
                       xanchor = "center",  # use center of legend as anchor
                       x = 0.5),
         margin = list(r = 50),
         xaxis = list(range = c(min(plot_data$week)-3*86400, max(plot_data$week)+8*86400)),
         yaxis = list(side = 'left', overlaying = "y2", title='Weekly average score', showgrid = T, zeroline = FALSE), # ticksuffix ="%",
         yaxis2 = list(side = 'right', title = 'Number of cases', showgrid = F, zeroline = FALSE))
  return(results) 
}
