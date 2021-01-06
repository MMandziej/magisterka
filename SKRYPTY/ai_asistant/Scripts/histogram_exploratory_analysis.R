function(feature,dataset,bins=50,Label=T){
  if(Label==T){
    if(is.numeric(dataset[,feature])){
      test=hist(dataset[,feature])
      test_0=hist(dataset[,feature][which(dataset$Label==0)],breaks = test$breaks)
      test_1=hist(dataset[,feature][which(dataset$Label==1)],breaks = test$breaks)
      
      plot_ly(x=test_0$breaks[-1],
              y=test_0$counts,
              type="bar",name = "Label = 0",textposition = 'auto',text=paste(100*round(test_0$counts/(test_0$counts+test_1$counts),2),"%",sep = "")
              ,marker=list(color='#dd4b39')
      )%>%
        add_trace(x=test_1$breaks[-1],
                  y=test_1$counts,
                  name = "Label = 1",text=paste(100*round(test_1$counts/(test_0$counts+test_1$counts),2),"%",sep = "")
                  ,marker=list(color='#FFB600')
        )%>%
        layout(#margin = list(b = 500),
          yaxis=list(title=HTML("<b>Number of observations</b>")
                     #,color='white'
          ),xaxis=list(title=feature,
                       tickangle = 45
                       #,color='white'
          ),title=HTML(paste("<b>Histogram of ", feature, "</b>",sep="")),
          barmode="stack"
          #,font=list(color='white')
        )
      #%>%
      # layout(plot_bgcolor='rgb(52,62,72)') %>% 
      # layout(paper_bgcolor='rgb(52,62,72)')
      
    }else{
      dataset[,feature]=as.character(dataset[,feature])
      dataset[is.na(dataset[,feature]),feature]='N/A'
      plot_ly(x=sort(unique(dataset[which(dataset$Label==0),feature])),
              y=table(dataset[which(dataset$Label==0),feature]),
              type="bar",name = "Label = 0",textposition = 'auto',
              text=paste(100*round(table(dataset[which(dataset$Label==0),feature])/table(dataset[which(dataset[,feature]%in%dataset[which(dataset$Label==0),feature]),feature]),2),"%",sep = "")
              ,marker=list(color='#dd4b39')
      )%>%
        add_trace(x=sort(unique(dataset[which(dataset$Label==1),feature])),
                  y=table(dataset[which(dataset$Label==1),feature]),
                  name = "Label = 1",
                  text=paste(100*round(table(dataset[which(dataset$Label==1),feature])/table(dataset[which(dataset[,feature]%in%dataset[which(dataset$Label==1),feature]),feature]),2),"%",sep = "")
                  ,marker=list(color='#FFB600')
        )%>%
        layout(#margin = list(b = 500),
          yaxis=list(
            title=HTML("<b>Number of observations</b>")
            #,color='white'
          )
          ,xaxis=list(
            title=HTML(paste("<b>", feature, "</b>", sep='')),
            tickangle = 45
            #,color='white'
          ),title=HTML(
            paste("<b>Histogram of ", feature, "</b>",sep=""))
          ,barmode="stack"
          #,font=list(color='white')
        )
      #%>%
      #  layout(plot_bgcolor='rgb(52,62,72)') %>% 
      #  layout(paper_bgcolor='rgb(52,62,72)')
      
      
    }
    #plot_ly(x=dataset[which(dataset$Label==0),feature],type="histogram",nbinsx=bins,name = "Label = 0")%>%
    #  add_trace(x=dataset[which(dataset$Label==1),feature],name = "Label = 1")%>%
    #  layout(#margin = list(b = 500),
    #    yaxis=list(title="Amount of cases"),xaxis=list(title=feature,tickangle = 45),title=paste("Histogram of ",feature,sep=""),barmode="stack")
    
  }else{
    plot_ly(x=dataset[,feature],type="histogram",nbinsx=bins)%>%
      layout(yaxis=list(
        title=HTML("<b>Number of observations</b>")
        #,color='white'
      ),
      xaxis=list(
        title=HTML(paste("<b>",feature, "</b>", sep='')),
        tickangle = 45
        #,color='white'
      ),
      title=HTML(paste("<b>Histogram of ", feature, "</b>", sep="")),
      barmode="stack")
    
  }
}
