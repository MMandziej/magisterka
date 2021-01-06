function(RQC_results){
  table=RQC_results[,c('GRID_ID',"Score","Label")]
  datatable(table,
            filter = "bottom",
            escape = F, options = list(
              dom = "Blfrtip",
              scrollX=T,
              lengthMenu = list( c(10, 20,50, -1) # declare values
                                 , c(10, 20,50, "All") # declare titles
              ) # end of lengthMenu customization
              , pageLength = 10
            ))
}
