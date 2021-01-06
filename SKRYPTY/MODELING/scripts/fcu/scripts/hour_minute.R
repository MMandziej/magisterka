hour_minute<- function(x,approx=30){
  hour=chron::hours(x)
  minute=chron::minutes(x)
  minute=round(minute/approx)*approx
  helper_table=as.data.frame(matrix(data = c(hour,minute),ncol=2))
  helper_table$final_hour=ifelse(helper_table$V2==60,helper_table$V1+1,helper_table$V1)
  helper_table$final_minute=ifelse(helper_table$V2==60,0,helper_table$V2)
  results_hour_minute=paste(helper_table$final_hour,helper_table$final_minute,sep=':')
  results_hour_minute=format(strptime(results_hour_minute,"%H:%M"),'%H:%M')
  return(results_hour_minute)
}