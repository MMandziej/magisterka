Sys.setenv(RETICULATE_PYTHON = 'C:/Users/mmandziej001/Anaconda3/envs/gputest')

#calling libraries
library(dplyr)
library(readxl)
library(reticulate)
library(RPostgreSQL)
library(textclean)

setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/monitoring/")

# Calling functions
source("scripts/hour_minute.R")
source("scripts/calculations.R")
setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/monitoring/")

## Loading PostgreSQL driver
# drv <- dbDriver("PostgreSQL")
# 
# ## Connecting to db
# con <-
#   dbConnect(
#     drv,
#     dbname = "lionqc",
#     host = "40.121.134.61",
#     port = 5432,
#     user = "postgres",
#     password = 'Mjord@n23'
#   )

set_utf8 <- function(x) {
  # Declare UTF-8 encoding on all character columns:
  chr <- sapply(x, is.character)
  x[, chr] <- lapply(x[, chr, drop = FALSE], `Encoding<-`, "UTF-8")
  # Same on column names:
  Encoding(names(x)) <- "UTF-8"
  x
}

### change it to dbGetQuery, file is in repo :)
encoding_map = set_utf8(as.data.frame(read_excel("data/encoding.xlsx")))

## Select workflow data
# wf_all<- set_utf8(dbGetQuery(con, "select  * from cutoff_all"))
#ht_all <- set_utf8(dbGetQuery(con, "select * from holiday_tracker_all"))
wf_all = read_excel(paste("data/wf/", format(Sys.time(), "%d%m%Y")," cut off.xlsx", sep = ''))
ht_all = read.csv("data/holiday_tracker/holiday_tracker_all.csv")
df <- file.info(list.files("/path/to/your/directory", full.names = T))
rownames(df)[which.max(df$mtime)]

## WF transformation
# filter dataset on only pending cases
wf_all <- wf_all %>% filter(CDDStatus == 'DR - Pending Signatory')
wf_all$DRSentToQCDate = as.POSIXct(wf_all$DRSentToQCDate, tz = 'UTC')
wf_all$DRSentToQCDate_match = as.POSIXct(substr(wf_all$DRSentToQCDate, 1, 10), tz = 'UTC')

## HT transformation
# Change polish characters to ordinary characters
# to replaced -> only latest file
for(i in 1:nrow(ht_all)){
  ht_all$Employee[i] = mgsub(ht_all$Employee[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
}

# Filtering data
ht_all <- ht_all[-which(is.na(ht_all$Team)),]
ht_all <- ht_all[-which(is.na(ht_all$Employee)),]
ht_all <- ht_all[-which(ht_all$Team %in% c("Mgmt", "Process", "MI", "SME", "PMO")), ]
ht_all$Date <- as.POSIXct(substr(ht_all$Date, 1, 10), tz = 'UTC')
# create experience table
group_project <- aggregate(ht_all$Date, by=list(Category=ht_all$Employee), FUN=min) # date of join to project
group_team <- aggregate(Date~Employee+Team+Role, ht_all, FUN=min) # date of join to team
colnames(group_project) <- c("Employee", "MinDateProject")
colnames(group_team) <- c("Employee", "Team", "Role", "MinDateTeam")
group_project$MinDateProject <- as.POSIXct(substr(group_project$MinDateProject, 1, 10), tz = 'UTC')
group_team$MinDateTeam <- as.POSIXct(substr(group_team$MinDateTeam, 1, 10), tz = 'UTC')

ht_experience <- inner_join(x = group_project, 
                            y = group_team, 
                            by = 'Employee')
# rearrange cols
ht_experience <- ht_experience[, c('Employee', 'Team', 'Role', 'MinDateProject', 'MinDateTeam')]

for(i in 1:nrow(ht_experience)){
  ht_experience$Employee[i] = mgsub(ht_experience$Employee[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
}

ht_experience_tl <- ht_experience %>% filter(Role == 'TL')
ht_experience_merged <- merge(ht_experience, ht_experience_tl, by = 'Team')

## Select unique backup time
uniq_backup <- sort(as.Date(unique(wf_all$BackupTime)))

## Preparing data to score daily
final_wf_df <- NULL
for(j in 1:length(uniq_backup)) {
  wf <- wf_all[which(as.Date(wf_all$BackupTime) == uniq_backup[j]),]
  # to be moved before loop
  ## Creating labels for reworks
  wf$Label = ifelse(wf$DRReworkCount > 0, 1, 0)
  
  # Assigning 0 to cases which have DRCompletedData and NA rework count
  wf$Label[which(!is.na(wf$DRCompletedDate)&is.na(wf$DRReworkCount))] <- 0
  
  ## Preparing daily prediction data
  for (i in 1:nrow(wf)) {
    wf$AnalystAssignedName[i] = mgsub(wf$AnalystAssignedName[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
    wf$FirstAnalystDR[i] = mgsub(wf$FirstAnalystDR[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
    
    # Last 5 days
    wf$NO_errors_last_5_days_DR[i] = nrow(wf[which(
      (wf$FirstAnalystDR == wf$AnalystAssignedName[i] |
         (wf$AnalystAssignedName == wf$AnalystAssignedName[i] &
            is.na(wf$FirstAnalystDR))) &
        as.numeric(wf$DRSentToQCDate) < as.numeric(wf$DRSentToQCDate[i]) &
        as.numeric(wf$DRSentToQCDate) > (as.numeric(wf$DRSentToQCDate[i]) - 5 * 86400) & wf$Label == 1), ])
    
    wf$NO_cases_last_5_days_DR[i] = nrow(wf[which(
      (wf$FirstAnalystDR == wf$AnalystAssignedName[i]|
         (wf$AnalystAssignedName == wf$AnalystAssignedName[i]&
            is.na(wf$FirstAnalystDR))) &
        as.numeric(wf$DRSentToQCDate) < as.numeric(wf$DRSentToQCDate[i]) &
        as.numeric(wf$DRSentToQCDate) > (as.numeric(wf$DRSentToQCDate[i]) -5 * 86400)), ])
    
    #last month
    wf$NO_errors_last_month_DR[i] = nrow(wf[which(
      (wf$FirstAnalystDR == wf$AnalystAssignedName[i]|
         (wf$AnalystAssignedName == wf$AnalystAssignedName[i]&
            is.na(wf$FirstAnalystDR))) &
        as.numeric(wf$DRSentToQCDate) < as.numeric(wf$DRSentToQCDate[i]) &
        as.numeric(wf$DRSentToQCDate) > (as.numeric(wf$DRSentToQCDate[i]) - 30 * 86400) & wf$Label == 1), ])
    
    wf$NO_cases_month_DR[i] = nrow(wf[which(
      (wf$FirstAnalystDR == wf$AnalystAssignedName[i]|
         (wf$AnalystAssignedName == wf$AnalystAssignedName[i]&
            is.na(wf$FirstAnalystDR))) &
        as.numeric(wf$DRSentToQCDate) < as.numeric(wf$DRSentToQCDate[i]) &
        as.numeric(wf$DRSentToQCDate) > (as.numeric(wf$DRSentToQCDate[i]) - 30 * 86400)), ])
  }
  
  # Calculating experiences
  #ht_experience$experience_project <-as.numeric(as.Date(Sys.time(), "YYYY-MM-DD") - ht$min_hate_date[1])
  #ht_experience$experience_team <- as.numeric(as.Date(Sys.time(), "YYYY-MM-DD") - ht$min_hate_date_team[1])
  
  # Merging holiday tracker with workflow data
  ## to match HT with workflow, we need propper date format to match observations (posixct) and
  ## experience (numeric - we can calculate difference between sendtoqcdate and experience table)
  
  # przed pêtlê 
  wf$DateJoiningProject <- NULL
  for (i in 1:nrow(wf)) {
    # we've put [1] becouse Verstraate, M. (Mitchell) was sometimes doubled becouse of TL and analyst role in HT
    # we will not use this feature, 4645 datapoints
    wf$HT_TL[i] = ht_all[which(ht_all$Employee == wf$AnalystAssignedName[i] & ht_all$Date == wf$DRSentToQCDate_match[i])[1], 3]
    wf$DateJoiningProject[i] = ht_experience[which(ht_experience$Employee == wf$AnalystAssignedName[i])[1], 4]
  }
  
  # przed pêtlê 
  wf$DateJoiningTeam = NA
  for (i in 1:nrow(wf)) {
    if (!is.na(wf$HT_TL[i])) {
      wf$DateJoiningTeam[i] = ht_experience_merged[which(ht_experience_merged$Employee.x == wf$AnalystAssignedName[i] &
                                                           ht_experience_merged$Employee.y == wf$TLAssignedName[i])[1], 5] # SECOND CONDITION CHANGED
                                                           # & ht_experience_merged$Team == wf$HT_TL[i]
    }
  }
  
  # za pêtlê 
  wf$Hour = NA
  wf$Hour = hour_minute(wf$DRSentToQCDate)
  
  #paste(hour(dataset$DRSentToQCDate),":",minute(dataset$DRSentToQCDate),sep="")
  wf$Day = NA
  wf$Day = weekdays(wf$DRSentToQCDate_match)
  
  #for numeric use the code below :
  wf$Hour_numeric = NA
  wf$Hour_numeric = as.numeric(as.POSIXct(wf$Hour, format = "%H:%M")) - as.numeric(as.POSIXct("00:00", format = "%H:%M"))
  
  ### Check if LUP/EUP are there
  wf$LegalUltimateParentGRID = ifelse(is.na(wf$LegalUltimateParentGRID), 0, 1)
  wf$LegalUltimateParentGRID[which(wf$PartyType == "Ultimate")] = 0
  
  ### ESR/CRS/FATCA/WPI
  wf$ESR = ifelse(is.na(wf$ESR), 'No ESR needed', wf$ESR)
  
  ### Party type
  wf$PartyType = ifelse(wf$LegalUltimateParentGRID == 1, "Subsidiary", "Ultimate")
  
  #wf=wf[,-which(colnames(wf)=="LegalUltimateParentGRID")]
  
  ### EconomicUPGRID - groups of cases
  wf$EconomicUltimateParentGRID[which(wf$EconomicUltimateParentGRID == 0)] = NA
  
  for (i in 1:nrow(wf)) {
    wf$Group_cases[i] = length(which(wf$EconomicUltimateParentGRID == wf$EconomicUltimateParentGRID[i]))
  }
  # za pêtlê 
  wf$Experience_team <- as.numeric(wf$DRSentToQCDate_match) - as.numeric(wf$DateJoiningTeam)
  wf$check_date <- as.Date(wf$DRSentToQCDate_match)
  wf$Experience_proj <- as.numeric(wf$DRSentToQCDate_match) - as.numeric(wf$DateJoiningProject)
  
  #ht_experience_tl$check_date <- as.Date(ht_experience_tl$mindateteam)
  
  #ht_exp_team <- aggregate(check_date ~ Team, data = ht_experience_tl, max)
  
  #ht_experience_tl_new<- merge(ht_experience_tl,ht_exp_team,by=c("Team","check_date"))
  
  #merged_wf <- merge(wf,ht_experience_tl_new, by.x = 'HT_TL', by.y = "Team", all.x = TRUE)
  wf$Population_match = NA
  for (t in 1:nrow(wf)){
    wf$Population_match[t]=ifelse(wf$HT_TL[t]%in% ht_all$Team[which(ht_all$Employee==wf$TLAssignedName[t]&
                                             ht_all$Date==wf$DRSentToQCDate_match[t])],1,0)
  }
  
  #merged_wf$Population_match = ifelse(merged_wf$TLAssignedName == merged_wf$Employee,'TRUE','FALSE')
  
  # preparing final dataset
  #final_wf <- data.frame(wf, merged_wf$Population_match)
  
  final_wf_df <- rbind(final_wf_df, wf)
  print(j)
  }

# final_wf_df <- final_wf_df %>% rename(NO_errors_last_5_days = NO_errors_last_5_days_DR,
#                                       NO_cases_last_5_days = NO_cases_last_5_days_DR,
#                                       NO_errors_last_month = NO_errors_last_month_DR,
#                                       NO_cases_month = NO_cases_month_DR,
#                                       TLAssigned = TLAssignedName)

output <- final_wf_df %>% mutate(DateJoiningProject = as.numeric(DateJoiningProject))
output$Day[output$Day == 'poniedzia³ek'] <- 'Monday'
output$Day[output$Day == 'wtorek'] <- 'Tuesday'
output$Day[output$Day == 'œroda'] <- 'Wednesday'
output$Day[output$Day == 'czwartek'] <- 'Thursday'
output$Day[output$Day == 'pi¹tek'] <- 'Friday'
write.csv(output, paste("data/scoring_input/scoring_input_", Sys.Date(), ".csv", sep=''), row.names=F)

py_run_file('scripts/lion_king_pqc_dr_prediction.py')
# dbWriteTable(con, "final_data_dr", final_wf_df,row.names = FALSE, append = TRUE)
