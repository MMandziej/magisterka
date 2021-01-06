calculate_production_savings = function(no_cases_discarded = 50,
                                        avg_proc_time = 1,
                                        cost_rate = 300) {
  metrics <- c("Time (hours)", "Cash (k PLN)", "Cases discarded")
  savings <- c(no_cases_discarded * avg_proc_time,
               no_cases_discarded * avg_proc_time * cost_rate / 1000,
               no_cases_discarded)
  
  output_table <- data.frame(metrics, savings)
  names(output_table)[names(output_table) == "metrics"] <- "Metric"
  names(output_table)[names(output_table) == "savings"] <- "Savings"
  
  return(output_table)
}
