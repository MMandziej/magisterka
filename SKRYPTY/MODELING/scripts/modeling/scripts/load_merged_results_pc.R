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


setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/model_training/scripts/docker_app")

# basic_plots = dget("basic_plots.R")
# basic_statistics_exploratory_analysis = dget("basic_statistics_exploratory_analysis.R")
# correlations_exploratory_analysis = dget("correlations_exploratory_analysis.R")
# expected_freq_exploratory_analysis = dget("expected_freq_exploratory_analysis.R")
# histogram_exploratory_analysis = dget("histogram_exploratory_analysis.R")
# boxplot_exploratory_analysis = dget("boxplot_exploratory_analysis.R")
# plotting_freq_exploratory_analysis = dget("plotting_freq_exploratory_analysis.R")
# basic_plots = dget("basic_plots.R")
# selected_features_table = dget("selected_features_table.R")
# feature_importance_table = dget("feature_importance_table.R")
# quantiles_and_IQR = dget("quantiles_and_IQR.R")
# barchart_classes = dget("barchart_classes.R")
# model_vs_time = dget("model_vs_time.R")  
# histogram_error_ratio_model_performance = dget("histogram_error_ratio_model_performance.R")
# histogram_box_avg_score = dget("histogram_box_avg_score.R")
# CalculateAUC = dget("CalculateAUC.R")
# fastAUC = dget("fastAUC.R")
# data_preprocessing = dget("data_preprocessing.R")
# plot_model_performance = dget("plot_model_performance.R")
# cut_off_distribution_table = dget("cut_off_distribution_table.R")
# AI_Assistant = dget("AI_Assistant_LK_app.R")
 
# ### FEATURE SELECTION - FULL DATASET ###
# dataset_fs <- as.data.frame(read_excel("QC_WF_HT_data_PC.xlsx"))
# dataset_fs <- dataset_fs[ , !(names(dataset_fs) %in% c("X1"))]
# 
# ### FEATURE SELECTION - FEATURES ###
# colnames_fs <- as.data.frame(read_csv("cat_colnames.csv"))
# #colnames_fs <- colnames_fs[ , !(names(colnames_fs) %in% c("X1" ))]
# 
# ### FEATURE SELECTION - MODELS ###
# Lasso_merged <- as.data.frame(read_csv("lasso.csv"))
# Boruta_merged <- as.data.frame(read_csv("boruta.csv"))
# RF_merged <- as.data.frame(read_csv("rf.csv"))
# 
# Variable_importance_all_methods_merged = list(Lasso_merged,
#                                               Boruta_merged,
#                                               RF_merged)
# 
# ### MODEL PERFORMANCE ###
# nn_results_train <- as.data.frame(read_csv("nn_train_merged.csv"))
# nn_results_test <- as.data.frame(read_csv("nn_test_merged.csv"))
# nn_results1 = list(nn_results_test, nn_results_train)
# 
# gbm_results_train <- as.data.frame(read_csv("gbm_train_merged.csv"))
# gbm_results_test <- as.data.frame(read_csv("gbm_test_merged.csv"))
# gbm_results1 = list(gbm_results_test, gbm_results_train)
# 
# rf_results_train <- as.data.frame(read_csv("rf_train_merged.csv"))
# rf_results_test <- as.data.frame(read_csv("rf_test_merged.csv"))
# rf_results1 = list(rf_results_test, rf_results_train)

### DISPLAY DATA IN AI ASSITANT ###
load("pc_app_data1.RData")

AI_Assistant(dataset = dataset_fs,
             stage = 'Model_results',
             Variable_importance_all_methods = Variable_importance_all_methods_merged,
             colnames_feature_selection = colnames_fs, #colnames(dataset_dummy_cat1), # colnames(dataset_dummy)
             nn_results = nn_results1,
             gbm_results = gbm_results1,
             rf_results = rf_results1)
