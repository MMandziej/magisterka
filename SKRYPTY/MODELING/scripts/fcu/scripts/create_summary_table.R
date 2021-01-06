create_summary_table = function(developement_dataset, monitoring_dataset, threshold, time_frame='days'){
  
  n_cases_develompent <- dim(developement_dataset)[1] # col1
  n_cases_monitoring <- dim(monitoring_dataset)[1] # col1
  n_errors_development <- sum(developement_dataset$Label) # col2
  n_errors_monitoring <- sum(monitoring_dataset$Label) # col2

    developement_dataset$datestamp = floor_date(developement_dataset$datestamp, unit=time_frame, week_start=1)
  monitoring_dataset$datestamp = floor_date(monitoring_dataset$datestamp, unit=time_frame, week_start=1)
  
  barchart_data_developement_dataset = developement_dataset %>%
    group_by(datestamp) %>% summarize(no_cases=n())
  
  barchart_data_monitoring_dataset = monitoring_dataset %>%
    group_by(datestamp) %>% summarize(no_cases=n())
  
  # count cases with erros on full development and training dataset in distinct time periods
  max_error_developement_dataset = developement_dataset %>%
    group_by(datestamp) %>% summarize(max_error_developement_dataset=sum(Label))
  
  max_error_monitoring_dataset = monitoring_dataset %>%
    group_by(datestamp) %>% summarize(max_error_monitoring_dataset=sum(Label))
  
  max_error_developement_dataset = as.data.frame(max_error_developement_dataset)
  max_error_monitoring_dataset = as.data.frame(max_error_monitoring_dataset)
  
  # calculate what cases include in QC population
  developement_dataset = developement_dataset[order( developement_dataset$scored_df_pqc, decreasing = T),]
  developement_dataset = developement_dataset[1:round((nrow(developement_dataset) * threshold)),]
  threshold_score = min(developement_dataset$scored_df_pqc)
  
  monitoring_dataset = monitoring_dataset[order(monitoring_dataset$scored_df_pqc, decreasing=T),]
  monitoring_dataset = monitoring_dataset[1:(which(
    abs(monitoring_dataset$scored_df_pqc-threshold_score)==min(
      abs(monitoring_dataset$scored_df_pqc-threshold_score)
    )
  )),]
  
  n_pop_cases_development <- dim(developement_dataset)[1] #col3
  n_pop_cases_monitoring <- dim(monitoring_dataset)[1] #col3
  n_pop_errors_development <- sum(developement_dataset$Label) #col4
  n_pop_errors_monitoring <- sum(monitoring_dataset$Label) #col4
  ratio_pop_development <- round(100 * n_pop_cases_development / n_cases_develompent, digits = 2) #col5
  ratio_pop_monitoring <- round(100 * n_pop_cases_monitoring / n_cases_monitoring, digits = 2) #col5
  ratio_error_development <- round(100 * n_pop_errors_development / n_errors_development, digits = 2) #col6
  ratio_error_monitoring <- round(100 * n_pop_errors_monitoring / n_errors_monitoring, digits = 2) #col6
  
  dataset <- c("Development", "Monitoring")
  total_no_cases <- c(n_cases_develompent, n_cases_monitoring)
  total_no_errors <- c(n_errors_development, n_errors_monitoring)
  no_cases_pop <- c(n_pop_cases_development, n_pop_cases_monitoring)
  no_erros_pop <- c(n_pop_errors_development, n_pop_errors_monitoring)
  ratio_population <- c(ratio_pop_development, ratio_pop_monitoring)
  ratio_error <- c(ratio_error_development, ratio_error_monitoring)
  
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
