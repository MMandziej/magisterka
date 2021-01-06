function(feature_name,Variable_importance_all_methods){
  models=as.data.frame(matrix(nrow = 1,ncol=3))
  colnames(models)=c("Lasso","Boruta","RF")
  
  models[1,1]=if(sum(Variable_importance_all_methods[[1]]$V2==feature_name)==0) {"N/A"} else {
    base :: ifelse(Variable_importance_all_methods[[1]][Variable_importance_all_methods[[1]]$V2==feature_name,1]>10,"Confirmed","Rejected")
  }
  models[1,2]=if(sum(Variable_importance_all_methods[[2]]$V7==feature_name)==0) {"N/A"} else {
    base :: ifelse(Variable_importance_all_methods[[2]][Variable_importance_all_methods[[2]]$V7==feature_name,6]=="Confirmed","Confirmed","Rejected")
  }
  models[1,3]=if(sum(Variable_importance_all_methods[[3]][,2]==feature_name)==0) {"N/A"} else {
    base :: ifelse(Variable_importance_all_methods[[3]][Variable_importance_all_methods[[3]][,2]==feature_name,2]>quantile(Variable_importance_all_methods[[3]][,1],probs = 0.1),"Confirmed","Rejected")
  }
  return(models)
}
