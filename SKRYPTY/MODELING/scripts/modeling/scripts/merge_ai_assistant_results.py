import glob
import os
import pandas as pd
import sys

# prefixes of categories
prefixes = ['AllError', 'NoMinor']

# define function to add techincal cat columns
def add_labels_guid(file, guid):
    df = pd.read_csv(file)
    df = df[['Unique', 'datestamp', 'Score', 'Label', 'Sum',
             'X_coordinates', 'y_coordinates']]
    if guid == '_nominor':
        temp = 'NoMinor'
    else:
        temp = 'AllTypes'
    df['LabelType'] = temp
    return df

# category mapping
category_mapping = {
    1 : 'Indentifying and Understanding the Client',
    2 : 'Nature of Business and Purpose of Relationship',
    3 : 'Source of Funds',
    4 : 'Verify Legal Representatives',
    5 : 'Client Ownership Structure',
    6 : 'Source of Wealth',
    7 : 'Screening',
    8 : 'PEPs',
    9 : 'Customer Risk Classification',
    10	: 'Approvals and Sign-Off',
    11	: 'Localisation Factors',
    12	: 'Vendor specific',
    13	: 'Critical Mistake DD level and entity type',
    14	: 'Documentation quality',
    15	: 'Client Outreach Form ',
    #16	: 'DD System not used correctly',
    17: 'Data Quality Issue',
    18: 'Documents incorrectly uploaded'}

### FEATURE SELECTION - RESULTS ###
# create list of category paths
fs_directory = r'model_training/data/ai_assistant_dumps/'
guids = ['', '_nominor']

# create list of fs files
boruta = [fs_directory + 'Boruta_variable_importance' + guid + '.xlsx' for guid in guids]
lasso = [fs_directory + '/Lasso_variable_importance' + guid + '.csv'  for guid in guids]
random_forest = [fs_directory + '/RF_variable_importance' + guid + '.csv' for guid in guids]

# load csv files as data frames
boruta_dfs = []
for file, guid in zip(boruta, guids):
    if guid == '_nominor':
        temp = 'NoMinor'
    else:
        temp = 'AllTypes'
    df = pd.read_excel(file)
    df['LabelType'] = temp
    boruta_dfs.append(df)

lasso_dfs = []
for file, guid in zip(lasso, guids):
    if guid == '_nominor':
        temp = 'NoMinor'
    else:
        temp = 'AllTypes'
    df = pd.read_csv(file)
    df['LabelType'] = temp
    lasso_dfs.append(df)

random_forest_dfs = []
for file, guid in zip(random_forest, guids):
    if guid == '_nominor':
        temp = 'NoMinor'
    else:
        temp = 'AllTypes'    
    df = pd.read_csv(file)
    df['LabelType'] = temp
    random_forest_dfs.append(df)

#  merged all categories
boruta_results = pd.concat(boruta_dfs)
lasso_results = pd.concat(lasso_dfs)
random_forest_results = pd.concat(random_forest_dfs)

# export results to csv files to show in AI assistant
boruta_results.to_csv(r"model_training\results\merged\boruta.csv")
lasso_results.to_csv(r"model_training\results\merged\lasso.csv")
random_forest_results.to_csv(r"model_training\results\merged\rf.csv")

### FEATURE SELECTION - COLNAMES ###
# create list of category paths
datasets = ['model_training/data/dataset_dummy_grouped_time_test' + guid + '.csv' for guid in guids]

# load csv files as data frames
datasets_cols = {}
for file, guid in zip(datasets, guids):
    if guid == '_nominor':
        temp = 'NoMinor'
    else:
        temp = 'AllTypes'
    df = pd.read_csv(file)
    datasets_cols[temp] = ','.join(list(df))
datasets_df = pd.DataFrame(datasets_cols.items(), columns=['LabelType', 'Cols'])
datasets_df.to_csv(r"model_training\results\merged\cat_colnames.csv")

## MODEL RESULTS ###
# create lists of all results files
gbm_train = ['model_training/results/gbm/gbm_train_results' + guid + '.csv' for guid in guids]
gbm_test = ['model_training/results/gbm/gbm_test_results' + guid + '.csv' for guid in guids]

nn_train = ['model_training/results/nn/nn_train_results' + guid + '.csv' for guid in guids]
nn_test = ['model_training/results/nn/nn_test_results' + guid + '.csv' for guid in guids]

crf_train = ['model_training/results/crf/rf_train_results' + guid + '.csv' for guid in guids]
crf_test = ['model_training/results/crf/rf_test_results' + guid + '.csv' for guid in guids]

# load csv files as data frames
gbm_train_dfs = []
for file, guid in zip(gbm_train, guids):
    df = add_labels_guid(file, guid)
    gbm_train_dfs.append(df)

gbm_test_dfs = []
for file, guid in zip(gbm_test, guids):
    df = add_labels_guid(file, guid)
    gbm_test_dfs.append(df)

nn_train_dfs = []
for file, guid in zip(nn_train, guids):
    df = add_labels_guid(file, guid)
    nn_train_dfs.append(df)

nn_test_dfs = []
for file, guid in zip(nn_test, guids):
    df = add_labels_guid(file, guid)
    nn_test_dfs.append(df)

crf_train_dfs = []
for file, guid in zip(crf_train, guids):
    df = add_labels_guid(file, guid)
    crf_train_dfs.append(df)

crf_test_dfs = []
for file, guid in zip(crf_test, guids):
    df = add_labels_guid(file, guid)
    crf_test_dfs.append(df)

#  merged all categories
gbm_train_results = pd.concat(gbm_train_dfs)
gbm_test_results = pd.concat(gbm_test_dfs)
nn_train_results = pd.concat(nn_train_dfs)
nn_test_results = pd.concat(nn_test_dfs)
rf_train_results = pd.concat(crf_train_dfs)
rf_test_results = pd.concat(crf_test_dfs)

# export results to csv files to show in AI assistant
gbm_train_results.to_csv(r"model_training\results\merged\gbm_train_merged.csv")
gbm_test_results.to_csv(r"model_training\results\merged\gbm_test_merged.csv")
nn_train_results.to_csv(r"model_training\results\merged\nn_train_merged.csv")
nn_test_results.to_csv(r"model_training\results\merged\nn_test_merged.csv")
rf_train_results.to_csv(r"model_training\results\merged\rf_train_merged.csv")
rf_test_results.to_csv(r"model_training\results\merged\rf_test_merged.csv")
