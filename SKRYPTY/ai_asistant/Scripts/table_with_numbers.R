function(whole_dataset,selected_population){
  table=data.frame(matrix(nrow = 3,ncol = 3))
  colnames(table)=c("No. of cases","No. of errors","Error ratio*")
  row.names(table)=c("Whole population","Population selected for QC check","Population not selected for QC check")
  table[1,]=c(nrow(whole_dataset),max(whole_dataset$Sum),percent(max(whole_dataset$Sum)/nrow(whole_dataset)))
  table[2,]=c(nrow(selected_population),max(selected_population$Sum),percent(max(selected_population$Sum)/nrow(selected_population)))
  table[3,]=c(as.numeric(table[1,1])-as.numeric(table[2,1]),as.numeric(table[1,2])-as.numeric(table[2,2]),percent((as.numeric(table[1,2])-as.numeric(table[2,2]))/(as.numeric(table[1,1])-as.numeric(table[2,1]))))
  table=datatable(table,rownames=T,options = list(dom = 't',pageLength=-1))
  #,caption = htmltools::tags$caption(
  # style = 'caption-side: top; text-align: center; font-size:22px;font-weight: bold; color:black;',
  #'Comparison of populations'
  
  return(table)
}
