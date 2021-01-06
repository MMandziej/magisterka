set.seed(100)
#### Welcome to Predictive QC workfile ####
# You will use this file to call functions related to AI_assistant, variable importance and model performance
# First, make sure that all of the libraries from ai_assistant/Scripts are required


### Part 1 - load the functions

your_dir = "C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/ai_asistant/Scripts/"
#your_dir=paste('C:/Users/',Sys.getenv("USERNAME"),'/Desktop/ai_asistant/Scripts/',sep = '')
basic_plots = dget(paste(your_dir,"basic_plots.R",sep=''))
basic_statistics_exploratory_analysis = dget(paste(your_dir,"basic_statistics_exploratory_analysis.R", sep=''))
correlations_exploratory_analysis = dget(paste(your_dir,"correlations_exploratory_analysis.R", sep=''))
expected_freq_exploratory_analysis = dget(paste(your_dir,"expected_freq_exploratory_analysis.R", sep=''))
histogram_exploratory_analysis = dget(paste(your_dir,"histogram_exploratory_analysis.R", sep=''))
boxplot_exploratory_analysis = dget(paste(your_dir,"boxplot_exploratory_analysis.R", sep=''))
plotting_freq_exploratory_analysis = dget(paste(your_dir,"plotting_freq_exploratory_analysis.R", sep=''))
basic_plots = dget(paste(your_dir,"basic_plots.R", sep=''))
selected_features_table = dget(paste(your_dir,"selected_features_table.R", sep=''))
feature_importance_table = dget(paste(your_dir,"feature_importance_table.R", sep=''))
plot_model_performance = dget(paste(your_dir,"plot_model_performance.R", sep=''))
quantiles_and_IQR = dget(paste(your_dir,"quantiles_and_IQR.R", sep=''))
barchart_classes = dget(paste(your_dir,"barchart_classes.R", sep=''))
model_vs_time = dget(paste(your_dir,"model_vs_time.R", sep=''))  
histogram_error_ratio_model_performance = dget(paste(your_dir,"histogram_error_ratio_model_performance.R", sep=''))
histogram_box_avg_score = dget(paste(your_dir,"histogram_box_avg_score.R", sep=''))
CalculateAUC = dget(paste(your_dir,"CalculateAUC.R", sep=''))
fastAUC = dget(paste(your_dir,"fastAUC.R", sep=''))
data_preprocessing = dget(paste(your_dir,"data_preprocessing.R", sep=''))
create_test_train = dget(paste(your_dir,"create_test_train.R", sep=''))
Lasso_feature_selection = dget(paste(your_dir,"Lasso_feature_selection.R", sep=''))
Boruta_feature_selection = dget(paste(your_dir,"Boruta_feature_selection.R", sep=''))
RF_feature_selection =  dget(paste(your_dir,"RF_feature_selection.R", sep=''))

AI_Assistant = dget("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/model_training/scripts/AI_Assistant_LK.R")

# Part 2 - load dataset

# Dataset should be already prepared in python/sql script and ready to visualize it in AI_assistant
# Make sure that dataset has features "Label" and "datestamp"

### change path to where you store iqa data
dataset = read_excel("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/data_prep/redevelopment data/QC_WF_HT_data_DR.xlsx")
colnames(dataset)[1]='Unique'
dataset$datestamp = as.POSIXct(as.character(dataset$datestamp), format = '%Y-%m-%d')
dataset = dataset[!is.na(dataset$ProcessingUnit),]
#dataset$datestamp = ifelse(is.nan(dataset$datestamp), dataset$Created, dataset$datestamp)
#dataset$Label = ifelse(dataset$Critical > 0 | dataset$Major > 0, 1, 0)

dataset = as.data.frame(dataset)
### Part 3 - visualization of features
AI_Assistant(dataset = dataset, stage = 'Exploratory_analysis')

### Part 4 - small changes in dataset
# after initial analysis of the dataset, if needed :

# Remove first cases for each analyst 
#dataset = dataset[dataset$analyst_cases_processed_all>0,] 

# Remove unnesesary columns : 
dataset_feature_selection = dataset
unused_columns = c('Created', 'PCSenttoQCDate', 'DRSentToQCDate', 'Critical', 'Major', 'Minor', 'PointsDeducted', 'Score',
                   'AnalystAssignedName', 'QCAssignedName', 'ProjectJoiningDate', 'TeamJoiningDate',
                   'Cases_last_5_days_of_CO', 'Cases_last_30_days_of_CO',
                   'Minor_last_5_checklistsCO', 'Major_last_5_checklistsCO',
                   'Critical_last_5_checklistsCO', 'Minor_last_10_checklistsCO',
                   'Major_last_10_checklistsCO', 'Critical_last_10_checklistsCO')
dataset_feature_selection = dataset_feature_selection[, -which(
  colnames(dataset_feature_selection) %in% unused_columns)]

### save results after preprocessing of full dataset
setwd("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_lion_king/")

save(list = ls(all.names = TRUE),
     file = "model_training/data/ai_assistant_dumps/lk_explanatory_analysis_dr.RData")
# load("model_training/data/ai_assistant_dumps/lk_explanatory_analysis1.RData")


### keep only obs with valid label
dataset_feature_selection = dataset_feature_selection[!is.na(dataset_feature_selection$Label),]

### remove rest of the columns with missing values 
dataset_feature_selection = dataset_feature_selection[ , colSums(is.na(dataset_feature_selection)) < 300]
#write.csv(dataset_feature_selection, "model_training/results/merged/dataset_fs.csv", row.names = F)

### Part 5 - dummy the data
dataset_dummy = data_preprocessing(dataset_feature_selection,
                                   frozen_columns = c('Unique', 'datestamp', "Label" ),
                                   remove_na = T)

### Part 6 - variable importance
Lasso_variable_importance = Lasso_feature_selection(dataset_dummy[,-which(
  colnames(dataset_dummy)=='datestamp')],
  label_column = 'Label')
Boruta_variable_importance = Boruta_feature_selection(dataset_dummy[,-which(
  colnames(dataset_dummy)=='datestamp')],
  label_column = 'Label')
RF_variable_importance = RF_feature_selection(dataset_dummy[,-which(
  colnames(dataset_dummy)=='datestamp')])

Variable_importance_all_methods = list(Lasso_variable_importance, Boruta_variable_importance, RF_variable_importance)

### Save all objects at the stage of feature selection
save(list = ls(all.names = TRUE),
     file = "model_training/data/ai_assistant_dumps/lk_feature_selection_dr.RData")
write.csv(Lasso_variable_importance, "model_training/data/ai_assistant_dumps/Lasso_variable_importance_dr.csv", row.names = F)
write.xlsx(Boruta_variable_importance, "model_training/data/ai_assistant_dumps/Boruta_variable_importance_dr.xlsx", row.names = F)
write.csv(RF_variable_importance, "model_training/data/ai_assistant_dumps/RF_variable_importance_dr.csv", row.names = F)
load('model_training/data/ai_assistant_dumps/lk_feature_selection1.RData')

### Part 7 - AI Assistant with feature importance
AI_Assistant(dataset = dataset,
             stage = 'Feature_selection',
             Variable_importance_all_methods = Variable_importance_all_methods,
             colnames_feature_selection = colnames(dataset_dummy)[-which(
               colnames(dataset_dummy)=='datestamp')])


### Part 8 - create test and train dataset 
#set.seed(100)
#smp_size <- floor(0.8 * nrow(dataset_dummy_cat1))
#train_ind <- sample(seq_len(nrow(dataset_dummy_cat1)), size = smp_size)
#dataset_dummy_grouped_time_train_cat1 <- dataset_dummy_cat1[train_ind, ]
#dataset_dummy_grouped_time_test_cat1 <- dataset_dummy_cat1[-train_ind, ]

dataset_dummy_grouped_time_test = create_test_train(dataset_dummy)[[1]]
dataset_dummy_grouped_time_train = create_test_train(dataset_dummy)[[2]]

plot_ly(data=dataset_dummy_grouped_time_test,
        x=~floor_date(datestamp, unit = 'weeks'),
        type='histogram',
        color =~Label) %>%
  add_trace(data = dataset_dummy_grouped_time_train,
            x=~floor_date(datestamp, unit = 'weeks'),
            type='histogram',
            color =~Label,
            inherit=F)

table(dataset_dummy_grouped_time_train$Label)
table(dataset_dummy_grouped_time_test$Label)
error_ratio_train = nrow(dataset_dummy_grouped_time_train[dataset_dummy_grouped_time_train$Label == 1,]) / nrow(dataset_dummy_grouped_time_train)
error_ratio_test = nrow(dataset_dummy_grouped_time_test[dataset_dummy_grouped_time_test$Label == 1,]) / nrow(dataset_dummy_grouped_time_test)
print(error_ratio_train)
print(error_ratio_test)

write.csv(dataset_dummy_grouped_time_train,
          paste("model_training/data/dataset_dummy_grouped_time_train_dr.csv"),
          row.names = F)
write.csv(dataset_dummy_grouped_time_test,
          paste("model_training/data/dataset_dummy_grouped_time_test_dr.csv"),
          row.names = F)

### Part 9 - read results from modelling part 
### GBM ###
gbm_train_results = as.data.frame(read_csv("model_training/results/gbm/gbm_train_results.csv"))
gbm_test_results = as.data.frame(read_csv("model_training/results/gbm/gbm_test_results.csv"))
gbm_results = list(gbm_test_results, gbm_train_results)

### NN ###
nn_train_results = as.data.frame(read_csv("model_training/results/nn/nn_train_results.csv"))
nn_test_results = as.data.frame(read_csv("model_training/results/nn/nn_test_results.csv"))
nn_results = list(nn_test_results, nn_train_results)

### RF ###
rf_train_results = as.data.frame(read_csv("model_training/results/crf/rf_train_results.csv"))
rf_test_results = as.data.frame(read_csv("model_training/results/crf/rf_test_results.csv"))
rf_results = list(rf_test_results, rf_train_results)

### Part 10 - Final AI Assistant 
save(list = ls(all.names = TRUE),
     file = "model_training/data/ai_assistant_dumps/lk_model_performance.RData")
load("model_training/data/ai_assistant_dumps/lk_model_performance.RData")

#AI_Assistant = dget("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_db/scripts/AI_Assistant_DB.R")
AI_Assistant(dataset = dataset_feature_selection,
             stage = 'Model_results',
             Variable_importance_all_methods = Variable_importance_all_methods,
             colnames_feature_selection = colnames(dataset_dummy), # colnames(dataset_dummy)
             nn_results = nn_results,
             gbm_results = gbm_results,
             rf_results = rf_results)

