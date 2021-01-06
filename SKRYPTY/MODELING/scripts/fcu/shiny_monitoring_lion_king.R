library(gtools)
library(lubridate)
library(plotly)
#library(RODBC)
library(shiny)
library(shinydashboard)
library(shinyWidgets)
library(shinyalert)
library(stringr)
library(dplyr)
#library(xlsx)
library(DT)
library(readxl)

# set working directory to the script path
#setwd(dirname(rstudioapi::getSourceEditorContext()$path))

### load data from DB and latest wofklow data from flat file
#db_conn = odbcConnect("LOCAL_SQL_SERVER")
#stats <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[monitoring].[stats]")
#full_backlog <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[production].[results_merged]")
#general_data <- sqlQuery(db_conn, "SELECT * FROM [pred_qc_lion_king].[production].[features]
#                         WHERE DRSentToQCDate > '2020-06-08 0:00:00.000'")

### load data from flat files for dynamic update
# stats
stats <- read_excel('sql_dumps/stats.xlsx')
stats$date <- as.POSIXct(stats$date)
# results_merged
full_backlog <- read_excel('sql_dumps/results_merged.xlsx')
full_backlog$GRID <- as.numeric(full_backlog$GRID)
full_backlog$pqc_timestamp <- as.POSIXct(full_backlog$pqc_timestamp)
full_backlog$Stage <- as.factor(full_backlog$Stage)
# features
general_data <- as.data.frame(read_excel('sql_dumps/features.xlsx'))
general_data$DRSentToQCDate <- as.POSIXct(general_data$DRSentToQCDate)
general_data <- general_data %>% filter(DRSentToQCDate > '2020-06-08 0:00:00.000')
general_data$BackupTime <- as.POSIXct(general_data$BackupTime)
general_data$week <- as.POSIXct(general_data$week)

general_data$GRID <- as.integer(general_data$GRID)
general_data$Label <- as.integer(general_data$Label)
general_data$FATCA <- as.integer(general_data$FATCA)
general_data$CRS <- as.integer(general_data$CRS)
general_data$FirstGroupCase <- as.integer(general_data$FirstGroupCase)
general_data$TeamExperience <- as.integer(general_data$TeamExperience)
general_data$ProjectExperience <- as.integer(general_data$ProjectExperience)

general_data$HourNumeric <- as.numeric(general_data$HourNumeric)

general_data$AnalystAssignedName <- as.factor(general_data$AnalystAssignedName)
general_data$QCAssignedName <- as.factor(general_data$QCAssignedName)
general_data$TLAssignedName <- as.factor(general_data$TLAssignedName)
general_data$ProcessingUnit <- as.factor(general_data$ProcessingUnit)
general_data$CDDRiskLevel <- as.factor(general_data$CDDRiskLevel)
general_data$ESR <- as.factor(general_data$ESR)
general_data$PartyType <- as.factor(general_data$PartyType)
general_data$Weekday <- as.factor(general_data$Weekday)

### load functions to display charts / tables
source('scripts/barchart_classes.R')
source('scripts/histogram_exploratory_analysis_boat.R')
source('scripts/dist_check_new.R')
source('scripts/dist_alert_check.R')
source('scripts/create_summary_stages_table.R')
source('scripts/cases_avg_score_plot.R')
source('scripts/main_plot_vs_time.R')
source('scripts/main_plot_vs_time_pop_comparison.R')
source('scripts/plot_variable_impact.R')
source('scripts/impact_on_score.R')
source('scripts/calculate_production_savings.R')

shiny::runApp("shinyapp.R", launch.browser = FALSE, port = 8080, host = "0.0.0.0")
