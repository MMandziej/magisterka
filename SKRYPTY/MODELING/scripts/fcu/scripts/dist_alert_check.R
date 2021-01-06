dist_alert_check <- function(results,
                             dataset,
                             time_feat='BackupTime',
                             time_frame='days')
  {
  
  unique_intervals <- sort(unique(results$pqc_timestamp))
  mean_lastn <- mean(results[results$pqc_timestamp == unique_intervals[length(unique_intervals)], ][['pqc']])
  quants <- quantile(results[results$pqc_timestamp < unique_intervals[length(unique_intervals)], ][['pqc']], probs=c(0.25, 0.75))
  
  if(mean_lastn > quants[1] & mean_lastn < quants[2] ) {
    alert = HTML('<font color=\"#2ab860\"><b>Average score from current scoring within IQR on full production backlog.</b></font>')
  } else {
    alert = HTML('<font color=\"#db0000\"><b>Average score from current scoring outside IQR on full production backlog.</b></font>')
  }
  
  features_intervals <- sort(unique(dataset$BackupTime))
  features <- c(
    "TLAssignedName", "ProcessingUnit", "CDDRiskLevel", "FATCA", "CRS", "ScreenedParties",
    "OwnershipLayers", "ESR", "PartyType", "GroupCases", "FirstGroupCase",
    "PopulationMatch", "HourNumeric", "Weekday",
    "Cases_last_5_days_of_DR", "Cases_last_5_days_of_PC", "Cases_last_30_days_of_DR",
    "Cases_last_30_days_of_PC", "Minor_last_5_checklistsDR", "Major_last_5_checklistsDR",
    "Critical_last_5_checklistsDR", "Minor_last_10_checklistsDR", "Major_last_10_checklistsDR",
    "Critical_last_10_checklistsDR", "Minor_last_5_checklistsPC", "Major_last_5_checklistsPC",
    "Critical_last_5_checklistsPC", "Minor_last_10_checklistsPC", "Major_last_10_checklistsPC",
    "Critical_last_10_checklistsPC", "ProjectExperience", "TeamExperience")
  count_diff = 0
  count_viol = 0  
  for(i in features) {
    decision <- tryCatch(
      {
        dist_check_new(dataset = general_data,
                       time_feat = 'BackupTime',
                       feature = i,
                       time_frame = 'days', #weeks/days
                       selected_time = as.POSIXct(features_intervals[length(features_intervals)]), # as.POSIXct
                       selected_lag_time = as.POSIXct(features_intervals[length(features_intervals)-1])) # as.POSIXct
      },
      error=function(cond) {
        #message(cond)
        count_viol = count_viol + 1
        return("Statistical assumptions for Chi-Squared homogenity tests were violated")
      })
    
    if (grepl("Statistically significant difference between", decision) == T) {
      count_diff = count_diff + 1
    } else if (grepl("assumptions for Chi-Squared homogenity tests were violated", decision) == T) {
      count_viol = count_viol + 1
    }
  }
  
  if(count_viol > 0.2 * length(features)) {
    out1 <- HTML(paste("<font color=\"#eb9234\"><b>Chi-square / Kolmogorov Smirnovow test assumptions violated for ",
                  count_viol, " out of ", length(features), " features in current and lagged period.</b></font>"))
  } else {
    #out1 <- HTML("<font color=\"#2ab860\"><b>Chi-square / Kolmogorov Smirnovow tests assumptions satisfied.</b></font>")
    out1 <- ""
  }
  
  if(count_diff > 0.2 * length(features)) {
    if(out1 == "") { 
      out2 <- HTML(paste("<font color=\"#db0000\"><b>Detected statistically significant difffenrce in distribution for ",
                    count_diff, " out of ", length(features), " features.</b></font>"))
    } else {
      out2 <- HTML("<font color=\"#2ab860\"><b>Features distribution stable between current and lagged periods.</b></font>")
    }
  } else {
    out2 <- ""
  }
  valuelist <- list(out1, out2, alert)
  return(valuelist)
}
