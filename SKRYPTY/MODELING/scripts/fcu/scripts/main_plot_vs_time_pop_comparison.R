main_plot_vs_time_pop_comparison = function(full_backlog) {
  
  # LOAD DATA AND ADD WEEK VARIABLE
  full_backlog$week = floor_date(full_backlog$pqc_timestamp, unit = 'weeks', week_start = 1)
  
  production_dataset <- full_backlog %>% filter(Stage == 'production') %>% arrange(pqc_timestamp)
  
  cases_production = production_dataset %>% group_by(week) %>%
    summarize(CasesCount=n(), LabelCount = sum(Label=="1"),
              SentErrorRate = 100 * sum(Label=="1" & Should_be_send_to_QC=="1") / sum(Should_be_send_to_QC=="1"),
              UnsentErrorRate = 100 * sum(Label=="1" & Should_be_send_to_QC=="0") / sum(Should_be_send_to_QC=="0"),
              SentCount = sum(Should_be_send_to_QC=="1"), UnsentCount = sum(Should_be_send_to_QC=="0"))
  
  ### POPULATION COMPARISON PLOT ###
  results = plot_ly() %>%
    
    # ERROR RATE - SENT TO QC
    add_trace(x = cases_production$week,
              y = cases_production$SentErrorRate,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of errors found - sent to QC',
              line = list(color='#F4A60A')) %>%
    # ERROR RATE - NOT SENT TO QC
    add_trace(x = cases_production$week,
              y = cases_production$UnsentErrorRate,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of errors found - not sent to QC',
              line = list(color='#58FB06')) %>%
    
    # NUMBER OF CASES - SENT TO QC
    add_trace(yaxis = 'y2',
              x = cases_production$week,
              y = cases_production$SentCount, 
              name = 'Number of cases - sent to QC',
              marker = list(color='#eb3434'),
              type = 'bar') %>%
    
    # NUMBER OF CASES - NOT SENT TO QC
    add_trace(yaxis = 'y2',
              x = cases_production$week,
              y = cases_production$UnsentCount, 
              name = 'Number of cases - not sent to QC',
              marker = list(color='#4a9934'),
              type = 'bar') %>%
    # ADJUST LEGEND
    layout(
      barmode = "stack",
      legend = list(y = -0.05,
                    orientation = "h",   # show entries horizontally
                    xanchor = "center",  # use center of legend as anchor
                    x = 0.5),
      margin = list(r = 50),
      xaxis = list(range = c(min(cases_production$week) - 5*86400, max(cases_production$week) + 10*86400)),
      
      yaxis = list(side = 'left',
                   overlaying = "y2",
                   ticksuffix = "%",
                   title = paste('[%] of errors in population'),
                   showgrid = T,
                   zeroline = FALSE),
      yaxis2 = list(side = 'right',
                    title = 'Number of cases',
                    showgrid = F,
                    zeroline = FALSE))
  
  return(results)
}
  