library(readxl)
library(RPostgreSQL)
library(lubridate)


drv <- dbDriver("PostgreSQL")

## Connecting to db
con <-
  dbConnect(
    drv,
    dbname = "lionqc",
    host = "40.121.134.61",
    port = 5432,
    user = "postgres",
    password = 'Mjord@n23'
  )

#set the directory to directory where you have data
setwd("C:/Users/oaydin006/Downloads/")

# install last cut off file
last_cut_off <- read_excel("13032020 cut off.xlsx")

# Select completed cases
completed_cases <- last_cut_off[which(!is.na(last_cut_off$DRCompletedDate)),]

# select cases which have been completed later than 27-01-202
completed_cases_id <- completed_cases[which(as.Date(completed_cases$DRCompletedDate)>as.Date("2020-01-27")),] 

final_wf_df <- dbGetQuery(con, "select  * from final_data_dr")


# select completed cases from final df
wf_to_score<- final_wf_df[final_wf_df$GRID %in% completed_cases_id$GRID,]

# Number of completed cases
length(unique(wf_to_score$GRID))

# Select cases when they were sent to QC
wf_to_score<- wf_to_score[wf_to_score$CDDStatus=="DR - Pending Signatory",]

# Number of cases to be scored
length(unique(wf_to_score$GRID))

# select the version of cases when they were sent to QC first time 
unique_id_score<-aggregate(BackupTime~GRID,data = wf_to_score, min)

# Have the final cases to be scored
wf_to_score_final <- merge(wf_to_score,unique_id_score,by=c("GRID","BackupTime"))

# Save cases to be scored in db
## Loading PostgreSQL driver
drv <- dbDriver("PostgreSQL")

## Connecting to db
con <-
  dbConnect(
    drv,
    dbname = "lionqc",
    host = "40.121.134.61",
    port = 5432,
    user = "postgres",
    password = 'Mjord@n23'
  )

dbWriteTable(con, "wf_to_score", wf_to_score_final,row.names = FALSE, append = TRUE)

# Getting scored data
scored_df<- read.csv("scored_15032020.csv",header = T, sep = ",")

scored_id <- data.frame(scored_df$GRID,scored_df$pqc)

# Get score for completed cases
comp_cases_scored<- merge(completed_cases_id,scored_id,by.x ="GRID",by.y = "scored_df.GRID")

# Create labels
comp_cases_scored$label <- ifelse(comp_cases_scored$DRReworkCount > 0, 1, 0)
comp_cases_scored$label[is.na(comp_cases_scored$label)]<- 0

avg_scores <- aggregate(scored_df.pqc ~ as.Date(DRCompletedDate)+label, data = comp_cases_scored, FUN = mean)
count_cases_completed <- aggregate(GRID ~ as.Date(DRCompletedDate), data = comp_cases_scored, FUN = length)

score_0 <- avg_scores[avg_scores$label==0,]
score_1 <- avg_scores[avg_scores$label==1,]
avg_scores_final <- data.frame(score_0$`as.Date(DRCompletedDate)`,score_0$scored_df.pqc, score_1$scored_df.pqc)
colnames(avg_scores_final) <- c("date", "score_wo_rework","score_w_rework")

count_avg_score <- merge(avg_scores_final,count_cases_completed,by.x="date" , by.y="as.Date(DRCompletedDate)" )

colnames(count_avg_score) <- c("date", "score_wo_rework","score_w_rework", "count_comp")

# weekly stats
count_avg_score$week<-floor_date(count_avg_score$date,'week')
avg_scores_wo_rework_week <- aggregate(score_wo_rework ~ week, data = count_avg_score, FUN = mean)
avg_scores_w_rework_week <- aggregate(score_w_rework ~ week, data = count_avg_score, FUN = mean)
count_cases_completed_week <- aggregate(count_comp ~ week, data = count_avg_score, FUN = sum)
merged_scores_week<- merge(avg_scores_wo_rework_week,avg_scores_w_rework_week,by='week')
avg_scores_count_week <- merge(merged_scores_week,count_cases_completed_week, by='week' )

# selectcases sent to qc from final df
wf_not_completed<- final_wf_df[which(is.na(final_wf_df$DRCompletedDate)),]

# select cases which have been sent to QC later than 27-01-2020
not_completed_cases_id <- wf_not_completed[which(wf_not_completed$CDDStatus=="DR - Pending Signatory"),] 

# select the version of cases when they were sent to QC first time 
unique_id_not_comp<-aggregate(BackupTime~GRID,data = not_completed_cases_id, min)

# Have the final cases to be scored
wf_not_completed_final <- merge(not_completed_cases_id,unique_id_not_comp,by=c("GRID","BackupTime"))

length(unique(wf_not_completed_final$GRID))

count_cases_not_comp <- aggregate(GRID ~ as.Date(BackupTime), data = wf_not_completed_final, FUN = length)

stats<- merge(count_cases_not_comp,count_cases_completed,by.x="as.Date(BackupTime)" ,by.y="as.Date(DRCompletedDate)")

colnames(stats) <- c("date","count_sent_qc","count_completed")
