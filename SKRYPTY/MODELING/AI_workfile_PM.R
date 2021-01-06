set.seed(100)

### Part 1 - load the functions
your_dir = "C:/Users/mmandziej001/Desktop/Projects/FAIT/Prediction Module/POLAND_DANE/MODELING/scripts/ai_asistant/"
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
AI_Assistant = dget(paste(your_dir,"AI_Assistant.R", sep=''))

# Part 2 - load dataset
# Make sure that dataset has features "Label" and "datestamp"
setwd("C:/Users/mmandziej001/Desktop/Projects/FAIT/Prediction Module/POLAND_DANE/MODELING/")
### change path to where you store iqa data
dataset = read_csv("model_training/data/RAW/dataset_inputed_plot.csv")
dataset = read_excel("model_training/data/RAW/data_EDA.xlsx")
dataset <- dataset %>% rename(Unique = NIP)
#dataset <- subset(dataset, select=c(Unique, Label:BruttoMargin))

colnames(dataset)[1]='Unique'
dataset$datestamp = as.POSIXct(as.character(dataset$DataUpadlosci), format = '%Y-%m-%d')
#dataset = dataset[!is.na(dataset$ProcessingUnit),]

dataset = as.data.frame(dataset)
### Part 3 - visualization of features
AI_Assistant(dataset = dataset, stage = 'Exploratory_analysis')

### Part 4 - small changes in dataset
# after initial analysis of the dataset, if needed :
# Remove unnesesary columns :
dataset_feature_selection = dataset
unused_columns = c('REGON', 'KRS', 'EMISID', 'DataUpadlosci', 'City', 'FiscalYear', 'FormaFinansowania',
                   'CompanyType', 'SegmentStockName', 'StatusVAT')
dataset_feature_selection = dataset_feature_selection[, -which(
  colnames(dataset_feature_selection) %in% unused_columns)]

# Merge somve classes into one (for factor categories only) with fractions < 3%
helper_1 = as.data.frame(prop.table(table(dataset$EMISLegalForm)))
dataset_feature_selection$EMISLegalForm=factor(
  ifelse(as.character(dataset_feature_selection$EMISLegalForm)%in%helper_1$Var1[helper_1$Freq>0.03],
         as.character(dataset_feature_selection$EMISLegalForm),'Other'))

helper_2 = as.data.frame(prop.table(table(dataset$RodzajRejestru)))
dataset_feature_selection$RodzajRejestru=factor(
  ifelse(as.character(dataset_feature_selection$RodzajRejestru)%in%helper_2$Var1[helper_2$Freq>0.01],
         as.character(dataset_feature_selection$RodzajRejestru),'Other'))

helper_3 = as.data.frame(prop.table(table(dataset$FormaWlasnosci)))
dataset_feature_selection$FormaWlasnosci=factor(
  ifelse(as.character(dataset_feature_selection$FormaWlasnosci)%in%helper_3$Var1[helper_3$Freq>0.03],
         as.character(dataset_feature_selection$FormaWlasnosci),'Other'))

helper_4 = as.data.frame(prop.table(table(dataset$SpecialLegalForm)))
dataset_feature_selection$SpecialLegalForm=factor(
  ifelse(as.character(dataset_feature_selection$SpecialLegalForm)%in%helper_4$Var1[helper_4$Freq>0.03],
         as.character(dataset_feature_selection$SpecialLegalForm),'Other'))

helper_5 = as.data.frame(prop.table(table(dataset$SegmentName)))
dataset_feature_selection$SegmentName=factor(
  ifelse(as.character(dataset_feature_selection$SegmentName)%in%helper_5$Var1[helper_5$Freq>0.03],
         as.character(dataset_feature_selection$SegmentName),'Other'))

helper_6 = as.data.frame(prop.table(table(dataset$MainPKD)))
dataset_feature_selection$MainPKD=factor(
  ifelse(as.character(dataset_feature_selection$MainPKD)%in%helper_6$Var1[helper_6$Freq>0.03],
         as.character(dataset_feature_selection$MainPKD),'Other'))

helper_7 = as.data.frame(prop.table(table(dataset$MainNAICSCodes)))
dataset_feature_selection$MainNAICSCodes=factor(
  ifelse(as.character(dataset_feature_selection$MainNAICSCodes)%in%helper_7$Var1[helper_7$Freq>0.03],
         as.character(dataset_feature_selection$MainNAICSCodes),'Other'))

helper_8 = as.data.frame(prop.table(table(dataset$Voivodeship)))
dataset_feature_selection$Voivodeship=factor(
  ifelse(as.character(dataset_feature_selection$Voivodeship)%in%helper_8$Var1[helper_8$Freq>0.03],
         as.character(dataset_feature_selection$Voivodeship),'Other'))


### save results after preprocessing of full dataset
setwd("C:/Users/mmandziej001/Desktop/Projects/FAIT/Prediction Module/POLAND_DANE/MODELING/")

save(list = ls(all.names = TRUE),
     file = "R_DUMPS/explanatory_analysis.RData")
# load("R_DUMPS/lk_explanatory_analysis_dr.RData")


### keep only obs with valid label
dataset_feature_selection = dataset_feature_selection[!is.na(dataset_feature_selection$Label),]

### remove rest of the columns with missing values 
dataset_feature_selection = dataset_feature_selection[ , colSums(is.na(dataset_feature_selection)) < 30000]
#write.csv(dataset_feature_selection, "model_training/results/merged/dataset_fs.csv", row.names = F)

### Part 5 - dummy the data
dataset_dummy = data_preprocessing(dataset_feature_selection,
                                   frozen_columns = c('Unique', 'datestamp', "Label" ),
                                   remove_na = T)
dataset_dummy = read_excel('model_training/data/RAW/dataset_undersampled_inputed_normalized_no_vat.xlsx')
colnames(dataset_dummy)[1]='Unique'
dataset_dummy$datestamp = as.POSIXct(as.character(dataset_dummy$DataUpadlosci), format = '%Y-%m-%d')
unused_columns = c('DataUpadlosci',
                   'EntityListedInVATRegistry_NIE', 'EntityListedInVATRegistry_TAK',
                   'RiskyRemovalBasis_BrakDanych', 'RiskyRemovalBasis_LikelyFraudulent', 'RiskyRemovalBasis_NaturalReason', 'RiskyRemovalBasis_NeverRemoved',
                   'MainProductsNull_NIE', 'MainProductsNull_TAK',
                   'SegmentName_Not listed', 'SegmentName_Other')
dataset_dummy = dataset_dummy[, -which(
  colnames(dataset_dummy) %in% unused_columns)]
### Part 6 - variable importance
RF_variable_importance = RF_feature_selection(dataset_dummy[,-which(
  colnames(dataset_dummy)=='datestamp')])
Lasso_variable_importance = Lasso_feature_selection(dataset_dummy[,-which(
  colnames(dataset_dummy)=='datestamp')],
  label_column = 'Label')
Boruta_variable_importance = Boruta_feature_selection(dataset_dummy[,-which(
  colnames(dataset_dummy)=='datestamp')],
  label_column = 'Label')

Variable_importance_all_methods = list(Lasso_variable_importance, Boruta_variable_importance, RF_variable_importance)

### Save all objects at the stage of feature selection
save(list = ls(all.names = TRUE),
     file = "model_training/R_DUMPS/feature_selection_inputed.RData")
write.csv(Lasso_variable_importance, "model_training/R_DUMPS/Lasso_variable_importance_inputed.csv", row.names = F)
write.csv(Boruta_variable_importance, "model_training/R_DUMPS/Boruta_variable_importance_inputed.csv", row.names = F)
write.csv(RF_variable_importance, "model_training/R_DUMPS/RF_variable_importance_inputed.csv", row.names = F)
load('model_training/R_DUMPS/feature_selection.RData')

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
          paste("R_DUMPS/dataset_dummy_grouped_time_train.csv"),
          row.names = F)
write.csv(dataset_dummy_grouped_time_test,
          paste("R_DUMPS/dataset_dummy_grouped_time_test.csv"),
          row.names = F)

### Part 9 - read results from modelling part 
### GBM ###
gbm_train_results = as.data.frame(read_csv("model_training/results/gbm/TRIMMED_DATA/gbm_train_results.csv"))
gbm_test_results = as.data.frame(read_csv("model_training/results/gbm/TRIMMED_DATA/gbm_test_results.csv"))
gbm_results = list(gbm_test_results, gbm_train_results)

### NN ###
nn_train_results = as.data.frame(read_csv("model_training/results/nn/TRIMMED_DATA/nn_train_results.csv"))
nn_test_results = as.data.frame(read_csv("model_training/results/nn/TRIMMED_DATA/nn_test_results.csv"))
nn_results = list(nn_test_results, nn_train_results)

### RF ###
rf_train_results = as.data.frame(read_csv("model_training/results/rf/TRIMMED_DATA/rf_train_results.csv"))
rf_test_results = as.data.frame(read_csv("model_training/results/rf/TRIMMED_DATA/rf_test_results.csv"))
rf_results = list(rf_test_results, rf_train_results)

### Part 10 - Final AI Assistant 
save(list = ls(all.names = TRUE),
     file = "model_training/R_DUMPS/model_performance.RData")
load("model_training/R_DUMPS/model_performance.RData")

#AI_Assistant = dget("C:/Users/mmandziej001/Desktop/FCU/SCRIPTS/predictive_qc_db/scripts/AI_Assistant_DB.R")
AI_Assistant(dataset = dataset_feature_selection,
             stage = 'Model_results',
             Variable_importance_all_methods = Variable_importance_all_methods,
             colnames_feature_selection = colnames(dataset_dummy), # colnames(dataset_dummy)
             nn_results = nn_results,
             gbm_results = gbm_results,
             rf_results = rf_results)
