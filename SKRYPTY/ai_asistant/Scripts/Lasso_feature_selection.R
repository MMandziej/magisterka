function(dataset,label_column = "Label"){
  colnames(dataset)[which(colnames(dataset)==label_column)]='Label'
  Lasso_models <- caret :: train(Label ~ .,
                                 data=data.frame(dataset[,-1]), method="glmnet",
                                 tuneGrid=expand.grid(alpha=1, lambda=0),
                                 trControl=trainControl(method = 'cv'))
  #Lasso_models <- caret :: train(Label ~ ., data=datasets[,-1], method="lasso")
  #Lasso_predictions<- caret::predict.train(object = Lasso_models)
  #Lasso_predictions=as.data.frame(Lasso_predictions)
  Lasso_variable_importance <- varImp(Lasso_models)
  Lasso_variable_importance=as.data.frame(as.matrix(Lasso_variable_importance$importance))
  Lasso_variable_importance[,2]=row.names(Lasso_variable_importance)
  Lasso_variable_importance=Lasso_variable_importance[order(Lasso_variable_importance$Overall),]
  Lasso_variable_importance[,3]=(1:nrow(Lasso_variable_importance))
  return(Lasso_variable_importance)
  #assign(x = paste("Lasso_predictions_",name,sep = ""),value = Lasso_predictions,envir = globalenv())
  
}
