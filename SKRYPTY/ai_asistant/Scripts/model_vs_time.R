function(PQC_results,RQC_results,threshold,type,time_frame='days'){
  PQC_results$datestamp=floor_date(PQC_results$datestamp,unit = time_frame)
  RQC_results$datestamp=floor_date(RQC_results$datestamp,unit = time_frame)
  full_dataset = rbind(PQC_results,RQC_results)
  if(type=="model_performance"){
    #
    #full_dataset=full_dataset%>%
    #  group_by(datestamp,Label)%>%
    #  summarize(no_cases=n())
    #full_dataset=as.data.frame(full_dataset)
    
    barchart_data_PQC = PQC_results%>%
        group_by(datestamp,Label)%>%
        summarize(no_cases=n())
    
    barchart_data_RQC = RQC_results%>%
      group_by(datestamp,Label)%>%
      summarize(no_cases=n())

    max_error_PQC=PQC_results%>%
      group_by(datestamp)%>%
      summarize(max_error_PQC=sum(Label))
    max_error_RQC=RQC_results%>%
      group_by(datestamp)%>%
      summarize(max_error_RQC=sum(Label))
    
    max_error_PQC=as.data.frame(max_error_PQC)
    max_error_RQC=as.data.frame(max_error_RQC)
    
    PQC_results=PQC_results[1:round((nrow(PQC_results)*threshold)),]
    RQC_results=RQC_results[1:round((nrow(RQC_results)*threshold)),]
    
    barchart_data_RQC_results_selected = RQC_results%>%
      group_by(datestamp)%>%
      summarize(no_cases_selected=n())
    
    barchart_data_PQC_results_selected = PQC_results%>%
      group_by(datestamp)%>%
      summarize(no_cases_selected=n())
    
    PQC_results=PQC_results%>%
      group_by(datestamp)%>%
      summarize(model_performance=sum(Label))
    RQC_results=RQC_results%>%
      group_by(datestamp)%>%
      summarize(model_performance=sum(Label))
    
    PQC_results=as.data.frame(PQC_results)
    RQC_results=as.data.frame(RQC_results)
    
    all_cases_PQC = barchart_data_PQC%>%
      group_by(datestamp)%>%
      summarize(no_cases=sum(no_cases))
    
    all_cases_RQC = barchart_data_RQC%>%
      group_by(datestamp)%>%
      summarize(no_cases=sum(no_cases))
    
    selected_line_RQC_results = merge(x = all_cases_RQC,y = barchart_data_RQC_results_selected,by = 'datestamp',all.x = T)
    selected_line_RQC_results[is.na(selected_line_RQC_results)]=0
    selected_line_RQC_results$selected_prop=100*selected_line_RQC_results$no_cases_selected/selected_line_RQC_results$no_cases
    
    selected_line_PQC_results = merge(x = all_cases_PQC,y = barchart_data_PQC_results_selected,by = 'datestamp',all.x = T)
    selected_line_PQC_results[is.na(selected_line_PQC_results)]=0
    selected_line_PQC_results$selected_prop=100*selected_line_PQC_results$no_cases_selected/selected_line_PQC_results$no_cases
    
    
    
    
    
    
    
    
    PQC_results=merge(x = max_error_PQC,y = PQC_results,by = 'datestamp',all.x = T)
    PQC_results[is.na(PQC_results)]=0
    PQC_results$model_performance=100*PQC_results$model_performance/PQC_results$max_error_PQC
    
    RQC_results=merge(x = max_error_RQC,y = RQC_results,by = 'datestamp',all.x = T)
    RQC_results[is.na(RQC_results)]=0
    RQC_results$model_performance=100*RQC_results$model_performance/max_error_RQC$max_error_RQC
    
    results=plot_ly()%>%
      add_trace(x=PQC_results$datestamp,y=PQC_results[,type],type = 'scatter',mode='lines',name='Train results',line=list(color='#E86607'))%>%
      add_trace(x=RQC_results$datestamp,y=RQC_results[,type],type = 'scatter',mode='lines',name='Test results',line=list(color='#20C50D'))%>%
      add_trace(x=selected_line_PQC_results$datestamp,y=selected_line_PQC_results$selected_prop,type = 'scatter',mode='lines',name='Train selected proportion',line=list(color='#E86607', dash = 'dash'))%>%
      add_trace(x=selected_line_RQC_results$datestamp,y=selected_line_RQC_results$selected_prop,type = 'scatter',mode='lines',name='Test selected proportion',line=list(color='#20C50D', dash = 'dash'))%>%
      add_trace(yaxis='y2',
                x = barchart_data_PQC$datestamp,
                y=barchart_data_PQC$no_cases, 
                #color=barchart_data_RQC$Label,
                name = 'Number of scored cases test', 
                type = 'bar',
                marker = list(
                  color = barchart_data_PQC$Label,
                  colorscale='Picnic')
      )%>%      hide_colorbar()%>%
      add_trace(yaxis='y2',
                x = barchart_data_RQC$datestamp,
                y=barchart_data_RQC$no_cases, 
                #color=barchart_data_RQC$Label,
                name = 'Number of scored cases test', 
                type = 'bar',
                marker = list(
                  color = barchart_data_RQC$Label,
                  colorscale='Portland')
                )%>% 
      hide_colorbar()%>%
      layout(legend = list(y = -0.05,orientation = "h",   # show entries horizontally
                           xanchor = "center",  # use center of legend as anchor
                           x = 0.5),
             xaxis = list(range = c(min(full_dataset$datestamp), max(full_dataset$datestamp)+15*86400)),
             title=paste("Changes of model performance within the time.",sep = ""),
             yaxis=list(side = 'left', overlaying = "y2",ticksuffix ="%",title=paste('Percent of errors found in ',100*threshold,'% of population'),showgrid = T, zeroline = FALSE),
             yaxis2 = list(side = 'right', title = 'No cases', showgrid = F, zeroline = FALSE))
    
  }else if(type=="part_of_population"){
    #full_dataset = rbind(PQC_results,RQC_results)
    #full_dataset=full_dataset%>%
    #  group_by(datestamp,Label)%>%
    #  summarize(no_cases=n())
    #full_dataset=as.data.frame(full_dataset)
    
    barchart_data_PQC = PQC_results%>%
      group_by(datestamp,Label)%>%
      summarize(no_cases=n())
    
    barchart_data_RQC = RQC_results%>%
      group_by(datestamp,Label)%>%
      summarize(no_cases=n())
    
    
    max_error_PQC=PQC_results%>%
      group_by(datestamp)%>%
      summarize(max_error_PQC=sum(Label))
    max_error_RQC=RQC_results%>%
      group_by(datestamp)%>%
      summarize(max_error_RQC=sum(Label))
    
    max_error_PQC=as.data.frame(max_error_PQC)
    max_error_RQC=as.data.frame(max_error_RQC)

    
    PQC_results=PQC_results%>%
      group_by(datestamp)%>%
      filter(Score>quantile(Score,probs = 1-threshold))%>%
      summarize(part_of_population=sum(Label))
    RQC_results=RQC_results%>%
      group_by(datestamp)%>%
      filter(Score>quantile(Score,probs = 1-threshold))%>%
      summarize(part_of_population=sum(Label))
    
    PQC_results=as.data.frame(PQC_results)
    RQC_results=as.data.frame(RQC_results)
    
    PQC_results=merge(x = max_error_PQC,y = PQC_results,by = 'datestamp',all.x = T)
    PQC_results[is.na(PQC_results)]=0
    PQC_results$part_of_population=100*PQC_results$part_of_population/PQC_results$max_error_PQC
    PQC_results[is.na(PQC_results)]=100
    
    RQC_results=merge(x = max_error_RQC,y = RQC_results,by = 'datestamp',all.x = T)
    RQC_results[is.na(RQC_results)]=0
    RQC_results$part_of_population=100*RQC_results$part_of_population/max_error_RQC$max_error_RQC
    RQC_results[is.na(RQC_results)]=100
    
    results=plot_ly()%>%
      add_trace(x=PQC_results$datestamp,y=PQC_results[,type],type = 'scatter',mode='lines',name='Train results',line=list(color='#E86607'))%>%
      add_trace(x=RQC_results$datestamp,y=RQC_results[,type],type = 'scatter',mode='lines',name='Test results',line=list(color='#20C50D'))%>%
      #add_trace(yaxis='y2',x = full_dataset$datestamp,y=full_dataset$no_cases, color=full_dataset$Label,name = 'Number of scored cases', type = 'bar')%>% 
      #hide_colorbar()%>%
      add_trace(yaxis='y2',
                x = barchart_data_PQC$datestamp,
                y=barchart_data_PQC$no_cases, 
                #color=barchart_data_RQC$Label,
                name = 'Number of scored cases test', 
                type = 'bar',
                marker = list(
                  color = barchart_data_PQC$Label,
                  colorscale='Picnic')
      )%>%      hide_colorbar()%>%
      add_trace(yaxis='y2',
                x = barchart_data_RQC$datestamp,
                y=barchart_data_RQC$no_cases, 
                #color=barchart_data_RQC$Label,
                name = 'Number of scored cases test', 
                type = 'bar',
                marker = list(
                  color = barchart_data_RQC$Label,
                  colorscale='Portland')
      )%>% 
      hide_colorbar()%>%
      layout(legend = list(y = -0.05,orientation = "h",   # show entries horizontally
                           xanchor = "center",  # use center of legend as anchor
                           x = 0.5),
             xaxis = list(range = c(min(full_dataset$datestamp), max(full_dataset$datestamp)+15*86400)),
             title=paste("Changes of model performance within the time.",sep = ""),
             yaxis=list(side = 'left', overlaying = "y2",ticksuffix ="%",title=paste('Percent of errors found in ',100*threshold,'% of population'),showgrid = T, zeroline = FALSE),
             yaxis2 = list(side = 'right', title = 'No cases', showgrid = F, zeroline = FALSE))
    
  }else if(type=="error_ratio"){
    
    PQC_results=PQC_results[1:(nrow(PQC_results)*threshold),]
    RQC_results=RQC_results[1:(nrow(RQC_results)*threshold),]
    
    
    PQC_results=PQC_results%>%
      group_by(datestamp)%>%
      summarize(error_ratio=sum(Label)/n())
    
    RQC_results=RQC_results%>%
      group_by(datestamp)%>%
      summarize(error_ratio=sum(Label)/n())
    
    
    PQC_results=as.data.frame(PQC_results)
    RQC_results=as.data.frame(RQC_results)
    
    results=plot_ly(type = 'scatter',mode='lines')%>%
      add_trace(x=PQC_results$datestamp,y=PQC_results[,type],mode='lines',name='Train results')%>%
      add_trace(x=RQC_results$datestamp,y=RQC_results[,type],mode='lines',name='Test results')%>%
      layout(legend=list(orientation = 'h'),title=paste("Changes of ",type," metric within the time.",sep = ""),yaxis=list(title=type))
    
  }else if(type == 'average_score'){
    PQC_results_0=PQC_results[which(PQC_results$Label == 0),]%>%
      group_by(datestamp)%>%
      summarize(average_score=mean(Score))
    PQC_results_1=PQC_results[which(PQC_results$Label == 1),]%>%
      group_by(datestamp)%>%
      summarize(average_score=mean(Score))
    
    RQC_results_0=RQC_results[which(RQC_results$Label == 0),]%>%
      group_by(datestamp)%>%
      summarize(average_score=mean(Score))
    RQC_results_1=RQC_results[which(RQC_results$Label == 1),]%>%
      group_by(datestamp)%>%
      summarize(average_score=mean(Score))
    
    PQC_results_0=as.data.frame(PQC_results_0)
    PQC_results_1=as.data.frame(PQC_results_1)
    RQC_results_0=as.data.frame(RQC_results_0)
    RQC_results_1=as.data.frame(RQC_results_1)
    
    results = plot_ly(x = PQC_results_0$datestamp, y = PQC_results_0$average_score, name = 'No rework train', type = 'scatter', mode = 'lines') %>%
      add_trace(x = PQC_results_1$datestamp, y = PQC_results_1$average_score, name = 'Rework train', type = 'scatter', mode = 'lines')%>%
      add_trace(x = RQC_results_0$datestamp, y = RQC_results_0$average_score, name = 'No rework test', type = 'scatter', mode = 'lines')%>%
      add_trace(x = RQC_results_1$datestamp, y = RQC_results_1$average_score, name = 'Rework test', type = 'scatter', mode = 'lines')
    
    
    
  }else{
    PQC_results$Predicted=0
    PQC_results$Predicted[1:nrow(PQC_results)*threshold]=1
    
    RQC_results$Predicted=0
    RQC_results$Predicted[1:nrow(RQC_results)*threshold]=1
    
    
    PQC_results=PQC_results%>%
      group_by(datestamp)%>%
      summarize(acc=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$overall['Accuracy'],
                auc=fastAUC(probs = Score,class = Label),
                F1=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$byClass['F1'])
    
    
    RQC_results=RQC_results%>%
      group_by(datestamp)%>%
      summarize(acc=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$overall['Accuracy'],
                auc=fastAUC(probs = Score,class = Label),
                F1=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$byClass['F1'])
    
    
    
    PQC_results=as.data.frame(PQC_results)
    RQC_results=as.data.frame(RQC_results)
    
    results=plot_ly(type = 'scatter',mode='lines')%>%
      add_trace(x=PQC_results$datestamp,y=PQC_results[,type],mode='lines',name='Train results')%>%
      add_trace(x=RQC_results$datestamp,y=RQC_results[,type],mode='lines',name='Test results')%>%
      layout(legend=list(orientation = 'h'),title=paste("Changes of ",type," metric within the time.",sep = ""),yaxis=list(title=type))
    
    
  }
  
  
  
  
  return(results)
}
