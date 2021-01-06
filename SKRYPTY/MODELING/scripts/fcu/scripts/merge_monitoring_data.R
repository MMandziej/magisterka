library(readxl)
library(RODBC)
library(RPostgreSQL)
library(lubridate)
library(dplyr)
library(xlsx)

#set the directory to directory where the general monitoring directory
setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/monitoring/")
#load("data/lion_king_monitoring_data.RData")
#load("data/lion_king_monitoring_data_22052020.RData")
db_conn = odbcConnect("LOCAL_SQL_SERVER")

stats <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[stats]")
developement_dataset <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[development_dataset]")
general_data <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[general_data]")
monitoring_prod_data <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[monitoring_production_dataset]")
scored_cases_backlog <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[production_backlog]")
wf_all_data <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[workflow_data]")
wf_selected_cols <- c("GRID", "ProcessingUnit", "TLAssignedName", "CDDRiskLevel", "FATCA", "CRS", "ESR",
                      "ScreenedParties", "OwnershipLayers", "PartyType", "NO_errors_last_5_days_DR", "NO_cases_last_5_days_DR",
                      "NO_errors_last_month_DR", "NO_cases_month_DR", "Day", "Hour_numeric", "Group_cases", "Experience_proj",
                      "Experience_team", "Population_match", "BackupTime")
wf_selected_data <- wf_all_data[, wf_selected_cols]



# install last cut off file
scoring_date <- as.Date(format(Sys.time(), "%Y-%m-%d"))
reference_date <- as.Date(format(Sys.time()))-7
last_cut_off <- read_excel("data/wf/02062020 cut off.xlsx")

# merge data for monitoring
scored_df <- read_excel("data/scoring_output/scored_2020-06-03.xlsx")
scored_df$week <- floor_date(scored_df$BackupTime, 'week')

used_cols <- c('GRID', 'ProcessingUnit', 'TLAssignedName', 'CDDRiskLevel',
               'FATCA', 'CRS', 'ESR', 'ScreenedParties', 'OwnershipLayers', 'PartyType',
               'NO_errors_last_5_days_DR', 'NO_cases_last_5_days_DR', 'NO_errors_last_month_DR', 'NO_cases_month_DR',
               'Day', 'Hour_numeric', 'Group_cases', 'Experience_proj', 'Experience_team', 'Population_match',
               'BackupTime', 'Label', 'week', 'pqc', 'pqc_timestamp')

# keep only columns used in monitoring
#scored_df <- scored_df[, used_cols]

# join data about reworks
scored_df <- scored_df[, !names(scored_df) %in% 'DRReworkCount']
DF2 <- last_cut_off %>% filter(!is.na(DRCompletedDate), as.Date(DRCompletedDate) > as.Date("2020-04-01"))
DF2 <- DF2[order(DF2$DRSentToQCDate, decreasing = TRUE), ]
DF2 <- DF2[, c('GRID', 'DRReworkCount')]

scored_df <- merge(x = scored_df, y = DF2, by = "GRID", all.x=TRUE)
scored_df$Label <- ifelse(scored_df$DRReworkCount >= 1, 1, 0)
scored_df$Label[is.na(scored_df$Label)] <- 0

# rename for consistency in the tables
scored_df = scored_df %>% rename(scored_df_pqc = pqc,
                                 datestamp = pqc_timestamp)

# change col types
# numeric
scored_df$GRID <- as.numeric(scored_df$GRID)
scored_df$ScreenedParties <- as.numeric(as.character(scored_df$ScreenedParties))
scored_df$OwnershipLayers <- as.numeric(as.character(scored_df$OwnershipLayers))
scored_df$Experience_proj <- as.numeric(as.character(scored_df$Experience_proj))
scored_df$Experience_team <- as.numeric(as.character(scored_df$Experience_team))
scored_df$Label <- as.numeric(as.character(scored_df$Label))
# integer
scored_df$NO_errors_last_5_days_DR <- as.integer(as.character(scored_df$NO_errors_last_5_days_DR))
scored_df$NO_cases_last_5_days_DR <- as.integer(as.character(scored_df$NO_cases_last_5_days_DR))
scored_df$NO_errors_last_month_DR <- as.integer(as.character(scored_df$NO_errors_last_month_DR))
scored_df$NO_cases_month_DR <- as.integer(as.character(scored_df$NO_cases_month_DR))
scored_df$Group_cases <- as.integer(as.character(scored_df$Group_cases))

# trim scored data and change column types -> general_data / a
scored_df_a <- scored_df[, colnames(general_data)]
scored_df_all <- scored_df[, colnames(wf_all_data)]
scored_df_selected <- scored_df[, colnames(wf_selected_data)]
scored_df_monitoring <- scored_df[, colnames(monitoring_prod_data)]

# update stats table
german_TLs <- c('Makowska, M.M. (Malgorzata)', 'Bartczak, K. (Kamil)', 'Jaszewski, M. (Michal)',
                'Jastrzebowska, S. (Sonia)', 'Skrzynecki, P. (Piotr)')

# last_cut_off$week <- floor_date(last_cut_off$BackupTime, 'week')
cases_sent_qc <- last_cut_off %>% filter(CDDStatus == 'DR - Pending Signatory',
                                         !TLAssignedName %in% german_TLs,
                                         !PSStatus %in% c('4. Ready to check - excluded by Ops Mgmt'))

completed_cases <- last_cut_off[which(!is.na(last_cut_off$DRCompletedDate)),]
completed_cases_latest <- completed_cases[which(as.Date(completed_cases$DRCompletedDate) > reference_date), ]

# merge data with the latest batch
general_data = rbind(general_data, scored_df_a)
wf_all_data = rbind(wf_all_data, scored_df_all)
wf_selected_data = rbind(wf_selected_data, scored_df_selected)
monitoring_prod_data = rbind(monitoring_prod_data, scored_df_monitoring)
scored_cases_backlog = rbind(scored_cases_backlog, scored_df)
stats = rbind(stats, list(scoring_date, nrow(cases_sent_qc), nrow(completed_cases_latest)))

# TO COMPLETE
# update data about reworks
# scored_cases_backlog <- merge(x = scored_cases_backlog, y = DF2, by = "GRID", all.x=TRUE)

# Select completed cases
completed_cases_id <- completed_cases[which(as.Date(completed_cases$DRCompletedDate) > as.Date("2020-04-27")),] 
# scored backlog

# monitorng and prod data
prod_data = monitoring_prod_data[which(as.Date(monitoring_prod_data$datestamp) > as.Date("2020-04-01")),]
prod_data_temp <- merge(prod_data, select(last_cut_off, GRID, DRReworkCount), by = 'GRID', all.x=TRUE)



saved_objects <- c("developement_dataset", "monitoring_prod_data", "scored_cases_backlog", "stats", "last_cut_off",
                   "general_data", "wf_all_data", "wf_selected_data")

save(list = saved_objects,
     file = paste("data/lion_king_monitoring_data_", format(Sys.time(), "%d%m%Y"), ".RData", sep=''))

###
write.xlsx(general_data, "data/monitoring/general_data.xlsx", row.names=F, sheetName='[monitoring].[general_data]')
write.xlsx(wf_all_data, "data/monitoring/wf_all_merged.xlsx", row.names=F, sheetName='[monitoring].[workflow_data]')
write.xlsx(monitoring_prod_data, "data/monitoring/monitoring_production.xlsx", row.names=F, sheetName='[monitoring].[monitoring_production_dataset]')
write.xlsx(scored_cases_backlog, "data/monitoring/scored_cases_backlog.xlsx", row.names=F, sheetName='[dbo].[scored_cases_backlog]')
write.xlsx(stats, "data/monitoring/stats.xlsx", row.names=F, sheetName='[monitoring].[stats]')


###
tables_available <- sqlTables(db_conn)
# sqlSave(db_conn, stats, tablename = '[pred_qc_lion_king].[monitoring].[stats]', rownames = F, append = T)  #, index = 'date')
close(db_conn)
