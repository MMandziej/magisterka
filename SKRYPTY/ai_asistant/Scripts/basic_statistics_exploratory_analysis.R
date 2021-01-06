function(feature, dataset, Label = T) {
  if (is.numeric(dataset[,feature]) == F) {
    if (Label == T) {
      dataset[is.na(dataset[,feature]), feature] = 'N/A'
      table = round(as.data.frame.matrix(addmargins(prop.table(table(dataset[,feature],dataset$Label)),
                                                    margin = 2)),4)
      table = datatable(table,
                        filter = "bottom",
                        escape = F,
                        options = list(
                        dom = "Blfrtip",
                        scrollX = T,
                        lengthMenu = list(c(10, 20, 50, -1), # declare values
                                          c(10, 20,50, "All")), # declare titles # end of lengthMenu customization
                        pageLength = 10)) %>%
        formatPercentage(digits = 2,columns = c(1, 2, 3))
      return(table)
    } else {
      dataset[is.na(dataset[,feature]), feature] = 'N/A'
      table = as.data.frame(prop.table(table(dataset[,feature])))
      colnames(table) = c(feature, "Frequency")
      table$Frequency = round(table$Frequency, 4)
      table = datatable(table,
                        filter = "bottom",
                        escape = F,
                        options = list(dom = "Blfrtip",
                                       scrollX = T,
                                       lengthMenu = list(c(10, 20, 50, -1), # declare values
                                                         c(10, 20, 50, "All")), # declare titles # end of lengthMenu customization
                                       pageLength = 10)) %>%
        formatPercentage(digits = 2, columns = c(2))
      return(table)
    }
  } else {
    overall = data.frame(matrix(nrow = 10, ncol = 2))
    colnames(overall) = c("Measure", "Value")
    overall[,1] = c("Min", "Max"," Mean", "Median", "1st Quartile", "3rd Quartile",
                    "Missing values", "St.Dev", "Skewness", "Kurtosis")
    overall[,2] = c(min(dataset[,feature], na.rm = T),
                    max(dataset[,feature], na.rm = T),
                    base::mean(dataset[,feature], na.rm = T),
                    median(dataset[,feature], na.rm = T),
                    quantile(dataset[,feature], probs = 0.25, na.rm = T),
                    quantile(dataset[,feature], probs = 0.75, na.rm = T),
                    sum(is.na(dataset[,feature])),
                    sd(dataset[,feature], na.rm = T),
                    skewness(dataset[,feature], na.rm = T),
                    kurtosis(dataset[,feature], na.rm = T))
    
    #statistics0=data.frame(matrix(nrow = 10,ncol = 2))
    #colnames(statistics0)=c("Measure","Value")
    #statistics0[,1]=c("Min","Max","Mean","Median","1st Quartile","3rd Quartile","Missing values","St.Dev","Skewness","Kurtosis")
    #statistics0[,2]=c(min(dataset[which(dataset$Label==0),feature]),max(dataset[which(dataset$Label==0),feature]),mean(dataset[which(dataset$Label==0),feature]),median(dataset[which(dataset$Label==0),feature]),quantile(dataset[which(dataset$Label==0),feature],probs = 0.25),quantile(dataset[which(dataset$Label==0),feature],probs = 0.75),sum(is.na(dataset[which(dataset$Label==0),feature])),sd(dataset[which(dataset$Label==0),feature]),skewness(dataset[which(dataset$Label==0),feature]),kurtosis(dataset[which(dataset$Label==0),feature]))
    
    #statistics1=data.frame(matrix(nrow = 10,ncol = 2))
    #colnames(statistics1)=c("Measure","Value")
    #statistics1[,1]=c("Min","Max","Mean","Median","1st Quartile","3rd Quartile","Missing values","St.Dev","Skewness","Kurtosis")
    #statistics1[,2]=c(min(dataset[which(dataset$Label==1),feature]),max(dataset[which(dataset$Label==1),feature]),mean(dataset[which(dataset$Label==1),feature]),median(dataset[which(dataset$Label==1),feature]),quantile(dataset[which(dataset$Label==1),feature],probs = 0.25),quantile(dataset[which(dataset$Label==1),feature],probs = 0.75),sum(is.na(dataset[which(dataset$Label==1),feature])),sd(dataset[which(dataset$Label==1),feature]),skewness(dataset[which(dataset$Label==1),feature]),kurtosis(dataset[which(dataset$Label==1),feature]))
    
    
    overall = datatable(overall,
                        filter = "bottom",
                        escape = F,
                        options = list(dom = "Blfrtip",
                                       scrollX = T,
                                       lengthMenu = list(c(10, 20 ,50, -1), # declare values
                                                         c(10, 20, 50, "All")), # declare titles # end of lengthMenu customization
                                       pageLength = 10))
    return(overall)
  }
}
