function(feature, dataset,Label=F){
  if(is.numeric(dataset[,feature])==F){
    plot_ly(y=dataset[,'Label'],x=dataset[,feature],color=dataset[,feature],type="box",height = 600)%>%
      layout(showlegend=F,yaxis=list(title='Label'),xaxis=list(title=feature))
  }else{
    plot_ly(dataset,y=dataset[,feature],type="box",name=feature,height = 600)%>%
      layout(showlegend=F,yaxis=list(title=feature))
  }
}
