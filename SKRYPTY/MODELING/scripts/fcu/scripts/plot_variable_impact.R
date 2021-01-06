plot_variable_impact = function(dataset, x_feature, y_feature = "pqc", loess_span = 0.90){
  if(is.numeric(dataset[,x_feature])){
    dataset <- dataset %>% filter(!is.na(x_feature))
    ll.smooth = loess(data = dataset, as.formula(paste(y_feature,
                                                       " ~ ",
                                                       x_feature)), span=loess_span)
    ll.pred = predict(ll.smooth, se = TRUE) # error
    ll.df = data.frame(x=ll.smooth$x, fit=ll.pred$fit,
                       lb = ll.pred$fit - (1.96 * ll.pred$se),
                       ub = ll.pred$fit + (1.96 * ll.pred$se))
    ll.df = ll.df[order(ll.df[,x_feature]),]
    # Imput 0 to NA's for numeric features
    dataset[[x_feature]][is.na(dataset[[x_feature]])] <- 0
    # dataset <- dataset %>% 
    #   mutate(FirstGroupCase = ifelse(FirstGroupCase == 1, 'FistGroupCase', 'ComingGroupCase'),
    #          PopulationMatch = ifelse(PopulationMatch == 1, 'Match', 'NoMatch'),
    #          FATCA = ifelse(FATCA == 1, 'FATCA included', 'No FATCA'),
    #          CRS = ifelse(CRS == 1, 'CRS included', 'No CRS'),)
    # 
      plot_ly(data = dataset,
            x = dataset[,x_feature],
            y = dataset[,y_feature],
            type = 'scatter',
            mode = 'markers',
            name = 'Results',
            marker = list(
              opacity = 0.4
            )) %>%
      add_lines(y = ~fitted(loess(as.formula(paste(y_feature,
                                                   " ~ ",
                                                   x_feature)))),
                line = list(color = '#d90e00'),
                name = "Loess Smoother", showlegend = TRUE)%>%
      add_ribbons(inherit = F,
                  x = ll.df[,x_feature],
                  ymin = ll.df$lb,
                  ymax = ll.df$ub,
                  name = "95% CI",
                  color = "#ff584d",
                  line = list(opacity=0.4, width=0, color="#ff584d")) %>%
      layout(xaxis = list(title = x_feature),
             yaxis = list(title = y_feature),
             title = paste0("Impact of the ",x_feature," on ",y_feature))
  } else {
    plot_ly(data = dataset,
            x = dataset[,x_feature],
            y = dataset[,y_feature],
            type = 'box',
            name = 'Results') %>%
      layout(xaxis = list(title = x_feature),
             yaxis = list(title = y_feature),
             title = paste0("Impact of the ", x_feature, " on ", y_feature))
  }
  
}
