dist_check_new <- function(dataset, time_feat, feature, time_frame, selected_time, selected_lag_time)
    
  {
  
  # standarize time column and extract subset for selected time periods
  dataset[,time_feat] <- floor_date(dataset[,time_feat], unit=time_frame,week_start = 4)
  dataset_selected_time <- dataset[which(dataset[,time_feat]==selected_time),]
  dataset_selected_lag_time <- dataset[which(dataset[,time_feat]==selected_lag_time),]

  # decide if feature is continuous or discrete
  if (is.numeric(dataset[,feature])) {
    # for continuous extract feature column
    feature_selected_time <- dataset_selected_time[,feature]
    feature_selected_lag_time <- dataset_selected_lag_time[,feature]
  } else {
    # for discrete extract number of obs for unique categories
    unique_vals <- sort(unique(dataset[feature])[!is.na(unique(dataset[feature]))])
    feature_selected_time <- c()
    feature_selected_lag_time <- c()
    for (i in 1:length(unique_vals)) {
      feature_selected_time[unique_vals[i]] <- sum(dataset_selected_time[feature] == unique_vals[i])
      feature_selected_lag_time[unique_vals[i]] <- sum(dataset_selected_lag_time[feature] == unique_vals[i])
    }
    # add sum of NA observations (NA treaded as seperated category) and get share of each category
    feature_selected_time['NA'] <- sum(is.na(dataset_selected_time$feature))
    feature_selected_time <- round(feature_selected_time / nrow(dataset_selected_time), digits = 4)
    feature_selected_lag_time['NA'] <- sum(is.na(dataset_selected_lag_time$feature))
    feature_selected_lag_time <- round(feature_selected_lag_time / nrow(dataset_selected_lag_time), digits = 4)
    }
    
    # If there is no data in t or t-1 period raise warning
    if (length(feature_selected_time) == 0) {
      decision <- paste("No enough data for first period ", selected_time, " for ", feature, sep="")
    } else if (length(feature_selected_lag_time) == 0) {
      decision <- paste("No enough data for second period ", selected_lag_time, " for ", feature, sep="")

    # If there is data for both selected periods run the test and print decision  
    } else {
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
    }
     return(decision)
   }
