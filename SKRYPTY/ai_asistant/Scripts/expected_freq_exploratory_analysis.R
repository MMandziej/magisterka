function(feature_one,feature_two,dataset){
  freq=as.data.frame.matrix(addmargins(table(dataset[,feature_one],dataset[,feature_two]),margin = c(1,2)))
  expected=freq[-nrow(freq),length(freq)]%*%(as.matrix(freq[nrow(freq),-length(freq)]))
  expected=expected/freq[nrow(freq),length(freq)]
  if(sum(expected<1)>1 | sum(expected<5)<0.2*length(expected)) {return(FALSE)} else {return(TRUE)}
}
