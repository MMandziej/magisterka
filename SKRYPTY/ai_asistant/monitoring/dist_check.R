dist_check <- function(dataset, time_feat, feature, time_frame, selected_time)
    
  {
    dataset[,time_feat] <- floor_date(dataset[,time_feat], unit=time_frame)
    dataset_selected_time <- dataset[which(dataset[,time_feat]==selected_time),]
    
    u_times <- sort(unique(dataset[,time_feat]))
    u_times_index <- which(u_times==selected_time)
    
    lag1_time <- u_times[u_times_index-1]
    dataset_lag1_time <- dataset[which(dataset[,time_feat]==lag1_time),]
    
    feature_selected_time <- dataset_selected_time[,feature]
    feature_lag1_time <- dataset_lag1_time[,feature]
    
    # If there is no data in t or t-1 period raise warning
    if (length(feature_selected_time) == 0) {
      decision <- paste("No enough data for period ", selected_time, " for ", feature, sep="")
    } else if (length(feature_lag1_time) == 0) {
      decision <- paste("No enough data for lagged period ", lag1_time, " for ", feature, sep="")

    # If there is enough data run the test and print decision  
    } else {
      results <- ks.test(feature_selected_time, feature_lag1_time)
      if (results$p.value < 0.05) {
        decision <- paste("Statistically significant difference between ",
                          selected_time," and ", lag1_time, " for ", feature, 
                          " (p-value = ", round(results$p.value, 5), ")", sep="")
      } else {
        decision <- paste("No statistically significant difference between ",
                          selected_time," and ", lag1_time, " for ", feature,
                          " (p-value = ", round(results$p.value, 5), ")", sep="")
      }
    }
     return(decision)
   }
