dist_check_new <- function(dataset,
                           time_feat,
                           feature,
                           time_frame='days',
                           selected_time,
                           selected_lag_time)
  # For continuous data Kolmogorov-Smirnov test can be used to asses whether feature distribution in
  # two periods. For categorical features Chi-Squared homogenity test can be used (if each cell has at least 5 obs)
  {
  
  num_cols <- c("OwnershipLayers", "ScreenedParties", "NO_errors_last_5_days_DR", "NO_cases_last_5_days_DR",
                "NO_errors_last_month_DR", "NO_cases_month_DR", "Hour_numeric", "Group_cases", "TeamExperience",
                "ProjectExperience", "Population_match", "Cases_last_5_days_of_DR", "Cases_last_5_days_of_PC",
                "Cases_last_30_days_of_DR", "Cases_last_30_days_of_PC", "Minor_last_5_checklistsDR",
                "Major_last_5_checklistsDR", "Critical_last_5_checklistsDR", "Minor_last_10_checklistsDR",
                "Major_last_10_checklistsDR", "Critical_last_10_checklistsDR", "Minor_last_5_checklistsPC",
                "Major_last_5_checklistsPC", "Critical_last_5_checklistsPC", "Minor_last_10_checklistsPC",
                "Major_last_10_checklistsPC", "Critical_last_10_checklistsPC")
  # standarize time column and extract subset for selected time periods
  dataset[,time_feat] <- floor_date(dataset[,time_feat], unit=time_frame)
  dataset_selected_time <- dataset[which(dataset[,time_feat]==selected_time),]
  dataset_selected_lag_time <- dataset[which(dataset[,time_feat]==selected_lag_time),]

  # decide if feature is continuous or discrete
  if (feature %in% num_cols) {
    # for continuous extract feature column
    feature_selected_time <- dataset_selected_time[,feature]
    feature_selected_lag_time <- dataset_selected_lag_time[,feature]
    # run Kolmogorov-Smirnov test
    results <- ks.test(feature_selected_time, feature_selected_lag_time)
    if (results$p.value < 0.05) {
      decision <- paste("Statistically significant difference between ",
                        selected_time," and ", selected_lag_time, " for ", feature, 
                        " (p-value = ", round(results$p.value, 5), ")", sep="")
    } else {
      decision <- paste("No statistically significant difference between ",
                        selected_time," and ", selected_lag_time, " for ", feature,
                        " (p-value = ", round(results$p.value, 5), ")", sep="")
    }
    
  } else {
    # for discrete extract number of obs for unique categories
    unique_vals_time <- sort(unique(dataset_selected_time[feature])[!is.na(unique(dataset_selected_time[feature]))])
    unique_vals_lag <- sort(unique(dataset_selected_lag_time[feature])[!is.na(unique(dataset_selected_lag_time[feature]))])
    unique_vals <- unique(c(unique_vals_time, unique_vals_lag))
    
    # vlookup for number of obs for each category
    feature_selected_time <- c()
    feature_selected_lag_time <- c()
    for (i in 1:length(unique_vals)) {
      feature_selected_time[unique_vals[i]] <- sum(dataset_selected_time[feature] == unique_vals[i])
      feature_selected_lag_time[unique_vals[i]] <- sum(dataset_selected_lag_time[feature] == unique_vals[i])
    }
    
    # check statistical assumption on minimum 5 obs in each class
    if (any(feature_selected_time < 5) | any(feature_selected_lag_time < 5)) {
      decision <- paste("Statistical assumptions for Chi-Squared homogenity tests were violated.
                        Cannot run the test for selected periods for ", feature, sep="")
    } else {
      # If assumptions met run Chi-Square homogenity test
      input_table <- rbind(feature_selected_time, feature_selected_lag_time)
      chisq_results <- chisq.test(input_table)
      if (chisq_results$p.value < 0.05) {
        decision <- paste("Detected statistically significant difference between ",
                          selected_time," and ", selected_lag_time, " for ", feature,
                          " (p-value = ", round(chisq_results$p.value, 5), ")", sep="")
      } else {
        decision <- paste("No statistically significant difference between ",
                          selected_time," and ", selected_lag_time, " for ", feature,
                          " (p-value = ", round(chisq_results$p.value, 5), ")", sep="")
      }
    }
  }
    
    # If there is no data in chosen period or lag period override decision and print warning
  if (length(feature_selected_time) == 0) {
    decision <- paste("No enough data for first period ", selected_time, " for ", feature, sep="")
    } else if (length(feature_selected_lag_time) == 0) {
      decision <- paste("No enough data for second period ", selected_lag_time, " for ", feature, sep="")
    # If there is data for both selected periods print decision from test
  }
  return(decision)
}
