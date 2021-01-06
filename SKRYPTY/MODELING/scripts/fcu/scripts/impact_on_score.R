impact_on_score = function(feature, dataset){
  if(is.numeric(dataset[,feature]) & feature!='Label') {
    if(feature == 'OwnershipLayers') {
      dataset[[feature]][is.na(dataset[[feature]])] <- 0
      #dataset <- dataset %>% filter(!is.na(x_feature))
      
    }
    
    dataset[,feature] = quantcut(dataset[,feature])
  }
  dataset = dataset %>%
    group_by_(feature) %>%
    summarize(avg_score = round(mean(pqc),4))
  return(as.data.frame(dataset))
}
