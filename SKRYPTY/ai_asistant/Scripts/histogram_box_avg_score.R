function(RQC_results,PQC_results,type, last_x_days = NA){
  if(!is.na(last_x_days)){
    PQC_results=PQC_results[which(PQC_results$datestamp>=as.numeric(as.POSIXct(as.character(today())))-last_x_days*86400),]
  }
  if(nrow(PQC_results)==0){
    print("No cases within selected period of time")
  }else{
    test=as.data.frame(matrix(nrow=sum(nrow(RQC_results),nrow(PQC_results)),ncol=3))
    colnames(test)=c("Label","Score","Group")
    test$Label[1:nrow(RQC_results)]=RQC_results$Label
    test$Score[1:nrow(RQC_results)]=RQC_results$Score
    test$Group[1:nrow(RQC_results)]='RQC'
    
    test$Label[(1+nrow(RQC_results)):nrow(test)]=PQC_results$Label
    test$Score[(1+nrow(RQC_results)):nrow(test)]=PQC_results$Score
    test$Group[(1+nrow(RQC_results)):nrow(test)]='PQC'
    if(type=='histogram'){
      test=test%>%
        group_by(Label,Group)%>%
        summarize(Average_Score=mean(Score))
      
      result=test%>%
        plot_ly()%>%
        add_trace(x= ~Label,y= ~Average_Score,color=~Group,type='bar')
    }else if(type=='box'){
      #test$Group=paste(test$Group,test$Label,sep=' ')
      result=test%>%
        plot_ly()%>%
        add_trace(x= ~Label,y= ~Score,color=~Group,type='box')%>%
        layout(boxmode="group")
    }
    return(result)
    
  }
}
