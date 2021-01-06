function (Dataset,
          frozen_columns = c('WFT ID', 'Label'),
          normalization_method = 'standardize',
          normalization_range = c(0, 1),
          remove_na = F) {

  contains_label = ifelse("Label" %in% names(Dataset), T, F)
  contains_datestamp = ifelse("datestamp" %in% names(Dataset), T, F)
  ### first, let's remove NA values
  if (remove_na==T) {
    Dataset = Dataset[complete.cases(Dataset),]
  }
  ### change hour to numeric
  #if("Hour"%in%colnames(Dataset)){
  #  Dataset$Hour=as.numeric(lubridate::hm(Dataset$Hour))
  #}
  ### let's normalize features in range
  
  j = 1
  names_of_column_numeric = vector()
  for (i in 1:length(colnames(Dataset))) {
    if (is.numeric(Dataset[,i]) == T &!colnames(Dataset)[i] %in% frozen_columns){
      names_of_column_numeric[j] = colnames(Dataset)[i]
      j = j+1
    }
  }
  
  for (i in names_of_column_numeric) {
    Dataset[,i] = BBmisc::normalize(Dataset[,i],
                                    method = normalization_method)
  }
  
  ###Dummifying the data
  j = 1
  names_of_column = vector()
  for (i in 1:length(colnames(Dataset))){
    if (is.numeric(Dataset[,i]) == F & !colnames(Dataset) [i] %in% frozen_columns) {
      names_of_column[j] = colnames(Dataset)[i]
      j = j+1
    }
  }
  
  for (i in names_of_column) {
    if (is.factor(Dataset[,i]) == F) {
      Dataset[,i] = factor(Dataset[,i],
                           levels=c(unique(Dataset[,i])),
                           labels = c(unique(Dataset[,i]))) 
    }
    Dataset <- createDummyFeatures(Dataset,cols=i)
    #Dataset=Dataset[,-length(Dataset)]
  }
  
  
  #names(Dataset)=remove_specials(names(Dataset))
  if (contains_label == T) {
    Dataset = Dataset[, c(1:(which(names(Dataset)=="Label")-1), (which(names(Dataset)=="Label")+1):length(names(Dataset)),which(names(Dataset)=="Label"))]
    names(Dataset)[length(Dataset)]="Label"                
  }
  
  if(contains_datestamp == T){
    Dataset=Dataset[,c(1:(which(names(Dataset)=="datestamp")-1),(which(names(Dataset)=="datestamp")+1):length(names(Dataset)),which(names(Dataset)=="datestamp"))]
    names(Dataset)[length(Dataset)]="datestamp"                
  }
  
  colnames(Dataset) = gsub(pattern = "\\.", replacement = "_", x = colnames(Dataset))
  colnames(Dataset) = gsub(pattern = ' ', replacement = "_", x = colnames(Dataset))
  Dataset$Label = factor(Dataset$Label)
  return(Dataset)
}
