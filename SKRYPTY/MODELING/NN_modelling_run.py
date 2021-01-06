import pandas as pd
import os
import random

from sklearn.model_selection import train_test_split
# from skmultilearn.modelselection import iterativetraintestsplit

from NN_modelling_restructured import full_search, narrow_search, backward_search, forward_search


train_data = pd.read_csv('model_training/data/data_train_under_inputed.csv')
test_data = pd.read_csv('model_training/data/data_test_under_inputed.csv')
print(len(train_data), sum(train_data['Label']), round(sum(train_data['Label']) / len(train_data) * 100, 2))
print(len(test_data), sum(test_data['Label']), round(sum(test_data['Label']) / len(test_data) * 100, 2))

train_id = train_data.pop('NIP')
test_id = test_data.pop('NIP')

train_labels = train_data.pop('Label')
test_labels = test_data.pop('Label')

train_datestamp = train_data.pop('DataUpadlosci')
test_datestamp = test_data.pop('DataUpadlosci')

boruta_importance = pd.read_excel('model_training/R_DUMPS/Boruta_variable_importance_under.xlsx')
boruta_importance = boruta_importance.sort_values(by=['normHits', 'meanImp'],
                                                  ascending=True)
boruta_features = list(
    boruta_importance[boruta_importance['decision'] == 'Confirmed'].V7)
boruta_pred_power = list(boruta_importance.V7)
boruta_features = [c for c in boruta_features if c not in [
    'DeclaredAccountsCount', 'RemovalDaysAgo',
    'X6', 'RevenueToWages', 'P4', 'RevenueToCash']]
#model_cols = ['ScreenedParties', 'OwnershipLayers', 'GroupCases', 'FirstGroupCase', 'PopulationMatch', 'HourNumeric', 'Cases_last_5_days_of_DR', 'Cases_last_5_days_of_PC', 'Cases_last_30_days_of_DR', 'Cases_last_30_days_of_PC', 'Minor_last_5_checklistsDR', 'Major_last_5_checklistsDR', 'Critical_last_5_checklistsDR', 'Minor_last_10_checklistsDR', 'Major_last_10_checklistsDR', 'Critical_last_10_checklistsDR', 'Minor_last_5_checklistsPC', 'Major_last_5_checklistsPC', 'Critical_last_5_checklistsPC', 'Minor_last_10_checklistsPC', 'Major_last_10_checklistsPC', 'Critical_last_10_checklistsPC', 'ProjectExperience', 'TeamExperience', 'TLAssignedName_Skrzynecki__P___Piotr_', 'TLAssignedName_Jastrzebowska__S___Sonia_', 'TLAssignedName_Makowska__M_M___Malgorzata_', 'TLAssignedName_Jurojc__M___Mateusz_', 'TLAssignedName_Yadav__N___Neha_', 'TLAssignedName_Bartczak__K___Kamil_', 'TLAssignedName_Bonczkowski__P___Pawel_', 'TLAssignedName_Wojciechowska__M___Magdalena_', 'TLAssignedName_Kolodziejczyk__A___Anna_', 'TLAssignedName_Reglinska__J___Joanna_', 'TLAssignedName_Michalik__J___Justyna_', 'TLAssignedName_Marcos_Cantabrana__I___Ivan_', 'TLAssignedName_Rybka__I_A___Izabela_Anna_', 'TLAssignedName_Armannsson__G___Gabriela_', 'TLAssignedName_Jaszewski__M___Michal_', 'TLAssignedName_Helak__G___Grzegorz_', 'ProcessingUnit_MidCorp', 'CDDRiskLevel_Normal', 'CDDRiskLevel_Low', 'CDDRiskLevel_Increased', 'CDDRiskLevel_Other', 'FATCA_FALSE', 'FATCA_TRUE', 'CRS_FALSE', 'CRS_TRUE', 'ESR_ESR_linked', 'ESR_No_ESR_needed', 'ESR_Full_ESR_review', 'PartyType_Subsidiary', 'PartyType_Ultimate', 'Weekday_Tuesday', 'Weekday_Monday', 'Weekday_Friday', 'Weekday_Wednesday', 'Weekday_Thursday']

boruta_train_data = train_data[boruta_features]#[boruta_features]
boruta_test_data = test_data[boruta_features]#[boruta_features]


models_list, models_params, output_table = full_search(
    train_data, train_labels, test_data, test_labels,
    max_iter=2000, max_hours=5.5,
    min_auc=0.70, max_overfit_auc=0.02,
    prefix='nn_results_all_features')

boruta_models_list, boruta_models_params, boruta_output_table = full_search(
    boruta_train_data, train_labels, boruta_test_data, test_labels,
    max_iter=2000, max_hours=5.5,
    min_auc=0.70, max_overfit_auc=0.02,
    prefix='nn_results_boruta_')

model_list_narrow, models_params_narrow, narrow_output_table = narrow_search(
    train_data, train_labels, test_data, test_labels,
    columns_to_drop=boruta_pred_power,
    max_iter=3, max_hours=0.55,
    min_auc=0.75, max_overfit_auc=0.02,
    prefix='nn_results_selected_columns')

model_list_backward, models_params_backward, backward_output_table = backward_search(
    train_data, train_labels, test_data, test_labels,
    columns_to_drop=boruta_pred_power,
    max_iter=10, max_hours=1,
    min_auc=0.71, max_overfit_auc=0.02,
    prefix='nn_results_selected_columns')
