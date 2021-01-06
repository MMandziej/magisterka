function(Variable_importance_all_methods){
  Selected_features=list()
  Selected_features_Lasso=as.data.frame(Variable_importance_all_methods[[1]][Variable_importance_all_methods[[1]]$Overall>10,2])
  Selected_features_Boruta=as.data.frame(Variable_importance_all_methods[[2]][Variable_importance_all_methods[[2]]$decision=="Confirmed",7])
  Selected_features_RF=as.data.frame(Variable_importance_all_methods[[3]][Variable_importance_all_methods[[3]][,1]>quantile(Variable_importance_all_methods[[3]][,1],probs = 0.1),2])
  Selected_features=list(Selected_features_Lasso,Selected_features_Boruta,Selected_features_RF)
  return(Selected_features)
}
