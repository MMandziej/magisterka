boxplot_classes = function(dataset,time_feature='datestamp',feature,Label='all',time_frame='month'){
  if(time_feature!='datestamp'){
    colnames(dataset)[which(colnames(dataset)==time_feature)]='datestamp'
  }
  dataset=as.data.frame(dataset)
  dataset[,time_feature]=floor_date(dataset[,time_feature],unit = time_frame)
  
  if(is.numeric(dataset[,feature])){
    results = plot_ly(dataset,
                      y=dataset[,feature],
                      x=~datestamp,
                      type='box')%>%
      layout(yaxis=list(title="Distribution of cases for each group"),xaxis=list(title="Date"),
             title=paste("Boxplot of ",feature," vs time.",sep = ""))
  }
  else{
    results=plot_ly(dataset,
                    x = ~datestamp,
                    type = 'histogram',
                    color=dataset[,feature]
                    )%>%
      layout(yaxis=list(title="Number of cases for each group"),xaxis=list(title="Date"),
             title=paste("Barchart of ",feature," vs time.",sep = ""))
  }
  return(results)
}
  