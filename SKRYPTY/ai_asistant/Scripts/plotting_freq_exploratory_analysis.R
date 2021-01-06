function(feature_one,feature_two,dataset){
  if(is.numeric(dataset[,feature_one])==F&is.numeric(dataset[,feature_two])==F){
    plot=as.data.frame(table(dataset[,feature_one],dataset[,feature_two]))%>%
      ggplot(aes(Var1,Var2,size=Freq))+
      xlab(feature_one)+
      ylab(feature_two)+
      geom_point(colour='#dd4b39')
    return(ggplotly(plot))
  } else if (is.numeric(dataset[,feature_one])&is.numeric(dataset[,feature_two])){
    plot=plot_ly(data = dataset,x=dataset[,feature_one],y=dataset[,feature_two],type = "scatter",mode='markers',marker=list(opacity=.2,color='#dd4b39'),width = 1100,height = 700)%>%
      layout(#margin = list(b = 50),
        legend=list(x=0.9,y=0.9),xaxis=list(title=feature_one,tickangle = 45),yaxis=list(title=feature_two),autosize=F)
    return(plot)
  } else if (is.numeric(dataset[,feature_one])){
    plot=plot_ly(x=dataset[,feature_one],color = dataset[,feature_two],type="histogram",alpha=0.6,width = 1100,height = 700)%>%layout(barmode="overlay",autosize=F)%>%
      layout(#margin = list(b = 50),
        legend=list(x=0.9,y=0.9),xaxis=list(title=feature_one,tickangle = 45),yaxis=list(title="Amount of cases"))
    return(plot)
  } else {
    plot=plot_ly(x=dataset[,feature_two],color = dataset[,feature_one],type="histogram",alpha=0.6,width = 1100,height = 700)%>%layout(barmode="overlay",autosize=F)%>%
      layout(#margin = list(b = 50),
        legend=list(x=0.9,y=0.9),xaxis=list(title=feature_two,tickangle = 45),yaxis=list(title="Amount of cases")) 
    return(plot)
  }
}
