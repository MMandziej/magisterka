function(method,Variable_importance_all_methods){
  #method - int representing lasso (1) boruta (2) and dalex(3)
  if(method=="Lasso"){
    lasso_features=as.data.frame(Variable_importance_all_methods[[1]][Variable_importance_all_methods[[1]]$Overall>10,2])
    names(lasso_features)="Features selected for the model"
    return(datatable(lasso_features,rownames=FALSE,options = list(dom = 't',pageLength=-1,scrollY="400px")))
  }else if(method=="Boruta"){
    boruta_features=as.data.frame(Variable_importance_all_methods[[2]][Variable_importance_all_methods[[2]]$decision=="Confirmed",7])
    names(boruta_features)="Features selected for the model"
    return(datatable(boruta_features,rownames=FALSE,options = list(dom = 't',pageLength=-1,scrollY="400px")))
  }else if(method=="RF"){
    Dalex_features=as.data.frame(Variable_importance_all_methods[[3]][Variable_importance_all_methods[[3]][,1]>quantile(Variable_importance_all_methods[[3]][,1],probs = 0.1),2])
    names(Dalex_features)="Features selected for the model"
    return(datatable(Dalex_features,rownames=FALSE,options = list(dom = 't',pageLength=-1,scrollY="400px")))                     
  }else if(method=="GBM"){
    Dalex_features=as.data.frame(Variable_importance_all_methods[[4]][Variable_importance_all_methods[[4]]$dropout_loss>quantile(Variable_importance_all_methods[[4]]$dropout_loss,probs = 0.1),1])
    names(Dalex_features)="Features selected for the model"
    return(datatable(Dalex_features,rownames=FALSE,options = list(dom = 't',pageLength=-1,scrollY="400px")))                     
  }else if(method=="NN"){
    Dalex_features=as.data.frame(Variable_importance_all_methods[[5]][Variable_importance_all_methods[[5]]$dropout_loss>quantile(Variable_importance_all_methods[[5]]$dropout_loss,probs = 0.1),1])
    names(Dalex_features)="Features selected for the model"
    return(datatable(Dalex_features,rownames=FALSE,options = list(dom = 't',pageLength=-1,scrollY="400px")))                     
  }
}
