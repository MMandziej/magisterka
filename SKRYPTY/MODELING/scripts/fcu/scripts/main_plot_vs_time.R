main_plot_vs_time = function(full_backlog,
                             threshold,
                             type='model_performance') {
  # LOAD DATA AND ADD WEEK VARIABLE
  full_backlog$week = floor_date(full_backlog$pqc_timestamp, unit = 'weeks', week_start = 1)
  
  # DIVIDE DATA INTO SEPARATED DATASETS
  development_dataset <- full_backlog %>% filter(Stage == 'development') %>% arrange(pqc_timestamp)
  monitoring_dataset <- full_backlog %>% filter(Stage == 'monitoring') %>% arrange(pqc_timestamp)
  production_dataset <- full_backlog %>% filter(Stage == 'production') %>% arrange(pqc_timestamp)
  
  # CALCULATE NUMBER OF CASES AND ERRORS PER WEEK
  cases_development = development_dataset %>% group_by(week) %>%
    summarize(CasesCount=n(), LabelCount=sum(Label=="1"))
  cases_monitoring = monitoring_dataset %>% group_by(week) %>%
    summarize(CasesCount=n(), LabelCount=sum(Label=="1"))
  cases_production = production_dataset %>% group_by(week) %>%
    summarize(CasesCount=n(), LabelCount=sum(Label=="1"))
  
  # CALCULATE MODEL PERFORMANCE METRICS
  development_dataset <- development_dataset %>% arrange(desc(pqc))
  monitoring_dataset <- monitoring_dataset %>% arrange(desc(pqc))
  
  development_data <- development_dataset[1:round((nrow(development_dataset) * threshold)),]
  threshold_score <- min(development_data$pqc)
  monitoring_data <- monitoring_dataset %>% filter(pqc >= threshold_score)
  
  production_data <- production_dataset %>% select(week, pqc, Label) %>%
    group_by(week) %>% arrange(week, desc(pqc)) %>%
    filter(pqc >= quantile(pqc, (1-threshold))) # filter(row_number() / n() <= .2)

  if (type == "model_performance") {
  # DEVELOPMENT MERGE DATA
  development_error_detection <- development_data %>% group_by(week) %>%
    summarize(CasesSelected=n(),
              ErrorsDetected=sum(Label=="1"))
  development_error_detection <- merge(development_error_detection, cases_development, by = 'week')
  development_error_detection$ErrorsDetectedPct <- 100 * development_error_detection$ErrorsDetected / development_error_detection$LabelCount
  development_error_detection$CasesSelectedPct <- 100 * development_error_detection$CasesSelected / development_error_detection$CasesCount
  development_error_detection[is.na(development_error_detection)] <- 100
  
  # MONITORING MERGE DATA
  monitoring_error_detection <- monitoring_data %>% group_by(week) %>%
    summarize(CasesSelected=n(),
              ErrorsDetected=sum(Label=="1"))
  monitoring_error_detection <- merge(monitoring_error_detection, cases_monitoring, by = 'week')
  monitoring_error_detection$ErrorsDetectedPct <- 100 * monitoring_error_detection$ErrorsDetected / monitoring_error_detection$LabelCount
  monitoring_error_detection$CasesSelectedPct <- 100 * monitoring_error_detection$CasesSelected / monitoring_error_detection$CasesCount
  monitoring_error_detection[is.na(monitoring_error_detection)] <- 100
  
  # PRODUCTION MERGE DATA
  production_error_detection <- production_data %>% group_by(week) %>%
    summarize(CasesSelected=n(),
              ErrorsDetected=sum(Label=="1"))
  production_error_detection <- merge(production_error_detection, cases_production, by = 'week')
  production_error_detection$ErrorsDetectedPct <- 100 * production_error_detection$ErrorsDetected / production_error_detection$LabelCount
  production_error_detection$CasesSelectedPct <- 100 *  production_error_detection$CasesSelected / production_error_detection$CasesCount
  production_error_detection[is.na(production_error_detection)] <- 100
  
  
  ### MODEL PERFORMANCE PLOT ###
  results = plot_ly() %>%
    # DEVELOPMENT ERROR DETECTION [%]
    add_trace(x = development_error_detection$week,
              y = development_error_detection$ErrorsDetectedPct,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of errors found - development',
              line = list(color='#cc971b')) %>%
    # DEVELOPMENT CASES SELECTED [%]
    add_trace(x = development_error_detection$week,
              y = development_error_detection$CasesSelectedPct,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of cases selected - development',
              line = list(color='#38c24d')) %>%
    
    # MONITORING ERROR DETECTION [%]
    add_trace(x = monitoring_error_detection$week,
             y = monitoring_error_detection$ErrorsDetectedPct,
             type = 'scatter',
             mode = 'lines',
             name = '[%] of errors found - monitoring',
             line = list(color='#d68f00')) %>%
    # # MONITORING CASES SELECTED [%]
    add_trace(x = monitoring_error_detection$week,
              y = monitoring_error_detection$CasesSelectedPct,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of cases selected - monitoring',
              line = list(color='#37db50')) %>%
    
    # PRODUCTION ERROR DETECTION [%]
    add_trace(x = production_error_detection$week,
              y = production_error_detection$ErrorsDetectedPct,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of errors found - production',
              line = list(color='#F4A60A')) %>%
    # PRODUCTION CASES SELECTED [%]
    add_trace(x = production_error_detection$week,
              y = production_error_detection$CasesSelectedPct,
              type = 'scatter',
              mode = 'lines',
              name = '[%] of cases selected - production',
              line = list(color='#58FB06')) %>%
    # NUMBER OF CASES SCORED - DEVELOPMENT
    add_trace(yaxis = 'y2',
              x = cases_development$week, y = cases_development$CasesCount, 
              name = 'Scored cases - development',
              marker = list(color='#d97cf2'),
              type = 'bar') %>%
    # NUMBER OF CASES SCORED - MONITORING
    add_trace(yaxis = 'y2',
              x = cases_monitoring$week, y = cases_monitoring$CasesCount, 
              name = 'Scored cases - monitoring',
              marker = list(color='#f29f7c'),
              type = 'bar') %>%
    # NUMBER OF CASES SCORED - PRODUCTION
    add_trace(yaxis = 'y2',
              x = cases_production$week, y = cases_production$CasesCount, 
              name = 'Scored cases - production',
              marker = list(color='#3fbafc'),
              type = 'bar') %>%
    # ADJUST LEGEND
    layout(#title = "Changes of model performance in time",
      legend = list(y = -0.05,
                    orientation = "h",   # show entries horizontally
                    xanchor = "center",  # use center of legend as anchor
                    x = 0.5),
      margin = list(r = 50),
      xaxis = list(range = c(min(cases_development$week), max(cases_production$week) + 10*86400)),
      
      yaxis = list(side = 'left',
                   overlaying = "y2",
                   ticksuffix = "%",
                   title = paste('[%] of errors found in ', 100 * threshold, '% of population'),
                   showgrid = T,
                   zeroline = FALSE),
      yaxis2 = list(side = 'right',
                    title = 'Scored cases',
                    showgrid = F,
                    zeroline = FALSE))
  } else if (type == 'average_score') {
  
  # GET AVG CASES REWORKS AND NO REWORKS
  development_data_0 <- development_data[development_data$Label == "0",]
  development_data_1 <- development_data[development_data$Label == "1",]
  monitoring_data_0 <- monitoring_data[monitoring_data$Label == "0",]
  monitoring_data_1 <- monitoring_data[monitoring_data$Label == "1",]
  production_data_0 <- production_data[production_data$Label == "0",]
  production_data_1 <- production_data[production_data$Label == "1",]
  
  development_avg_scores_0 <- development_data_0 %>% group_by(week) %>%
    summarize(AvgScore=mean(pqc) * 100)
  development_avg_scores_1 <- development_data_1 %>% group_by(week) %>%
    summarize(AvgScore=mean(pqc) * 100)
  
  monitoring_avg_scores_0 <- monitoring_data_0 %>% group_by(week) %>%
    summarize(AvgScore=mean(pqc) * 100)
  monitoring_avg_scores_1 <- monitoring_data_1 %>% group_by(week) %>%
    summarize(AvgScore=mean(pqc) * 100)
  
  production_avg_scores_0 <- production_data_0 %>% group_by(week) %>%
    summarize(AvgScore=mean(pqc) * 100)
  production_avg_scores_1 <- production_data_1 %>% group_by(week) %>%
    summarize(AvgScore=mean(pqc) * 100)
  
  ### AVERAGE SCORES PLOT ###
  results = plot_ly() %>%
    # DEVELOPMENT NO REWORKS
    add_trace(x = development_avg_scores_0$week,
              y = development_avg_scores_0$AvgScore,
              name = 'Score for cases with no rework - development',
              type = 'scatter',
              mode = 'lines',
              line = list(color='#DE2626')) %>%
    # DEVELOPMENT REWORKS
    add_trace(x = development_avg_scores_1$week,
              y = development_avg_scores_1$AvgScore,
              name = 'Score for cases with with rework - development',
              type = 'scatter',
              mode = 'lines',
              line = list(color='#266EDE')) %>%
    # MONITORING NO REWORKS
    add_trace(x = monitoring_avg_scores_0$week,
              y = monitoring_avg_scores_0$AvgScore,
              name = 'Score for cases with no rework rework - monitoring',
              type = 'scatter',
              mode = 'lines',
              line = list(color='#BB0000')) %>%
    # MONITORING REWORKS
    add_trace(x = monitoring_avg_scores_1$week,
              y = monitoring_avg_scores_1$AvgScore,
              name = 'Score for cases with rework - monitoring',
              type = 'scatter',
              mode = 'lines',
              line = list(color='#0A54C6'))%>%
    # PRODUCTION NO REWORKS
    add_trace(x = production_avg_scores_0$week,
              y = production_avg_scores_0$AvgScore,
              name = 'Score for cases with no rework rework - production',
              type = 'scatter',
              mode = 'lines',
              line = list(color='#750202')) %>%
    # PRODUCTION REWORKS
    add_trace(x = production_avg_scores_1$week,
              y = production_avg_scores_1$AvgScore,
              name = 'Score for cases with rework - production',
              type = 'scatter',
              mode = 'lines',
              line = list(color='#003891'))%>%
    # NUMBER OF CASES SCORED - DEVELOPMENT
    add_trace(yaxis = 'y2',
              x = cases_development$week, y = cases_development$CasesCount, 
              name = 'Scored cases - development',
              marker = list(color='#d97cf2'),
              type = 'bar') %>%
    # NUMBER OF CASES SCORED - MONITORING
    add_trace(yaxis = 'y2',
              x = cases_monitoring$week, y = cases_monitoring$CasesCount, 
              name = 'Scored cases - monitoring',
              marker = list(color='#f29f7c'),
              type = 'bar') %>%
    # NUMBER OF CASES SCORED - PRODUCTION
    add_trace(yaxis = 'y2',
              x = cases_production$week, y = cases_production$CasesCount, 
              name = 'Scored cases - production',
              marker = list(color='#3fbafc'),
              type = 'bar') %>%
    
    layout(#title = "Changes of model performance in time",
      legend = list(y = -0.05,
                    orientation = "h",   # show entries horizontally
                    xanchor = "center",  # use center of legend as anchor
                    x = 0.5),
      margin = list(r = 50),
      xaxis = list(range = c(min(development_avg_scores_0$week), max(production_avg_scores_0$week) + 10*86400)),
      yaxis=list(side = 'left',
                 overlaying = "y2",
                 ticksuffix = "%",
                 title = paste('Average reworks / no-reworks scores in ', 100*threshold, '% of population'),
                 showgrid = T,
                 zeroline = FALSE),
      yaxis2 = list(side = 'right',
                    title = 'Scored cases',
                    showgrid = F,
                    zeroline = FALSE))
  }
  return(results)
}
  