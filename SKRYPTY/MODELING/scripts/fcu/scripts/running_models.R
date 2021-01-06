Sys.setenv(RETICULATE_PYTHON = 'C:/Users/mmandziej001/Anaconda3/envs/gputest')

#calling libraries
library(dplyr)
library(readxl)
library(reticulate)
library(RPostgreSQL)
library(textclean)
library(xlsx)

setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/Production/DR/")

# Calling functions
source("scripts/hour_minute.R")
# source("scripts/calculations.R")
source("scripts/merge_ht_data.R")


## Select workflow data
wf_all <- read_excel(paste("data/wf/", format(Sys.time(), "%d%m%Y")," cut off.xlsx", sep = ''))
# ht_all <- read.csv("data/holiday_tracker/holiday_tracker_all.csv")
ht_all <- holiday_tracker_all

## WF transformation
# Change polish characters to ordinary characters
for (i in 1:nrow(wf_all)) {
  wf_all$AnalystAssignedName[i] = mgsub(wf_all$AnalystAssignedName[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
  wf_all$QCAssignedName[i] = mgsub(wf_all$QCAssignedName[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
  wf_all$TLAssignedName[i] = mgsub(wf_all$TLAssignedName[i], pattern = encoding_map$pattern, replacement = encoding_map$replacement)
}

# Transform necessary features
wf_all$GreenlightedDR = ifelse(wf_all$GreenlightedDR == 0, FALSE, TRUE)
wf_all$DRSentToQCDate = as.POSIXct(wf_all$DRSentToQCDate, tz = 'UTC')
wf_all$DRSentToQCDate_match = as.POSIXct(substr(wf_all$DRSentToQCDate, 1, 10), tz = 'UTC')


# Filtering data
# ht_all <- ht_all[-which(is.na(ht_all$Team)),]
# ht_all <- ht_all[-which(is.na(ht_all$Employee)),]
# ht_all <- ht_all[-which(ht_all$Team %in% c("Mgmt", "Process", "MI", "SME", "PMO")), ]
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

ht_experience_tl <- ht_experience %>% filter(Role == 'TL')
ht_experience_analyst <- ht_experience %>% filter(Role == 'Analyst')
ht_experience_merged <- merge(ht_experience, ht_experience_tl, by = 'Team')
# prepare TL - Analyst mapping
tl_analyst_mapping = merge(ht_experience_analyst, ht_experience_tl, by = 'Team')
tl_analyst_mapping <- tl_analyst_mapping %>% select_(~Team, ~Employee.x, ~MinDateProject.x, ~MinDateTeam.x,
                                    ~Employee.y, ~MinDateProject.y, ~MinDateTeam.y)
colnames(tl_analyst_mapping) <- c('Team', 'Analyst', 'AnalystMinDateProject', 'AnalystMinDateTeam',
                                  'TeamLeader', 'TLMinDateProject', 'TLMinDateTeam')

write.xlsx(tl_analyst_mapping,
           paste("data/tl_analyst_mapping_", Sys.Date(), ".xlsx", sep = ''),
           row.names = F,
           showNA = FALSE)

## Select unique backup time
uniq_backup <- sort(as.Date(unique(wf_all$BackupTime)))
## Creating labels for reworks
wf_all$Label = ifelse(wf_all$DRReworkCount > 0, 1, 0)
# Assigning 0 to cases which have DRCompletedData and NA rework count
wf_all$Label[which(!is.na(wf_all$DRCompletedDate) & is.na(wf_all$DRReworkCount))] <- 0
# create new cols to append
wf_all$DateJoiningProject <- NULL
wf_all$DateJoiningTeam = NA
wf_all$Population_match = NA

## Preparing data to score daily
final_wf_df <- NULL
for(j in 1:length(uniq_backup)) {
  wf <- wf_all[which(as.Date(wf_all$BackupTime) == uniq_backup[j]),]
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
      (wf$FirstAnalystDR == wf$AnalystAssignedName[i] |
         (wf$AnalystAssignedName == wf$AnalystAssignedName[i] &
            is.na(wf$FirstAnalystDR))) &
        as.numeric(wf$DRSentToQCDate) < as.numeric(wf$DRSentToQCDate[i]) &
        as.numeric(wf$DRSentToQCDate) > (as.numeric(wf$DRSentToQCDate[i]) - 5 * 86400)), ])
    
    #last month
    wf$NO_errors_last_month_DR[i] = nrow(wf[which(
      (wf$FirstAnalystDR == wf$AnalystAssignedName[i]|
         (wf$AnalystAssignedName == wf$AnalystAssignedName[i] &
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
  

  for (i in 1:nrow(wf)) {
    # we've put [1] becouse Verstraate, M. (Mitchell) was sometimes doubled becouse of TL and analyst role in HT
    # we will not use this feature, 4645 datapoints
    wf$HT_TL[i] = ht_all[which(ht_all$Employee == wf$AnalystAssignedName[i] & ht_all$Date == wf$DRSentToQCDate_match[i])[1], 2] #assign team number as HT_TL
    wf$DateJoiningProject[i] = ht_experience[which(ht_experience$Employee == wf$AnalystAssignedName[i])[1], 4]
  }
  
  for (i in 1:nrow(wf)) {
    if (!is.na(wf$HT_TL[i])) {
      wf$DateJoiningTeam[i] = ht_experience_merged[which(ht_experience_merged$Employee.x == wf$AnalystAssignedName[i] &
                                                           ht_experience_merged$Employee.y == wf$TLAssignedName[i])[1], 5] # SECOND CONDITION CHANGED
                                                           # & ht_experience_merged$Team == wf$HT_TL[i]
    }
  }
  
  for (i in 1:nrow(wf)) {
    wf$Group_cases[i] = length(which(wf$EconomicUltimateParentGRID == wf$EconomicUltimateParentGRID[i]))
  }

  
  for (t in 1:nrow(wf)){
    wf$Population_match[t] = ifelse(wf$HT_TL[t] %in% ht_all$Team[which(ht_all$Employee == wf$TLAssignedName[t] &
                                             ht_all$Date == wf$DRSentToQCDate_match[t])], 1, 0) # change from ht_all$Team to ht_all$Employee
  }
  
  # merged_wf$Population_match = ifelse(merged_wf$TLAssignedName == merged_wf$Employee,'TRUE','FALSE')
  # preparing final dataset
  final_wf_df <- rbind(final_wf_df, wf)
  print(j)
  }

# filter dataset on only pending cases and cases not in German population
german_TLs <- c('Makowska, M.M. (Malgorzata)', 'Bartczak, K. (Kamil)', 'Jaszewski, M. (Michal)',
                'Jastrzebowska, S. (Sonia)', 'Skrzynecki, P. (Piotr)')
final_wf_df <- final_wf_df %>% filter(CDDStatus == 'DR - Pending Signatory',
                                      !TLAssignedName %in% german_TLs,
                                      !PSStatus %in% c('4. Ready to check - excluded by Ops Mgmt'))

final_wf_df$Hour = NA
final_wf_df$Hour = hour_minute(final_wf_df$DRSentToQCDate)
final_wf_df$Hour_numeric = NA
final_wf_df$Hour_numeric = as.numeric(as.POSIXct(final_wf_df$Hour, format = "%H:%M")) - as.numeric(as.POSIXct("00:00", format = "%H:%M"))
final_wf_df$Day = NA
final_wf_df$Day = weekdays(final_wf_df$DRSentToQCDate_match)

### Check if LUP/EUP are there
final_wf_df$LegalUltimateParentGRID = ifelse(is.na(final_wf_df$LegalUltimateParentGRID), 0, 1)
final_wf_df$LegalUltimateParentGRID[which(final_wf_df$PartyType == "Ultimate")] = 0

### ESR/CRS/FATCA/WPI
final_wf_df$ESR = ifelse(is.na(final_wf_df$ESR), 'No ESR needed', final_wf_df$ESR)

### Party type
final_wf_df$PartyType = ifelse(final_wf_df$LegalUltimateParentGRID == 1, "Subsidiary", "Ultimate")

### EconomicUPGRID - groups of cases
final_wf_df$EconomicUltimateParentGRID[which(final_wf_df$EconomicUltimateParentGRID == 0)] = NA

final_wf_df$Experience_team <- as.numeric(final_wf_df$DRSentToQCDate_match) - as.numeric(final_wf_df$DateJoiningTeam)
final_wf_df$check_date <- as.Date(final_wf_df$DRSentToQCDate_match)
final_wf_df$Experience_proj <- as.numeric(final_wf_df$DRSentToQCDate_match) - as.numeric(final_wf_df$DateJoiningProject)

output <- final_wf_df %>% mutate(DateJoiningProject = as.numeric(DateJoiningProject),
                                 HT_TL = as.character(HT_TL))
output$Day[output$Day == 'poniedzia³ek'] <- 'Monday'
output$Day[output$Day == 'wtorek'] <- 'Tuesday'
output$Day[output$Day == 'œroda'] <- 'Wednesday'
output$Day[output$Day == 'czwartek'] <- 'Thursday'
output$Day[output$Day == 'pi¹tek'] <- 'Friday'
write.csv(as.data.frame(output),
          paste("data/scoring_input/scoring_input_", Sys.Date(), ".csv", sep=''),
          row.names=F)
write.xlsx(as.data.frame(output),
           paste("data/scoring_input/scoring_input_", Sys.Date(), ".xlsx", sep=''),
           row.names=F,
           showNA=FALSE)

py_run_file('scripts/lion_king_pqc_dr_prediction.py')
# dbWriteTable(con, "final_data_dr", final_wf_df,row.names = FALSE, append = TRUE)
