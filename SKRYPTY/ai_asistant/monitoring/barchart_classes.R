barchart_classes <- function(dataset,time_feature='datestamp',feature,Label='all',time_frame='month',prop=T){
  if(time_feature!='datestamp'){
    colnames(dataset)[which(colnames(dataset)==time_feature)]='datestamp'
    time_feature='datestamp'
  }
  dataset = dataset[complete.cases(dataset[,feature]),]
  if(Label=='all'){
    if(is.numeric(dataset[,feature])){
      dataset[,time_feature]=floor_date(dataset[,time_feature], unit = time_frame, week_start = 1)
      dataset[,feature]=quantcut(dataset[,feature],q=5)
      test_1=table(dataset[,time_feature],dataset[,feature])
      if(prop==T){
        test_1=prop.table(test_1,margin = 1)
      }
      test_1=as.data.frame(test_1)
      test_1=reshape(test_1,timevar = 'Var2',idvar = 'Var1',direction='wide')
      colnames(test_1)=c("Date","Q1","Q2","Q3","Q4","Q5")[1:(length(unique(dataset[,feature]))+1)]
      
      test_plot=plot_ly(type="bar",textposition = 'auto')
      
      for (i in 2:length(test_1)){
        test_plot=test_plot%>%
          add_trace(x=test_1[,1],
                    y=test_1[,i],
                    name = colnames(test_1)[i])
      }
      test_plot=test_plot%>%
        layout(yaxis=list(title="% of cases for each group"),xaxis=list(title="Date"),
               title=paste("Barchart of ",feature," vs time.",sep = ""))
      if(prop==T){
        test_plot=test_plot%>%
          layout(barmode='stack')
      }
    }else{
      dataset[,time_feature]=floor_date(dataset[,time_feature],unit = time_frame)
      test_1=table(dataset[,time_feature],dataset[,feature])
      if(prop==T){
        test_1=prop.table(test_1,margin = 1)
      }
      test_1=as.data.frame(test_1)
      test_1=reshape(test_1,timevar = 'Var2',idvar = 'Var1',direction='wide')
      colnames(test_1)=c("Date",unique(dataset[,feature]))
      
      test_plot=plot_ly(type="bar",textposition = 'auto')
      
      for (i in 2:length(test_1)){
        test_plot=test_plot%>%
          add_trace(x=test_1[,1],
                    y=test_1[,i],
                    name = colnames(test_1)[i])
      }
      test_plot=test_plot%>%
        layout(yaxis=list(title="% of cases for each group"),xaxis=list(title="Date"),
               title=paste("Barchart of ",feature," vs time.",sep = ""))
      if(prop==T){
        test_plot=test_plot%>%
          layout(barmode='stack')
      }
    }
  }else{
    if(is.numeric(dataset[,feature])){
      dataset[,time_feature]=floor_date(dataset[,time_feature],unit = time_frame)
      dataset[,feature]=quantcut(dataset[,feature],q=5)
      test_1=table(dataset[which(dataset[,'Label']==Label),time_feature],dataset[which(dataset[,'Label']==Label),feature])
      if(prop==T){
        test_1=prop.table(test_1,margin = 1)
      }
      test_1=as.data.frame(test_1)
      test_1=reshape(test_1,timevar = 'Var2',idvar = 'Var1',direction='wide')
      colnames(test_1)=c("Date","Q1","Q2","Q3","Q4","Q5")[1:(length(unique(dataset[,feature]))+1)]
      
      test_plot=plot_ly(type="bar",textposition = 'auto')
      
      for (i in 2:length(test_1)){
        test_plot=test_plot%>%
          add_trace(x=test_1[,1],
                    y=test_1[,i],
                    name = colnames(test_1)[i])
      }
      test_plot=test_plot%>%
        layout(yaxis=list(title="% of cases for each group"),xaxis=list(title="Date"),
               title=paste("Barchart of ",feature," vs time.",sep = ""))
      if(prop==T){
        test_plot=test_plot%>%
          layout(barmode='stack')
      }
    }else{
      dataset[,time_feature]=floor_date(dataset[,time_feature],unit = time_frame)
      test_1=table(dataset[which(dataset[,'Label']==Label),time_feature],dataset[which(dataset[,'Label']==Label),feature])
      if(prop==T){
        test_1=prop.table(test_1,margin = 1)
      }
      test_1=as.data.frame(test_1)
      test_1=reshape(test_1,timevar = 'Var2',idvar = 'Var1',direction='wide')
      colnames(test_1)=c("Date",unique(dataset[,feature]))
      
      test_plot=plot_ly(type="bar",textposition = 'auto')
      
      for (i in 2:length(test_1)){
        test_plot=test_plot%>%
          add_trace(x=test_1[,1],
                    y=test_1[,i],
                    name = colnames(test_1)[i])
      }
      test_plot=test_plot%>%
        layout(yaxis=list(title="% of cases for each group"),xaxis=list(title="Date"),
               title=paste("Barchart of ",feature," vs time.",sep = ""))
      if(prop==T){
        test_plot=test_plot%>%
          layout(barmode='stack')
      }
    }
  }
  
  return(test_plot)
}