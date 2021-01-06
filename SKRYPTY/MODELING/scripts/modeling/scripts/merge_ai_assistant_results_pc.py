import os
import pandas as pd
import sys

# prefixes of categories
prefixes = ['Documentation standard', 'Risk factors', 'Screening', 'ESR',
            'Client Outreach', 'Relationship', 'ODD (Office Due Diligence) - local requirements (if applicable)',
            'FATCA_CRS', 'Control', 'Critical', 'Major', 'Minor']

# define function to add techincal cat columns
def add_labels_guid(file, guid):
    df = pd.read_csv(file)
    df = df[['Unique', 'datestamp', 'Score', 'Label', 'Sum',
             'X_coordinates', 'y_coordinates']]
    df['CategoryName'] = guid
    return df

# category mapping
category_mapping = {
    1 : 'Documentation standard',
    2 : 'Risk factors',
    3 : 'Screening',
    4 : 'ESR',
    5 : 'Client Outreach',
    6 : 'Relationship',
    7 : 'ODD (Office Due Diligence) - local requirements (if applicable)',
    8 : 'FATCA_CRS',
    9 : 'Control',
    10	: 'Critical',
    11	: 'Major',
    12	: 'Minor'}

### FEATURE SELECTION - RESULTS ###
# create list of category paths
fs_directory = r'model_training/data/ai_assistant_dumps/PC/'
directories = [r'model_training/data/ai_assistant_dumps/PC/' + str(i) + '_' + j + '/'
               for i, j in category_mapping.items()]
guids = [str(i) + '_' + j + '/' for i, j in category_mapping.items()]

# create list of fs files
boruta = [fs_directory + 'Boruta_variable_importance_pc.xlsx' for fs_directory in directories]
lasso = [fs_directory + '/Lasso_variable_importance_pc.csv' for fs_directory in directories]
random_forest = [fs_directory + '/RF_variable_importance_pc.csv' for fs_directory in directories]

# load csv files as data frames
boruta_dfs = []
for file, guid in zip(boruta, category_mapping.values()):
    df = pd.read_excel(file)
    df['CategoryName'] = guid
    boruta_dfs.append(df)

lasso_dfs = []
for file, guid in zip(lasso, category_mapping.values()):
    df = pd.read_csv(file)
    df['CategoryName'] = guid
    lasso_dfs.append(df)

random_forest_dfs = []
for file, guid in zip(random_forest, guids):
    df = pd.read_csv(file)
    df['CategoryName'] = guid
    random_forest_dfs.append(df)

#  merged all categories
boruta_results = pd.concat(boruta_dfs)
lasso_results = pd.concat(lasso_dfs)
random_forest_results = pd.concat(random_forest_dfs)

# export results to csv files to show in AI assistant
boruta_results.to_csv(r"model_training\results\PC\merged\boruta.csv")
lasso_results.to_csv(r"model_training\results\PC\merged\lasso.csv")
random_forest_results.to_csv(r"model_training\results\PC\merged\rf.csv")

### FEATURE SELECTION - COLNAMES ###
# create list of category paths
datasets = ['model_training/data/PC/dataset_dummy_grouped_time_test_cat' + str(guid) + '.csv'
            for guid in category_mapping.keys()]

# load csv files as data frames
datasets_cols = {}
for file, guid in zip(datasets, category_mapping.values()):
    df = pd.read_csv(file)
    datasets_cols[guid] = ','.join(list(df))
datasets_df = pd.DataFrame(datasets_cols.items(), columns=['CategoryName', 'Cols'])
datasets_df.to_csv(r"model_training\results\PC\merged\cat_colnames.csv")

## MODEL RESULTS ###
# create lists of all results files
gbm_train = ['model_training/results/PC/gbm/' + guid + 'gbm_train_results.csv'
             for guid in guids]
gbm_test = ['model_training/results/PC/gbm/' + guid + 'gbm_test_results.csv'
             for guid in guids]

nn_train = ['model_training/results/PC/nn/' + guid + 'nn_train_results.csv'
             for guid in guids]
nn_test = ['model_training/results/PC/nn/' + guid + 'nn_test_results.csv'
             for guid in guids]

crf_train = ['model_training/results/PC/crf/' + guid + 'rf_train_results.csv'
             for guid in guids]
crf_test = ['model_training/results/PC/crf/' + guid + 'rf_test_results.csv'
             for guid in guids]

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
gbm_train_results.to_csv(r"model_training\results\PC\merged\gbm_train_merged.csv")
gbm_test_results.to_csv(r"model_training\results\PC\merged\gbm_test_merged.csv")
nn_train_results.to_csv(r"model_training\results\PC\merged\nn_train_merged.csv")
nn_test_results.to_csv(r"model_training\results\PC\merged\nn_test_merged.csv")
rf_train_results.to_csv(r"model_training\results\PC\merged\rf_train_merged.csv")
rf_test_results.to_csv(r"model_training\results\PC\merged\rf_test_merged.csv")
