create_test_train = function(dataset){
  set.seed(100)
  former_dataset = dataset
  dataset$datestamp = floor_date(dataset$datestamp,unit = 'weeks')
  dataset$part_score = runif(nrow(dataset))
  dataset_train = dataset%>%
    group_by(datestamp,Label)%>%
    mutate(
      part_score = ifelse(part_score<=quantile(part_score,probs = 0.8,type = 1),0,1))%>%
    filter(part_score==0)
  dataset_test = dataset%>%
    group_by(datestamp,Label)%>%
    mutate(
      part_score = ifelse(part_score<=quantile(part_score,probs = 0.8,type = 1),0,1))%>%
    filter(part_score==1)
  dataset_train=as.data.frame(
    dataset_train[,-which(
      colnames(dataset_train)=='part_score'
    )]
  )
  dataset_test=as.data.frame(
    dataset_test[,-which(
      colnames(dataset_test)=='part_score'
    )]
  )
  dataset_train = former_dataset[which(former_dataset[,1]%in%dataset_train[,1]),]
  dataset_test = former_dataset[which(former_dataset[,1]%in%dataset_test[,1]),]
  return(list(dataset_test,dataset_train))
}
