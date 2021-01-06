function(feature_one,feature_two,dataset){
  if(is.numeric(dataset[,feature_one])==F&is.numeric(dataset[,feature_two])==F){
    if(expected_freq_exploratory_analysis(feature_one,feature_two,dataset)==FALSE){
      return(print("Assumptions of Chi squared test are not fulfilled"))
    } else {
      test=chisq.test(dataset[,feature_one],dataset[,feature_two])
      if(test$p.value>0.05){
        return(paste("Based on Chi-Square test,there are no arguments to say that features are not independent. P-value = ",test$p.value,"level",sep = " "))
      }else{
        return(paste("Based on Chi-Square test, features are not independent. P-value = ",test$p.value,sep=""))
      }
    }
  }else if (is.numeric(dataset[,feature_one])&is.numeric(dataset[,feature_two])){
    test=cor.test(dataset[,feature_one],dataset[,feature_two],method = "pearson")
    if(test$p.value<0.05){
      return(paste("Based on Pearson's test,significant correlation at",test$estimate,"coefficient.",sep = " "))
    }else{
      return(paste("Based on Pearson's test,correlations are not significant. P-value = ",test$p.value,sep=""))
    }
    #return(cor.test(dataset[,feature_one],dataset[,feature_two],method = "pearson"))
  } else if (is.numeric(dataset[,feature_one])){
    test=kruskal.test(dataset[,feature_one]~dataset[,feature_two],data=dataset)
    if(test$p.value<0.05){
      return(paste("Based on Kruskal-Wallis test, there's significant correlation between features. P-value = ",test$p.value,sep = ""))
    }else{
      return(paste("Based on Kruskal-Wallis test, there's no significant correlation between features. P-value = ",test$p.value,sep = ""))
    }
  } else {
    test=kruskal.test(dataset[,feature_two]~dataset[,feature_one],data=dataset)
    if(test$p.value<0.05){
      return(paste("Based on Kruskal-Wallis test, there's significant correlation between features. P-value = ",test$p.value,sep = ""))
    }else{
      return(paste("Based on Kruskal-Wallis test, there's no significant correlation between features. P-value = ",test$p.value,sep = ""))
    }
  }
}
