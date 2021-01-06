from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from tensorflow.keras.models import load_model


best_model = load_model(r'model_training\results\PC\final_models\12_Minor\final_model.h5')

train_data = pd.read_csv(r'model_training\results\PC\final_models\12_Minor\dataset_dummy_grouped_time_train_minor.csv')
test_data = pd.read_csv(r'model_training\results\PC\final_models\12_Minor\dataset_dummy_grouped_time_test_minor.csv')

train_id = train_data.pop('Unique')
test_id = test_data.pop('Unique')

train_labels = train_data.pop('Label')
test_labels = test_data.pop('Label')

train_datestamp = train_data.pop('datestamp')
test_datestamp = test_data.pop('datestamp')

boruta_importance = pd.read_excel(r'model_training/data/ai_assistant_dumps/PC/10_Critical/Boruta_variable_importance_pc.xlsx')
boruta_importance = boruta_importance.sort_values(by=['normHits', 'meanImp'],
                                                  ascending=True)
boruta_features = list(
    boruta_importance[boruta_importance['decision'] == 'Confirmed'].V7)

models_cols = ['CORelationship_Major_last_5_checklists', 'COFATCA/CRS_Major_last_10_checklists', 'TLAssignedName_Bartczak__K___Kamil_', 'DRODD_(Office_Due_Diligence)_-_local_requirements_(if_applicable)_Major_last_10_checklists', 'CORisk_factors_Major_last_10_checklists', 'PartyType_Ultimate', 'PCControl_Major_last_10_checklists', 'TLAssignedName_Michalik__J___Justyna_', 'TLAssignedName_Yadav__N___Neha_', 'PCESR_Major_last_5_checklists', 'DRRelationship_Critical_last_10_checklists', 'DRODD_(Office_Due_Diligence)_-_local_requirements_(if_applicable)_Major_last_5_checklists', 'ProcessingCountry_BMG', 'Category_DE_AT', 'PCFATCA/CRS_Minor_last_5_checklists', 'Cases_last_5_days_of_PC', 'PCRisk_factors_Major_last_10_checklists', 'PCESR_Critical_last_5_checklists', 'ProcessingUnit_Gdansk', 'ProcessingUnit_MidCorp', 'PCDocumentation_standard_Major_last_10_checklists', 'DRControl_Major_last_5_checklists', 'COClient_Outreach_Major_last_5_checklists', 'PCESR_Major_last_10_checklists', 'CODocumentation_standard_Minor_last_10_checklists', 'COODD_(Office_Due_Diligence)_-_local_requirements_(if_applicable)_Major_last_5_checklists', 'TLAssignedName_Marcos_Cantabrana__I___Ivan_', 'DRRelationship_Major_last_10_checklists', 'COScreening_Major_last_5_checklists', 'COClient_Outreach_Major_last_10_checklists', 'PCRelationship_Critical_last_5_checklists', 'MLRORequest_FALSE', 'PCESR_Critical_last_10_checklists', 'MLRORequest_TRUE', 'TeamExperience', 'DRControl_Critical_last_5_checklists', 'OwnershipLayers', 'DRDocumentation_standard_Minor_last_5_checklists', 'PCFATCA/CRS_Critical_last_5_checklists', 'GroupCases', 'COScreening_Major_last_10_checklists', 'PCDocumentation_standard_Major_last_5_checklists', 'PCESR_Minor_last_10_checklists', 'DRDocumentation_standard_Minor_last_10_checklists', 'COODD_(Office_Due_Diligence)_-_local_requirements_(if_applicable)_Major_last_10_checklists', 'PCScreening_Major_last_5_checklists', 'PCScreening_Major_last_10_checklists', 'CasesGroupPercProcessed', 'PCDocumentation_standard_Minor_last_10_checklists', 'ProjectExperience', 'ScreenedParties', 'Cases_last_30_days_of_PC', 'DRClient_Outreach_Major_last_10_checklists', 'PCESR_Minor_last_5_checklists', 'DRClient_Outreach_Major_last_5_checklists', 'AnalystGroupPercProcessed', 'FirstGroupCase', 'PCDocumentation_standard_Minor_last_5_checklists']

# del train_data['Unnamed: 0']
# del test_data['Unnamed: 0']

test_data = test_data[models_cols]  # used_columns, boruta_features, models_cols
train_data = train_data[models_cols]  # used_columns, boruta_features, models_cols

# test results
test_predictions = best_model.predict(test_data)
test_predictions_df = pd.DataFrame(test_predictions)

test_results = pd.concat([test_id, test_datestamp, test_predictions_df, test_labels], axis=1)
test_results = test_results.rename(columns={0: "Score"})
test_results = test_results.sort_values(by='Score', axis=0, ascending=False)
len_test_75 = round(len(test_results) * 0.75)
positives_test = test_results['Label'].sum()
positives_test_75 = test_results.iloc[:len_test_75]['Label'].sum()
ratio_test75 = positives_test_75 / positives_test
        
SumTest = pd.DataFrame(np.cumsum(test_results['Label']))
SumTest = SumTest.rename(columns={'Label': 'Sum'})
test_results = pd.concat([test_results, SumTest], axis=1)
test_results.reset_index(inplace=True, drop=True)
X_coordinates = pd.DataFrame(np.arange(1, (test_results.shape[0]+1))/(test_results.shape[0]))
X_coordinates = X_coordinates.rename(columns={0: 'X_coordinates'})
y_coordinates = pd.DataFrame(test_results['Sum']/test_results['Sum'].max())
y_coordinates = y_coordinates.rename(columns={'Sum': 'y_coordinates'})
test_results = pd.concat([test_results, X_coordinates, y_coordinates], axis=1)
auc_test = roc_auc_score(test_labels, test_predictions_df)

# train results
train_predictions = best_model.predict(train_data)
train_predictions_df = pd.DataFrame(train_predictions)

train_results = pd.concat([train_id, train_datestamp, train_predictions_df, train_labels], axis=1)
train_results = train_results.rename(columns={0: "Score"})
train_results = train_results.sort_values(by='Score', axis=0, ascending=False)
len_train_75 = round(len(train_results) * 0.75)
positives_train = train_results['Label'].sum()
positives_train_75 = train_results.iloc[:len_train_75]['Label'].sum()
ratio_train75 = positives_train_75 / positives_train

SumTrain = pd.DataFrame(np.cumsum(train_results['Label']))
SumTrain = SumTrain.rename(columns={'Label': 'Sum'})
train_results = pd.concat([train_results, SumTrain], axis=1)
train_results.reset_index(inplace=True, drop=True)
X_coordinates = pd.DataFrame(np.arange(1, (train_results.shape[0]+1))/(train_results.shape[0]))
X_coordinates = X_coordinates.rename(columns={0: 'X_coordinates'})
y_coordinates = pd.DataFrame(train_results['Sum']/train_results['Sum'].max())
y_coordinates = y_coordinates.rename(columns={'Sum': 'y_coordinates'})
train_results = pd.concat([train_results, X_coordinates, y_coordinates], axis=1)
auc_train = roc_auc_score(train_labels, train_predictions_df)
print(auc_train, auc_test, ratio_train75, ratio_test75)

train_results.to_csv(r'model_training\results\PC\final_models\12_Minor\nn_train_results.csv')
test_results.to_csv(r'model_training\results\PC\final_models\12_Minor\nn_test_results.csv')
