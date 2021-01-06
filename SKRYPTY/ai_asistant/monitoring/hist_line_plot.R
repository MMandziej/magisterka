hist_line_plot = function(developement_dataset,monitoring_dataset,threshold,type,time_frame='days',Label=T){
  if(time_frame=='developement_vs_monitoring'){
    
  }else{
    developement_dataset$datestamp=floor_date(developement_dataset$datestamp,unit = time_frame,week_start = 1)
    monitoring_dataset$datestamp=floor_date(monitoring_dataset$datestamp,unit = time_frame,week_start = 1)
  
    if(type=="model_performance"){
      #full_dataset = rbind(developement_dataset,monitoring_dataset)
      #full_dataset=full_dataset%>%
      #  group_by(datestamp,Label)%>%
      #  summarize(no_cases=n())
      #full_dataset=as.data.frame(full_dataset)
      if(Label){
        barchart_data_developement_dataset = developement_dataset%>%
          group_by(datestamp,Label)%>%
          summarize(no_cases=n())
        
        barchart_data_monitoring_dataset = monitoring_dataset%>%
          group_by(datestamp,Label)%>%
          summarize(no_cases=n())
      }else{
        barchart_data_developement_dataset = developement_dataset%>%
          group_by(datestamp)%>%
          summarize(no_cases=n())
        
        barchart_data_monitoring_dataset = monitoring_dataset%>%
          group_by(datestamp)%>%
          summarize(no_cases=n())
      }

      
      production_developement_dataset = developement_dataset%>%
        group_by(datestamp)%>%
        summarize(no_cases=n())
      
      production_monitoring_dataset = monitoring_dataset%>%
        group_by(datestamp)%>%
        summarize(no_cases=n())
      
      
      max_error_developement_dataset=developement_dataset%>%
        group_by(datestamp)%>%
        summarize(max_error_developement_dataset=sum(Label))
      max_error_monitoring_dataset=monitoring_dataset%>%
        group_by(datestamp)%>%
        summarize(max_error_monitoring_dataset=sum(Label))
      
      max_error_developement_dataset=as.data.frame(max_error_developement_dataset)
      max_error_monitoring_dataset=as.data.frame(max_error_monitoring_dataset)
      
      
      developement_dataset = developement_dataset[order(
        developement_dataset$Score,
        decreasing = T),]
      developement_dataset=developement_dataset[1:round((nrow(developement_dataset)*threshold)),]
      threshold_score = min(developement_dataset$Score)
      
      monitoring_dataset = monitoring_dataset[order(
        monitoring_dataset$Score,
        decreasing = T),]
      
      monitoring_dataset=monitoring_dataset[1:(which(
        abs(monitoring_dataset$Score-threshold_score)==min(
          abs(monitoring_dataset$Score-threshold_score)
        )
      )[1]),]
      
      barchart_data_developement_dataset_selected = developement_dataset%>%
        group_by(datestamp)%>%
        summarize(no_cases_selected=n())
      
      barchart_data_monitoring_dataset_selected = monitoring_dataset%>%
        group_by(datestamp)%>%
        summarize(no_cases_selected=n())
      
      
      selected_line_developement_dataset = merge(x = production_developement_dataset,y = barchart_data_developement_dataset_selected,by = 'datestamp',all.x = T)
      selected_line_developement_dataset[is.na(selected_line_developement_dataset)]=0
      selected_line_developement_dataset$selected_prop=100*selected_line_developement_dataset$no_cases_selected/selected_line_developement_dataset$no_cases
      
      selected_line_monitoring_dataset = merge(x = production_monitoring_dataset,y = barchart_data_monitoring_dataset_selected,by = 'datestamp',all.x = T)
      selected_line_monitoring_dataset[is.na(selected_line_monitoring_dataset)]=0
      selected_line_monitoring_dataset$selected_prop=100*selected_line_monitoring_dataset$no_cases_selected/selected_line_monitoring_dataset$no_cases
      

      
      developement_dataset=developement_dataset%>%
        group_by(datestamp)%>%
        summarize(model_performance=sum(Label))
      monitoring_dataset=monitoring_dataset%>%
        group_by(datestamp)%>%
        summarize(model_performance=sum(Label))
      
      developement_dataset=as.data.frame(developement_dataset)
      monitoring_dataset=as.data.frame(monitoring_dataset)
      
      developement_dataset=merge(x = max_error_developement_dataset,y = developement_dataset,by = 'datestamp',all.x = T)
      developement_dataset[is.na(developement_dataset)]=0
      developement_dataset$model_performance=100*developement_dataset$model_performance/developement_dataset$max_error_developement_dataset
      
      monitoring_dataset=merge(x = max_error_monitoring_dataset,y = monitoring_dataset,by = 'datestamp',all.x = T)
      monitoring_dataset[is.na(monitoring_dataset)]=0
      monitoring_dataset$model_performance=100*monitoring_dataset$model_performance/max_error_monitoring_dataset$max_error_monitoring_dataset
      
      results=plot_ly()%>%
        add_trace(x=developement_dataset$datestamp,y=developement_dataset[,type],type = 'scatter',mode='lines',name='[%] of errors found - developement',line=list(color='#F4A60A'))%>%
        add_trace(x=monitoring_dataset$datestamp,y=monitoring_dataset[,type],type = 'scatter',mode='lines',name='[%] of errors found - monitoring',line=list(color='#F47B0A'))%>%
        add_trace(x=selected_line_developement_dataset$datestamp,y=selected_line_developement_dataset$selected_prop,type = 'scatter',mode='lines',name='[%] of cases selected - developement',line=list(color='#58FB06'))%>%
        add_trace(x=selected_line_monitoring_dataset$datestamp,y=selected_line_monitoring_dataset$selected_prop,type = 'scatter',mode='lines',name='[%] of cases selected - monitoring', line=list(color='#0AC621'))%>%
        add_trace(yaxis='y2',
                  x = barchart_data_developement_dataset$datestamp,
                  y=barchart_data_developement_dataset$no_cases, 
                  name = 'Number of scored cases - developement', 
                  type = 'bar',
                  marker = list(
                    color = barchart_data_developement_dataset$Label,
                    colorscale='Picnic')
        )%>%      hide_colorbar()%>%
        add_trace(yaxis='y2',
                  x = barchart_data_monitoring_dataset$datestamp,
                  y=barchart_data_monitoring_dataset$no_cases, 
                  name = 'Number of scored cases - monitoring', 
                  type = 'bar',
                  marker = list(
                    color = barchart_data_monitoring_dataset$Label,
                    colorscale='Portland')
        )%>% 
        hide_colorbar()%>%
        layout(legend = list(y = -0.05,orientation = "h",   # show entries horizontally
                             xanchor = "center",  # use center of legend as anchor
                             x = 0.5),
               margin = list(r = 50),
               barmode = 'stack',
               xaxis = list(range = c(min(developement_dataset$datestamp), max(monitoring_dataset$datestamp)+15*86400)),
               # title=paste("Changes of model performance within the time.",sep = ""),
               yaxis=list(side = 'left', overlaying = "y2",ticksuffix ="%",title=paste('[%] of errors found in ', 100 * threshold, '% of population'),showgrid = T, zeroline = FALSE),
               yaxis2 = list(side = 'right', title = 'Number of cases', showgrid = F, zeroline = FALSE))
      
    }else if(type=="part_of_population"){
      #full_dataset = rbind(developement_dataset,monitoring_dataset)
      #full_dataset=full_dataset%>%
      #  group_by(datestamp,Label)%>%
      #  summarize(no_cases=n())
      #full_dataset=as.data.frame(full_dataset)
      
      if(Label){
        barchart_data_developement_dataset = developement_dataset%>%
          group_by(datestamp,Label)%>%
          summarize(no_cases=n())
        
        barchart_data_monitoring_dataset = monitoring_dataset%>%
          group_by(datestamp,Label)%>%
          summarize(no_cases=n())
      }else{
        barchart_data_developement_dataset = developement_dataset%>%
          group_by(datestamp)%>%
          summarize(no_cases=n())
        
        barchart_data_monitoring_dataset = monitoring_dataset%>%
          group_by(datestamp)%>%
          summarize(no_cases=n())
      }
      
      
      max_error_developement_dataset=developement_dataset%>%
        group_by(datestamp)%>%
        summarize(max_error_developement_dataset=sum(Label))
      max_error_monitoring_dataset=monitoring_dataset%>%
        group_by(datestamp)%>%
        summarize(max_error_monitoring_dataset=sum(Label))
      
      max_error_developement_dataset=as.data.frame(max_error_developement_dataset)
      max_error_monitoring_dataset=as.data.frame(max_error_monitoring_dataset)
      
      
      developement_dataset=developement_dataset%>%
        group_by(datestamp)%>%
        filter(Score>=quantile(Score,probs = 1-threshold))%>%
        summarize(part_of_population=sum(Label))
      monitoring_dataset=monitoring_dataset%>%
        group_by(datestamp)%>%
        filter(Score>=quantile(Score,probs = 1-threshold))%>%
        summarize(part_of_population=sum(Label))
      
      developement_dataset=as.data.frame(developement_dataset)
      monitoring_dataset=as.data.frame(monitoring_dataset)
      
      developement_dataset=merge(x = max_error_developement_dataset,y = developement_dataset,by = 'datestamp',all.x = T)
      developement_dataset[is.na(developement_dataset)]=0
      developement_dataset$part_of_population=100*developement_dataset$part_of_population/developement_dataset$max_error_developement_dataset
      developement_dataset[is.na(developement_dataset)]=100
      
      monitoring_dataset=merge(x = max_error_monitoring_dataset,y = monitoring_dataset,by = 'datestamp',all.x = T)
      monitoring_dataset[is.na(monitoring_dataset)]=0
      monitoring_dataset$part_of_population=100*monitoring_dataset$part_of_population/max_error_monitoring_dataset$max_error_monitoring_dataset
      monitoring_dataset[is.na(monitoring_dataset)]=100
      
      results=plot_ly()%>%
        add_trace(x=developement_dataset$datestamp,y=developement_dataset[,type],type = 'scatter',mode='lines',name='% of errors found in developement dataset',line=list(color='#ffda3b'))%>%
        add_trace(x=monitoring_dataset$datestamp,y=monitoring_dataset[,type],type = 'scatter',mode='lines',name='% of errors found in monitoring dataset',line=list(color='#20C50D'))%>%
        #add_trace(yaxis='y2',x = full_dataset$datestamp,y=full_dataset$no_cases, color=full_dataset$Label,name = 'Number of scored cases', type = 'bar')%>% 
        #hide_colorbar()%>%
        add_trace(yaxis='y2',
                  x = barchart_data_developement_dataset$datestamp,
                  y=barchart_data_developement_dataset$no_cases, 
                  #color=barchart_data_monitoring_dataset$Label,
                  name = 'Number of scored cases test', 
                  type = 'bar',
                  marker = list(
                    color = barchart_data_developement_dataset$Label,
                    colorscale='Picnic')
        )%>%      hide_colorbar()%>%
        add_trace(yaxis='y2',
                  x = barchart_data_monitoring_dataset$datestamp,
                  y=barchart_data_monitoring_dataset$no_cases, 
                  #color=barchart_data_monitoring_dataset$Label,
                  name = 'Number of scored cases test', 
                  type = 'bar',
                  marker = list(
                    color = barchart_data_monitoring_dataset$Label,
                    colorscale='Portland')
        )%>% 
        hide_colorbar()%>%
        layout(legend = list(y = -0.05,orientation = "h",   # show entries horizontally
                             xanchor = "center",  # use center of legend as anchor
                             x = 0.5),
               barmode = 'stack',
               margin = list(r = 50),
               xaxis = list(range = c(min(developement_dataset$datestamp), max(monitoring_dataset$datestamp)+15*86400)),
               # title=paste("Changes of model performance within the time.",sep = ""),
               yaxis=list(side = 'left', overlaying = "y2",ticksuffix ="%",title=paste('Percent of errors found in ',100*threshold,'% of population'),showgrid = T, zeroline = FALSE),
               yaxis2 = list(side = 'right', title = 'No cases', showgrid = F, zeroline = FALSE))
      
    }else if(type == 'average_score'){
      developement_dataset_0=developement_dataset[which(developement_dataset$Label == 0),]%>%
        group_by(datestamp)%>%
        summarize(average_score=mean(Score))
      developement_dataset_1=developement_dataset[which(developement_dataset$Label == 1),]%>%
        group_by(datestamp)%>%
        summarize(average_score=mean(Score))
      
      monitoring_dataset_0=monitoring_dataset[which(monitoring_dataset$Label == 0),]%>%
        group_by(datestamp)%>%
        summarize(average_score=mean(Score))
      monitoring_dataset_1=monitoring_dataset[which(monitoring_dataset$Label == 1),]%>%
        group_by(datestamp)%>%
        summarize(average_score=mean(Score))
      
      if(Label){
        barchart_data_developement_dataset = developement_dataset%>%
          group_by(datestamp,Label)%>%
          summarize(no_cases=n())
        
        barchart_data_monitoring_dataset = monitoring_dataset%>%
          group_by(datestamp,Label)%>%
          summarize(no_cases=n())
      }else{
        barchart_data_developement_dataset = developement_dataset%>%
          group_by(datestamp)%>%
          summarize(no_cases=n())
        
        barchart_data_monitoring_dataset = monitoring_dataset%>%
          group_by(datestamp)%>%
          summarize(no_cases=n())
      }
      
      
      developement_dataset_0=as.data.frame(developement_dataset_0)
      developement_dataset_1=as.data.frame(developement_dataset_1)
      monitoring_dataset_0=as.data.frame(monitoring_dataset_0)
      monitoring_dataset_1=as.data.frame(monitoring_dataset_1)
      
      results = plot_ly(x = developement_dataset_0$datestamp, y = developement_dataset_0$average_score, name = 'Score for cases with no rework - development', type = 'scatter', mode = 'lines',line=list(color='#DE2626')) %>%
        add_trace(x = developement_dataset_1$datestamp, y = developement_dataset_1$average_score, name = 'Score for cases with with rework - development', type = 'scatter', mode = 'lines',line=list(color='#266EDE'))%>%
        add_trace(x = monitoring_dataset_0$datestamp, y = monitoring_dataset_0$average_score, name = 'Score for cases with no rework rework - monitoring', type = 'scatter', mode = 'lines',line=list(color='#BB0000'))%>%
        add_trace(x = monitoring_dataset_1$datestamp, y = monitoring_dataset_1$average_score, name = 'Score for cases with rework - monitoring', type = 'scatter', mode = 'lines',line=list(color='#0A54C6'))%>%
        add_trace(yaxis='y2',
                  x = barchart_data_developement_dataset$datestamp,
                  y=barchart_data_developement_dataset$no_cases, 
                  name = 'Number of scored cases - developement', 
                  type = 'bar')%>%
        add_trace(yaxis='y2',
                  x = barchart_data_monitoring_dataset$datestamp,
                  y=barchart_data_monitoring_dataset$no_cases, 
                  name = 'Number of scored cases - monitoring', 
                  type = 'bar')%>%
        layout(legend = list(y = -0.05,orientation = "h",   # show entries horizontally
                             xanchor = "center",  # use center of legend as anchor
                             x = 0.5),
               margin = list(r = 50),
               xaxis = list(range = c(min(developement_dataset$datestamp), max(monitoring_dataset$datestamp)+15*86400)),
               # title=paste("Changes of model performance within the time.",sep = ""),
               yaxis=list(side = 'left', overlaying = "y2",ticksuffix ="%",title=paste('Average score'),showgrid = T, zeroline = FALSE),
               yaxis2 = list(side = 'right', title = 'No cases', showgrid = F, zeroline = FALSE))
      
    }  
  }
  
  
    
  
  return(results)
}

