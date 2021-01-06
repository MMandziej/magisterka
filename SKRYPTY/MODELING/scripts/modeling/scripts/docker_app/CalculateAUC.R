function(models_list){
  output = as.data.frame(matrix(nrow = length(models_list), ncol=2))
  colnames(output) = c("Dataset", "AUC")
  if (length(models_list) == 6) {
    output[,1]=c("Test all features", "Train all features", "Test selected features", "Train selected features",
                 "Test no population", "Train no population")
  } else if(length(models_list) == 2) {
    output[,1] = c("Test", "Train")
  } else {
    output[,1] = c("Gradient Boosted Machine", "Neural Network", "Regression Random Forest",
                   "Penalized Regression", "Classification Random Forest")
  }
  for (i in (1:length(models_list))) {
    output[i,2] = fastAUC(models_list[[i]]['Score'], models_list[[i]]['Label'])
  }
  output = datatable(output, rownames = FALSE, options = list(dom = 't', pageLength = -1),
                     caption = htmltools::tags$caption(
                     style = 'caption-side: top; text-align: center; font-size:16px;font-weight: bold; color:black;',
                     'Area under curve')) %>%
    formatRound(digits = 2, columns = 2)
  return(output)
}
