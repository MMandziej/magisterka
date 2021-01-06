function(dataset, time_feature = 'datestamp', feature, Label = 'all'){
  if(is.numeric(dataset[,feature])){
    if(Label == 'all'){
      dataset[,time_feature] = substr(dataset[,time_feature], 1, 7)
      helper = as.data.frame(matrix(nrow = length(unique(dataset[,time_feature])), ncol = 7))
      helper$V1 = unique(dataset[,time_feature])
      for (i in 1:nrow(helper)) {
        helper[i,2:6] = quantile(dataset[which(dataset[,time_feature] == helper[i,1]), feature])
        helper[i,7] = IQR(dataset[which(dataset[,time_feature] == helper[i,1]), feature], na.rm = T)
      }
      colnames(helper) = c("Date", "Q 0%", "Q 25%", "Q 50%", "Q 75%", "Q 100%", "IQR") # wyrzuciæ jako sta³¹ przed funkcjê 
      helper = helper[order(helper$Date, decreasing = F),]
    } else {
      dataset = dataset[which(dataset[,'Label'] == Label),]
      dataset[,time_feature] = substr(dataset[,time_feature], 1, 7)
      helper = as.data.frame(matrix(nrow = length(unique(dataset[,time_feature])), ncol = 7))
      helper$V1 = unique(dataset[,time_feature])
      for (i in 1:nrow(helper)){
        helper[i,2:6] = quantile(dataset[which(dataset[,time_feature] == helper[i,1]), feature])
        helper[i,7] = IQR(dataset[which(dataset[,time_feature] == helper[i,1]), feature], na.rm = T)
      }
      colnames(helper) = c("Date", "Q 0%", "Q 25%", "Q 50%", "Q 75%", "Q 100%", "IQR") # wyrzuciæ jako sta³¹ przed funkcjê 
      helper = helper[order(helper$Date, decreasing = F),]
    }
    helper = datatable(helper,
                       filter = "bottom",
                       caption = paste('Values of quantiles and IQR for ', feature, sep=''),
                       escape = F,
                       options = list(dom = "t", scrollX=T,
                                      lengthMenu = list(c(10, 20,50, -1),  # declare values
                                                        c(10, 20,50, "All")), # declare titles # end of lengthMenu customization
                                      pageLength = 10))
  } else {
    if (Label == 'all') {
      dataset[,time_feature] = substr(dataset[,time_feature], 1, 7)
      helper = table(dataset[,time_feature], dataset[,feature])
      helper = round(prop.table(helper, margin = 1), 4)
      helper = as.data.frame(helper)
      helper = reshape(helper, timevar = 'Var2', idvar = 'Var1', direction = 'wide')
      colnames(helper) = c("Date", unique(dataset[,feature]))
    } else {
      dataset = dataset[which(dataset[,'Label'] == Label),]
      dataset[,time_feature] = substr(dataset[,time_feature], 1, 7)
      helper = table(dataset[,time_feature], dataset[,feature])
      helper = round(prop.table(helper, margin = 1), 4)
      helper = as.data.frame(helper)
      helper = reshape(helper, timevar = 'Var2', idvar = 'Var1', direction='wide')
      colnames(helper) = c("Date", unique(dataset[,feature]))
    } 
    helper = datatable(helper,
                     caption = paste('Frequencies for each value in ', feature, sep=''),
                     filter = "bottom",
                     escape = F,
                     options = list(dom = "t",
                                    scrollX = T,
                                    lengthMenu = list(c(10, 20, 50, -1), # declare values
                                                      c(10, 20, 50, "All")), # declare titles # end of lengthMenu customization
                                    pageLength = 10)) %>%
      formatPercentage(digits = 2,columns = c(2:length(helper)))
  }

  #? t(helper)
  return(helper)
}
