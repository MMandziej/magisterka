histogram_exploratory_analysis<- function(feature, dataset, bins=50, Label=T){
  if (Label == T) {
    if (is.numeric(dataset[,feature])) {
      
      test = hist(dataset[,feature])
      test_0 = hist(dataset[,feature][which(dataset$Label==0)], breaks=test$breaks)
      test_1 = hist(dataset[,feature][which(dataset$Label==1)], breaks=test$breaks)
      plot_ly(x = as.factor(test_0$breaks[-1]),
              y = test_0$counts,
              type = "bar", name = "No rework (0)", textposition = 'auto', 
              text = paste(100 * round(test_0$counts / (test_0$counts+test_1$counts), 2), "%", sep = "")
              ,marker = list(color='#dd4b39')
      ) %>%
        add_trace(x = as.factor(test_1$breaks[-1]),
                  y = test_1$counts,
                  name = "Rework (1)", text = paste(100 * round(test_1$counts / (test_0$counts + test_1$counts), 2), "%", sep = ""),
                  marker = list(color='#FFB600')
        ) %>%
        layout(#margin = list(b = 500),
          yaxis = list(title = "Number of cases"), #color='white',
          xaxis = list(title = feature, tickangle = 45), #,color='white'
          title = paste("Histogram of ", feature, sep = ""),
          barmode = "stack") #font=list(color='white') #%>%
      # layout(plot_bgcolor='rgb(52,62,72)') %>% 
      # layout(paper_bgcolor='rgb(52,62,72)')
      
    } else {
      dataset[is.na(dataset[,feature]),feature] = 'N/A'
      
      label_0 <- as.character(dataset[which(dataset$Label==0),feature])
      label_1 <- as.character(dataset[which(dataset$Label==1),feature])
      
      plot_ly(x = sort(unique(label_0)),
              y = table(label_0),
              type = "bar", name = "No rework (0)", textposition = 'auto',
              text = paste(100 * round(table(label_0) / table(as.character(dataset[which(dataset[,feature] %in% label_0),feature])), 2), "%", sep = ""),
              marker = list(color='#dd4b39')) %>%
        
        add_trace(x = as.character(sort(unique(label_1))),
                  y = table(label_1),
                  name = "Rework (1)",
                  text = paste(100 * round(table(label_1) / table(as.character(dataset[which(dataset[,feature] %in% label_1),feature])), 2),"%",sep = ""),
                  marker = list(color='#FFB600')) %>%
        
        layout(yaxis = list(title=HTML("<b>Number of cases</b>")), #,color='white' #margin = list(b = 500),
               xaxis = list(title=HTML(paste("<b>",feature,sep='')),
                            tickangle = 45), #,color='white'
               title = HTML(paste("<b>Histogram of ", feature, sep = "")),
               barmode="stack") #,font=list(color='white')
      #%>%
      #  layout(plot_bgcolor='rgb(52,62,72)') %>% 
      #  layout(paper_bgcolor='rgb(52,62,72)')
      
      
    }
    #plot_ly(x=dataset[which(dataset$Label==0),feature],type="histogram",nbinsx=bins,name = "Label = 0")%>%
    #  add_trace(x=dataset[which(dataset$Label==1),feature],name = "Label = 1")%>%
    #  layout(#margin = list(b = 500),
    #    yaxis=list(title="Amount of cases"),xaxis=list(title=feature,tickangle = 45),title=paste("Histogram of ",feature,sep=""),barmode="stack")
    
  } else {
    plot_ly(x = as.factor(dataset[,feature]), type = "histogram", nbinsx = bins, height = 600, width = 1100) %>%
      layout(
        #margin = list(b = 500),
        autosize = F,
        yaxis = list(title = "Number of cases"),
        xaxis = list(title = feature,
                     tickangle = 45),
        title = paste("Histogram of ", feature, sep = ""),
        barmode = "stack",
        font = list(color = 'white'))
  }
}
