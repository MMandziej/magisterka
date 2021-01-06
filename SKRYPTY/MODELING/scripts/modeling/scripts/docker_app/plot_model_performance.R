function(results_list, red_cut_off=0.3, amber_cut_off=0.7){
  model_perf = plot_ly(
    x=results_list[[1]]$X_coordinates,
    y=results_list[[1]]$y_coordinates,
    type='scatter',
    mode='line',
    name="Test dataset",
    line=list(color='#197519')) %>% #'#dd4b39'
    
    add_trace(
      x=results_list[[2]]$X_coordinates,
      y=results_list[[2]]$y_coordinates,
      name="Train dataset",
      line=list(color='#2a88ad')) %>% # 'rgb(255, 153, 0)'
    
    add_segments(x=red_cut_off,
                 xend=red_cut_off,
                 y=0, yend=1,
                 name="Red bucket",
                 line=list(color='#a83e32', width=3)) %>%
    add_segments(x=amber_cut_off,
                 xend=amber_cut_off,
                 y=0, yend=1,
                 name="Amber bucket",
                 line=list(color='#e8b43a', width=3)) %>%
    
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