function(PQC_results,RQC_results,threshold,type){
  if(type=='error_ratio'){
    PQC_value=100*round(sum(PQC_results[1:(nrow(PQC_results)*threshold),'Label'])/
                          (nrow(PQC_results)*threshold),4)
    RQC_value=100*round(sum(RQC_results[1:(nrow(RQC_results)*threshold),'Label'])/
                          (nrow(RQC_results)*threshold),4)
    result=plot_ly()%>%
      add_trace(x=0,y=RQC_value,type='bar',hoverinfo='text',text=paste(RQC_value,'%',sep=''))%>%
      add_trace(x=seq((-0.5),0.5,by = 0.05),
                y=PQC_value,type='scatter',
                mode='lines',
                hoverinfo='text',
                text=paste(PQC_value,'%',sep=''))%>%
      #add_segments(x=-0.5,xend = 0.5,y=PQC_value, yend=PQC_value,line=list(color="#E88D14"),showlegend=F)%>%
      layout(showlegend=F,
             xaxis=list(title=HTML("<b>Test data</b>"),zeroline=F,showgrid=F,range=c(-0.5,0.5),showticklabels=F),
             yaxis=list(ticksuffix ="%",title="Error ratio in selected sample"),
             annotations=list(
               xref='x',
               yref='y',
               x=0.42,
               ax=20,
               ay=-40,
               y=PQC_value,
               text=HTML('<b>Train data</b>')
             ))
    
  }else if(type=='model_performance'|type=='part_of_population'){
    PQC_value=100*round(PQC_results[floor((nrow(PQC_results)*threshold)),'y_coordinates'],4)
    RQC_value=100*round(sum(RQC_results[1:(nrow(RQC_results)*threshold),'Label'])/sum(RQC_results[,'Label']),4)
    result=plot_ly()%>%
      add_trace(x=0,y=RQC_value,type='bar',hoverinfo='text',text=paste(RQC_value,'%',sep=''))%>%
      add_trace(x=seq((-0.5),0.5,by = 0.05),y=PQC_value,type='scatter',mode='lines', hoverinfo='text',text=paste(PQC_value,'%',sep=''))%>%
      #add_segments(x=-0.5,xend = 0.5,y=PQC_value, yend=PQC_value,line=list(color="#E88D14"),showlegend=F)%>%
      layout(showlegend=F,
             xaxis=list(title=HTML("<b>Test data</b>"),zeroline=F,showgrid=F,range=c(-0.5,0.5),showticklabels=F),
             yaxis=list(ticksuffix ="%",title="Covered % of errors in selected sample"),
             annotations=list(
               xref='x',
               yref='y',
               x=0.42,
               ax=20,
               ay=-40,
               y=PQC_value,
               text=HTML('<b>Train data</b>')
             ))
  }else if(type == 'average_score'){
    PQC_results_0=PQC_results[which(PQC_results$Label == 0),]%>%
      summarize(average_score=mean(Score))
    PQC_results_1=PQC_results[which(PQC_results$Label == 1),]%>%
      summarize(average_score=mean(Score))
    
    RQC_results_0=RQC_results[which(RQC_results$Label == 0),]%>%
      summarize(average_score=mean(Score))
    RQC_results_1=RQC_results[which(RQC_results$Label == 1),]%>%
      summarize(average_score=mean(Score))
    
    mean_0_score = mean(PQC_results_0$average_score,RQC_results_0$average_score)
    mean_1_score = mean(PQC_results_1$average_score,RQC_results_1$average_score)
    
    result=plot_ly()%>%
      add_trace(x=0,y=mean_1_score,type='bar',hoverinfo='text',text=mean_1_score)%>%
      add_trace(x=seq((-0.5),0.5,by = 0.05),y=mean_0_score,type='scatter',mode='lines', hoverinfo='text',text=mean_0_score)%>%
      #add_segments(x=-0.5,xend = 0.5,y=PQC_value, yend=PQC_value,line=list(color="#E88D14"),showlegend=F)%>%
      layout(showlegend=F,
             xaxis=list(title=HTML("<b>Rework cases</b>"),zeroline=F,showgrid=F,range=c(-0.5,0.5),showticklabels=F),
             yaxis=list(#ticksuffix ="%",
               title="Average score"),
             annotations=list(
               xref='x',
               yref='y',
               x=0.42,
               ax=20,
               ay=-40,
               y=mean_0_score,
               text=HTML('<b>No rework cases</b>')
             ))
    
    
  }else{
    PQC_results$Predicted=0
    PQC_results$Predicted[1:nrow(PQC_results)*threshold]=1
    
    RQC_results$Predicted=0
    RQC_results$Predicted[1:nrow(RQC_results)*threshold]=1
    
    PQC_results=PQC_results%>%
      summarize(acc=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$overall['Accuracy'],
                auc=fastAUC(probs = Score,class = Label),
                F1=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$byClass['F1'])
    
    
    RQC_results=RQC_results%>%
      summarize(acc=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$overall['Accuracy'],
                auc=fastAUC(probs = Score,class = Label),
                F1=confusionMatrix(factor(Predicted,levels = c(0,1)),factor(Label,levels = c(0,1)))$byClass['F1'])
    result=plot_ly()%>%
      add_trace(x=0,y=RQC_results[,type],type='bar',hoverinfo='text',text=RQC_results[,type])%>%
      add_trace(x=seq((-0.5),0.5,by = 0.05),y=PQC_results[,type],type='scatter',mode='lines', hoverinfo='text',text=PQC_results[,type])%>%
      #add_segments(x=-0.5,xend = 0.5,y=PQC_value, yend=PQC_value,line=list(color="#E88D14"),showlegend=F)%>%
      layout(showlegend=F,
             xaxis=list(title=HTML("<b>Test data</b>"),zeroline=F,showgrid=F,range=c(-0.5,0.5),showticklabels=F),
             yaxis=list(#ticksuffix ="%",
               title=paste(type," in selected sample")),
             annotations=list(
               xref='x',
               yref='y',
               x=0.42,
               ax=20,
               ay=-40,
               y=PQC_results[,type],
               text=HTML('<b>Train data</b>')
             ))
    
  }
  return(result)
}
