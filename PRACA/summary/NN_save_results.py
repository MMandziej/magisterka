from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from tensorflow.keras.models import load_model


best_model = load_model(r'model_training\results\nn\ALL_DATA\BORUTA\nn_results_full_data_boruta_2020-08-19.h5')

train_data = pd.read_csv(r'data_train_under_inputed.csv')
test_data = pd.read_csv(r'data_test_under_inputed.csv')

train_id = train_data.pop('NIP')
test_id = test_data.pop('NIP')

train_labels = train_data.pop('Label')
test_labels = test_data.pop('Label')

train_datestamp = train_data.pop('DataUpadlosci')
test_datestamp = test_data.pop('DataUpadlosci')

boruta_importance = pd.read_excel(r'model_training/R_DUMPS/Boruta_variable_importance_under.xlsx')
boruta_importance = boruta_importance.sort_values(by=['normHits', 'meanImp'],
                                                  ascending=True)
boruta_features = list(
    boruta_importance[boruta_importance['decision'] == 'Confirmed'].V7)
boruta_features = [c for c in boruta_features if c not in [
    'DeclaredAccountsCount', 'RemovalDaysAgo',
    'X6', 'P4', 'RevenueToWages', 'RevenueToCash'
    ]]

models_cols = ['EMISLegalForm_Other', 'ExpiredLicenses', 'ActiveLicenses', 'NoMail_NIE', 'FormaWlasnosci_WĹASNOĹšÄ† PRYWATNA KRAJOWA POZOSTAĹA', 'FormaWlasnosci_WĹASNOĹšÄ† ZAGRANICZNA', 'VirtualAccountsPresence_NIE', 'NoMail_TAK', 'PhoneNotPresent_NIE', 'PhoneNotPresent_TAK', 'FormaWlasnosci_Other', 'FormaWlasnosci_WĹASNOĹšÄ† KRAJOWYCH OSĂ“B FIZYCZNYCH', 'SpecialLegalForm_SPĂ“ĹKI JAWNE', 'VirtualAccountsPresence_TAK', 'AdresBiuroWirtualne_NIE', 'RyzykownaDziaĹ‚alnoscGlowna_NIE', 'AdresLokal_TAK', 'NoFax_TAK', 'NoFax_NIE', 'CAACEksport_NIE', 'NoWebsite_NIE', 'NoWebsite_TAK', 'AdresLokal_NIE', 'CAACImport_NIE', 'AffiliatesCount', 'DescriptionNull_NIE', 'AdresLokal_BrakDanych', 'DescriptionNull_TAK', 'MainPKD_BrakDanych', 'CAACImport_BrakDanych', 'CAACEksport_BrakDanych', 'RyzykowneDzialalnosciDodatkowe_BrakDanych', 'RyzykownaDziaĹ‚alnoscGlowna_BrakDanych', 'AdresBiuroWirtualne_BrakDanych', 'NonCurrentLiabilities', 'ExternalIdsOthers', 'EMISLegalForm_PL-SK', 'RepresentationCount', 'RetainedEarnings', 'CashandCashEquivalents', 'SpecialLegalForm_SPĂ“ĹKI AKCYJNE', 'EMISLegalForm_PL-SJ', 'TotalAssets', 'ProfitBeforeIncomeTax', 'ROE', 'PropertyPlantAndEquipment', 'OperatingProfitEBIT', 'X10', 'TotalLiabilities', 'RyzykowneDzialalnosciDodatkowe_TAK', 'NetProfitLossForThePeriod', 'EMISLegalForm_PL-SA', 'DepreciationAmortization', 'X14', 'CurrentAssets', 'A3', 'A2', 'IncomeTax', 'RegisteredCapitalValue', 'NumberOfEmployees', 'CurrentLiabilities', 'PreviousNamesCount', 'ROA', 'WorkingCapital', 'SpecialLegalForm_SPĂ“ĹKI KOMANDYTOWE', 'X11', 'X8', 'EMISLegalForm_PL-SPZOO', 'LegalForm_JEDNOSTKA ORGANIZACYJNA NIEMAJÄ„CA OSOBOWOĹšCI PRAWNEJ', 'A4', 'BruttoMargin', 'ROS', 'LegalForm_OSOBA PRAWNA', 'DepreciationImpairment', 'X13', 'X9', 'SpecialLegalForm_SPĂ“ĹKI Z OGRANICZONÄ„ ODPOWIEDZIALNOĹšCIÄ„', 'EmployeeBenefitExpense', 'IssuedCapital', 'A5', 'PreviousNameChangeYearsAgo', 'TotalEquity', 'NetSalesRevenue', 'RyzykowneDzialalnosciDodatkowe_NIE', 'A1', 'P3', 'ExecutivesCount', 'AuditDaysAgo', 'Wiek', 'SecondaryPKDCount', 'OwnersCount']

# del train_data['Unnamed: 0']
# del test_data['Unnamed: 0']

test_data = test_data[boruta_features]  # boruta_features, models_cols
train_data = train_data[boruta_features]  # boruta_features, models_cols

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
print(auc_train, auc_test, ratio_train75, ratio_test75)

train_results.to_csv(r'model_training\final_models\nn_train_results.csv')
test_results.to_csv(r'model_training\final_models\nn_test_results.csv')
