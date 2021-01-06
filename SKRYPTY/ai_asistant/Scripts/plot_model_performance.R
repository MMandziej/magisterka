function(results_list){
  model_perf = plot_ly(
    x=results_list[[1]]$X_coordinates,
    y=results_list[[1]]$y_coordinates,
    type='scatter',
    mode='line',
    name="Test dataset",
    line=list(color='#dd4b39')) %>%
    
    add_trace(
      x=results_list[[2]]$X_coordinates,
      y=results_list[[2]]$y_coordinates,
      name="Train dataset",
      line=list(color='rgb(255, 153, 0)')) %>%
    
    layout(title='<b>Model performance</b>',
           titlefont=list(size=22,
                          color='black',
                          face='bold'),
           margin=list(t=50),
           xaxis=list(tickformat="%",
                      title="% of cases"),
           yaxis=list(tickformat="%",
                      title="% of errors found"))
  return(model_perf)
}
