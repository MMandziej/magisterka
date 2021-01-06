library(RColorBrewer)
library(RCurl)
#library(readxl)
library(dplyr)
library(ggplot2)
library(readr)
library(shinyWidgets)
library(plotly)
library(shiny)
library(DT)
library(shinythemes)
library(tidyr)
library(shinyjs)
library(shinyalert)
library(formattable)
library(shinydashboard)
library(stringr)
library(e1071)
library(dashboardthemes)
library(rpart)
library(rpart.plot)
library(naniar)


#setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/model_training/scripts/docker_app")
load("pc_app_data.RData")
AI_Assistant = dget("AI_Assistant_LK_app.R")


# basic_plots = dget("basic_plots.R")
# basic_statistics_exploratory_analysis = dget("basic_statistics_exploratory_analysis.R")
# histogram_exploratory_analysis = dget("histogram_exploratory_analysis.R")
# boxplot_exploratory_analysis = dget("boxplot_exploratory_analysis.R")
# CalculateAUC = dget("CalculateAUC.R")
# fastAUC = dget("fastAUC.R")
# plot_model_performance = dget("plot_model_performance.R")
# cut_off_distribution_table = dget("cut_off_distribution_table.R")


### DISPLAY DATA IN AI ASSITANT ###
AI_Assistant(dataset = dataset_fs,
             stage = 'Model_results',
             Variable_importance_all_methods = Variable_importance_all_methods_merged,
             colnames_feature_selection = colnames_fs, #colnames(dataset_dummy_cat1), # colnames(dataset_dummy)
             nn_results = nn_results1,
             gbm_results = gbm_results1,
             rf_results = rf_results1)
