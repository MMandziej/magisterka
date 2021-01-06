function(dataset,feature,threshold){
  dataset = dataset[order(dataset[,feature],decreasing = F),]
  plot_ly(dataset,
          y=dataset[,feature],
          hoverinfo = 'y',
          type = 'scatter',
          name = 'Model scores for the cases')%>%
    add_lines(x = 1:nrow(dataset),
              y=quantile(dataset[,feature],
                         probs = 1-threshold),
              name = paste('Threshold to cover',100*threshold,'% of cases'))%>%
    layout(legend = list(orientation = 'h'),
           xaxis = list(
             showticklabels = FALSE),
           yaxis = list(
             title = 'Model score'
           ),
           title = list(
             text = paste('Distribution of scores from',
                          substr(min(dataset$datestamp),1,10),
                          'to',
                          substr(max(dataset$datestamp),1,10))
           ))
}
