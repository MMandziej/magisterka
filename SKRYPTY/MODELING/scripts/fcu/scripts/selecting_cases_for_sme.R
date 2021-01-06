# selecting cases for SME review
comp_cases_scored$week<-floor_date(as.Date(comp_cases_scored$DRCompletedDate),'week')+5

comp_cases_scored_selected_week <- comp_cases_scored[comp_cases_scored$week=='2020-02-21',]  

comp_cases_scored_selected_week<- comp_cases_scored_selected_week[comp_cases_scored_selected_week$label==1,]

dim(comp_cases_scored_selected_week)

comp_cases_scored_wo_r_check <- comp_cases_scored_selected_week[comp_cases_scored_selected_week$scored_df.pqc<0.5,]
comp_cases_scored_wo_r_check <- comp_cases_scored_wo_r[comp_cases_scored_wo_r$scored_df.pqc<0.4,]

dim(comp_cases_scored_wo_r_check)

for_sme <- data.frame(comp_cases_scored_wo_r_check$GRID,comp_cases_scored_wo_r_check$DRSentToQCDate,comp_cases_scored_wo_r_check$DRCompletedDate,comp_cases_scored_wo_r_check$scored_df.pqc,comp_cases_scored_wo_r_check$label)
write.csv(for_sme,"for_sme_review.csv")
