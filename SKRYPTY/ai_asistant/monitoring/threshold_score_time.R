function(dataset, time_aggregation,probs = 0.46){
  dataset$datestamp= floor_date(dataset$datestamp,unit = time_aggregation,week_start = 4)
  dataset = as.data.frame(dataset%>%
    group_by(datestamp)%>%
    summarize(Score = quantile(Score,
                               probs = 1-probs)))
  plot_ly(dataset,
          x=~datestamp,
          y=~Score,
          type = 'scatter',
          mode = 'lines')
  
}