function(dataset,time_aggregation,probs,selected_sample = T){
  dataset$datestamp= floor_date(dataset$datestamp,unit = time_aggregation,week_start = 4)
  dataset = as.data.frame(dataset%>%
                            group_by(datestamp)%>%
                            mutate(Label = as.character(Label)))
  if(selected_sample){
    dataset = as.data.frame(dataset%>%
                              filter(Score > quantile(Score,
                                                      probs = 1-probs)))
  }
                            
  dataset$Label[is.na(dataset$Label)] = 'Missing value'
  dataset$Label[dataset$Label=='1']='Error found'
  dataset$Label[dataset$Label=='0']='No error'
  grouped_Label=table(dataset$datestamp,dataset$Label)
  grouped_Label=prop.table(grouped_Label,margin = 1)
  grouped_Label=as.data.frame(grouped_Label)
  grouped_Label=reshape(grouped_Label,timevar = 'Var2',idvar = 'Var1',direction='wide')
  colnames(grouped_Label)=c("Date","Effor found","Missing value","No error")
  histogram=plot_ly(type="bar",textposition = 'auto')
  
  for (i in 2:length(grouped_Label)){
    histogram=histogram%>%
      add_trace(x=grouped_Label[,1],
                y=grouped_Label[,i],
                name = colnames(grouped_Label)[i])
  }
  histogram=histogram%>%
    layout(yaxis=list(title="% of cases for each group"),xaxis=list(title="Date"),
           title=ifelse(selected_sample,
                        "Error ratio in selected sample",
                        'Error ratio in whole population'),
           barmode = 'stack')
  histogram
}
