create_summary_stages_table = function(full_backlog,
                                       threshold) {
  full_backlog$week = floor_date(full_backlog$pqc_timestamp, unit = 'weeks', week_start = 1)
  
  # DIVIDE DATA INTO SEPARATED DATASETS
  development_dataset <- full_backlog %>% filter(Stage == 'development') %>% arrange(pqc_timestamp)
  monitoring_dataset <- full_backlog %>% filter(Stage == 'monitoring') %>% arrange(pqc_timestamp)
  production_dataset <- full_backlog %>% filter(Stage == 'production',
                                                Should_be_send_to_QC == "1") %>% arrange(pqc_timestamp)
  #production_dataset <- full_backlog %>% filter(Stage == 'production') %>% arrange(pqc_timestamp)
  
  production_dev_dataset <- production_dataset %>% filter(pqc_timestamp < '2020-06-08')
  production_redev_dataset <- production_dataset %>% filter(pqc_timestamp >= '2020-06-08')
  
  n_cases_develompent <- dim(development_dataset)[1] # col1
  n_cases_monitoring <- dim(monitoring_dataset)[1] # col1
  n_cases_production <- nrow(production_dataset) # col1
  n_cases_production_dev <- nrow(production_dev_dataset) # col1
  n_cases_production_redev <- nrow(production_redev_dataset) # col1
  
  n_errors_development <- sum(development_dataset$Label=="1") # col2
  n_errors_monitoring <- sum(monitoring_dataset$Label=="1") # col2
  n_errors_production <- sum(production_dataset$Label=="1") # col2
  n_errors_production_dev <- sum(production_dev_dataset$Label=="1") # col2
  n_errors_production_redev <- sum(production_redev_dataset$Label=="1") # col2
  
  # calculate what cases include in QC population
  development_dataset = development_dataset[order( development_dataset$pqc, decreasing = T),]
  development_dataset = development_dataset[1:round((nrow(development_dataset) * threshold)),]
  threshold_score = min(development_dataset$pqc) # scored_df_pqc) <- error? No such column as scored_df_pqc at this moment
  
  monitoring_dataset = monitoring_dataset[order(monitoring_dataset$pqc, decreasing=T),]
  monitoring_dataset = monitoring_dataset[1:round((nrow(monitoring_dataset) * threshold)),]
  
  production_data <- production_dataset %>% select(week, pqc, Label) %>%
    group_by(week) %>% arrange(week, desc(pqc)) %>%
    filter(pqc >= quantile(pqc, (1-threshold)))
  
  production_data_dev <- production_dev_dataset %>% select(week, pqc, Label) %>%
    group_by(week) %>% arrange(week, desc(pqc)) %>%
    filter(pqc >= quantile(pqc, (1-threshold)))
  
  production_data_redev <- production_redev_dataset %>% select(week, pqc, Label) %>%
    group_by(week) %>% arrange(week, desc(pqc)) %>%
    filter(pqc >= quantile(pqc, (1-threshold)))
  
  n_pop_cases_development <- dim(development_dataset)[1] #col3
  n_pop_cases_monitoring <- dim(monitoring_dataset)[1] #col3
  n_pop_cases_production <- nrow(production_data) #col3
  n_pop_cases_production_dev <- nrow(production_data_dev) #col3
  n_pop_cases_production_redev <- nrow(production_data_redev) #col3
  
  n_pop_errors_development <- sum(development_dataset$Label=="1") #col4
  n_pop_errors_monitoring <- sum(monitoring_dataset$Label=="1") #col4
  n_pop_errors_production <- sum(production_data$Label=="1") #col4
  n_pop_errors_production_dev <- sum(production_data_dev$Label=="1") #col4
  n_pop_errors_production_redev <- sum(production_data_redev$Label=="1") #col4
  
  ratio_pop_development <- round(100 * n_pop_cases_development / n_cases_develompent, digits = 2) #col5
  ratio_pop_monitoring <- round(100 * n_pop_cases_monitoring / n_cases_monitoring, digits = 2) #col5
  ratio_pop_production <- round(100 * n_pop_cases_production / n_cases_production, digits = 2) #col5
  ratio_pop_production_dev <- round(100 * n_pop_cases_production_dev / n_cases_production_dev, digits = 2) #col5
  ratio_pop_production_redev <- round(100 * n_pop_cases_production_redev / n_cases_production_redev, digits = 2) #col5
  
  ratio_error_development <- round(100 * n_pop_errors_development / n_errors_development, digits = 2) #col6
  ratio_error_monitoring <- round(100 * n_pop_errors_monitoring / n_errors_monitoring, digits = 2) #col6
  ratio_error_production <- round(100 * n_pop_errors_production / n_errors_production, digits = 2) #col6
  ratio_error_production_dev <- round(100 * n_pop_errors_production_dev / n_errors_production_dev, digits = 2) #col6
  ratio_error_production_redev <- round(100 * n_pop_errors_production_redev / n_errors_production_redev, digits = 2) #col6
  
  dataset <- c("Development", "Monitoring", "Production - full",
               "Production - development model", "Production - redevelopment model")
  total_no_cases <- c(n_cases_develompent, n_cases_monitoring, n_cases_production,
                      n_cases_production_dev, n_cases_production_redev)
  total_no_errors <- c(n_errors_development, n_errors_monitoring, n_errors_production,
                       n_errors_production_dev, n_errors_production_redev)
  no_cases_pop <- c(n_pop_cases_development, n_pop_cases_monitoring, n_pop_cases_production,
                    n_pop_cases_production_dev, n_pop_cases_production_redev)
  no_erros_pop <- c(n_pop_errors_development, n_pop_errors_monitoring, n_pop_errors_production,
                    n_pop_errors_production_dev, n_pop_errors_production_redev)
  ratio_population <- c(ratio_pop_development, ratio_pop_monitoring, ratio_pop_production,
                        ratio_pop_production_dev, ratio_pop_production_redev)
  ratio_error <- c(ratio_error_development, ratio_error_monitoring, ratio_error_production,
                   ratio_error_production_dev, ratio_error_production_redev)
  
  # create output table
  output_table <- data.frame(dataset, total_no_cases, total_no_errors, no_cases_pop,
                             no_erros_pop, ratio_population, ratio_error)
  names(output_table)[names(output_table) == "dataset"] <- "Dataset"
  names(output_table)[names(output_table) == "total_no_cases"] <- "Total no of cases"
  names(output_table)[names(output_table) == "total_no_errors"] <- "Total no of errors"    
  names(output_table)[names(output_table) == "no_cases_pop"] <- "No of cases within selected population" 
  names(output_table)[names(output_table) == "no_erros_pop"] <- "No of errors within selected population"
  names(output_table)[names(output_table) == "ratio_population"] <- "Ratio of population"
  names(output_table)[names(output_table) == "ratio_error"] <- "Error ratio"

  return(output_table)
}
