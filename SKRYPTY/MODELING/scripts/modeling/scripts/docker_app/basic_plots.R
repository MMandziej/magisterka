function(type, ...){
  if (type == 'histogram') {
    histogram_exploratory_analysis(...)
  } else {
    boxplot_exploratory_analysis(...)
  }
}