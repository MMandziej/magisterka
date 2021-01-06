model_performance_table = function(developement_dataset, monitoring_dataset, threshold, time_frame='days'){

    developement_dataset$datestamp = floor_date(developement_dataset$datestamp, unit=time_frame, week_start=1)
    monitoring_dataset$datestamp = floor_date(monitoring_dataset$datestamp, unit=time_frame, week_start=1)

    barchart_data_developement_dataset = developement_dataset%>%
      group_by(datestamp) %>% summarize(no_cases=n())
    
    barchart_data_monitoring_dataset = monitoring_dataset%>%
      group_by(datestamp) %>% summarize(no_cases=n())
      
    # count cases with erros on full development and training dataset in distinct time periods
    max_error_developement_dataset = developement_dataset%>%
      group_by(datestamp) %>% summarize(max_error_developement_dataset=sum(Label))
      
    max_error_monitoring_dataset = monitoring_dataset%>%
      group_by(datestamp) %>% summarize(max_error_monitoring_dataset=sum(Label))
      
    max_error_developement_dataset = as.data.frame(max_error_developement_dataset)
    max_error_monitoring_dataset = as.data.frame(max_error_monitoring_dataset)
  
    # calculate what cases include in QC population
    developement_dataset = developement_dataset[order( developement_dataset$scored_df.pqc, decreasing = T),]
    developement_dataset = developement_dataset[1:round((nrow(developement_dataset) * threshold)),]
    threshold_score = min(developement_dataset$scored_df.pqc)

    monitoring_dataset = monitoring_dataset[order(monitoring_dataset$scored_df.pqc, decreasing=T),]
    monitoring_dataset = monitoring_dataset[1:(which(
      abs(monitoring_dataset$scored_df.pqc-threshold_score)==min(
        abs(monitoring_dataset$scored_df.pqc-threshold_score)
        )
      )),]

    barchart_data_developement_dataset_selected = developement_dataset%>%
      group_by(datestamp)%>% summarize(no_cases_selected=n())
    
    barchart_data_monitoring_dataset_selected = monitoring_dataset%>%
      group_by(datestamp) %>% summarize(no_cases_selected=n())
      
    selected_line_developement_dataset = merge(x = barchart_data_developement_dataset,y = barchart_data_developement_dataset_selected,by = 'datestamp',all.x = T)
    selected_line_developement_dataset[is.na(selected_line_developement_dataset)]=0
    selected_line_developement_dataset$selected_prop=100*selected_line_developement_dataset$no_cases_selected/selected_line_developement_dataset$no_cases
      
    selected_line_monitoring_dataset = merge(x = barchart_data_monitoring_dataset,y = barchart_data_monitoring_dataset_selected,by = 'datestamp',all.x = T)
    selected_line_monitoring_dataset[is.na(selected_line_monitoring_dataset)]=0
    selected_line_monitoring_dataset$selected_prop=100*selected_line_monitoring_dataset$no_cases_selected/selected_line_monitoring_dataset$no_cases
      
    developement_dataset=developement_dataset%>%
      group_by(datestamp) %>% summarize(model_performance=sum(Label))
    
    monitoring_dataset=monitoring_dataset%>%
      group_by(datestamp) %>% summarize(model_performance=sum(Label))
      
    developement_dataset = as.data.frame(developement_dataset)
    monitoring_dataset = as.data.frame(monitoring_dataset)
      
    developement_dataset = merge(x=max_error_developement_dataset, y=developement_dataset, by='datestamp', all.x=T)
    developement_dataset[is.na(developement_dataset)] = 0
    developement_dataset$model_performance = 100* developement_dataset$model_performance / developement_dataset$max_error_developement_dataset
      
    monitoring_dataset = merge(x=max_error_monitoring_dataset, y=monitoring_dataset, by='datestamp', all.x=T)
    monitoring_dataset[is.na(monitoring_dataset)] = 0
    monitoring_dataset$model_performance = 100 * monitoring_dataset$model_performance / max_error_monitoring_dataset$max_error_monitoring_dataset
      
    # rename columns for concatenation and create technical column
    names(developement_dataset)[names(developement_dataset) == "max_error_developement_dataset"] <- "max_error"
    names(monitoring_dataset)[names(monitoring_dataset) == "max_error_monitoring_dataset"] <- "max_error"
    developement_dataset$Type <- "Development"
    monitoring_dataset$Type <- "Monitoring"     
    # join full dataset
    full_dataset <- rbind(developement_dataset, monitoring_dataset)
    selected_lines_all <-rbind(selected_line_developement_dataset, selected_line_monitoring_dataset)
    full_data <- merge(x = full_dataset, y = selected_lines_all, by = "datestamp", all = TRUE)
    # weighted average
    full_data$model_weighted <- full_data$no_cases * full_data$model_performance
    full_data1 <- subset(full_data, select=c("max_error", "no_cases", "no_cases_selected",
                                             "selected_prop", "model_performance", "model_weighted"))
    agg_data1 <- aggregate(full_data1, by=list(Dataset=full_data$Type), na.rm=TRUE, FUN=sum)
    agg_data1$model_weighted_error <- agg_data1$model_weighted / agg_data1$no_cases
    agg_data1 <- subset(agg_data1, select=c("Dataset", "model_weighted_error"))
    agg_data1$model_weighted_error <- round(agg_data1$model_weighted_error, digit=2)
    names(agg_data1)[names(agg_data1) == "model_weighted_error"] <- "Model performance - weighted average"
      
    # aggregate on dataset type
    agg_data <- aggregate(full_data, by=list(Dataset=full_data$Type), na.rm=TRUE, FUN=mean)
    agg_data <- subset(agg_data, select=c("Dataset", "max_error", "no_cases", "no_cases_selected",
                                            "selected_prop", "model_performance"))
    agg_data$max_error <- round(agg_data$max_error)
    agg_data$no_cases <- round(agg_data$no_cases)
    agg_data$no_cases_selected <- round(agg_data$no_cases_selected)
    agg_data$selected_prop <- round(agg_data$selected_prop, digit=2)
    agg_data$model_performance <- round(agg_data$model_performance, digit=2)
      
    # rename columns
    names(agg_data)[names(agg_data) == "max_error"] <- "No of errors"
    names(agg_data)[names(agg_data) == "no_cases"] <- "No of cases"    
    names(agg_data)[names(agg_data) == "no_cases_selected"] <- "No of cases selected" 
    names(agg_data)[names(agg_data) == "selected_prop"] <- "[%] selected population"
    names(agg_data)[names(agg_data) == "model_performance"] <- "Model performance - plain average"
      
    final_data <- merge(x = agg_data, y = agg_data1, by = "Dataset", all = TRUE)
    results <- final_data # full_data, agg_data, agg_data1, final_data
    #developement_dataset, monitoring_dataset, selected_line_developement_dataset, selected_line_monitoring_dataset)
  
  return(results)
}
