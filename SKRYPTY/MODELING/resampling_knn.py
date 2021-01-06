import numpy as np
import pandas as pd
import imblearn

from collections import Counter
from copy import deepcopy
from imblearn.under_sampling import CondensedNearestNeighbour, RandomUnderSampler
from sklearn.impute import KNNImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = pd.read_excel(r'model_training/data/RAW/modelling_data_inputed_merged.xlsx')
drop_cols = [
    'REGON', 'KRS', 'EMISID', 'City', 'FiscalYear', 'FormaFinansowania',
    'CompanyType', 'SegmentStockName', 'StatusVAT', 'DividendCount',
    'SegmentName', 'SegmentStockName', 'SecondaryNAICSCount', 'MainNAICSCount',
    'MainProductsNull'
    ]

cols = [col for col in list(data) if col not in drop_cols]
data = data[cols]

### Merge underrepresented classes ###
# EMISLegalForm
EMISLegalForm_helper = data.groupby('EMISLegalForm').count()[['NIP']].reset_index(level=0)
EMISLegalForm_helper['EMISLegalFormFraction'] = EMISLegalForm_helper['NIP'] / len(data)
EMISLegalForm_helper_underrepresented = list(EMISLegalForm_helper[EMISLegalForm_helper['EMISLegalFormFraction'] < 0.03].EMISLegalForm)
data['EMISLegalForm'] = np.where(np.isin(data['EMISLegalForm'], EMISLegalForm_helper_underrepresented),
                                        'Other',
                                        data['EMISLegalForm'])

# LegalForm
LegalForm_helper = data.groupby('LegalForm').count()[['NIP']].reset_index(level=0)
LegalForm_helper['LegalFormFraction'] = LegalForm_helper['NIP'] / len(data)
LegalForm_helper_underrepresented = list(LegalForm_helper[LegalForm_helper['LegalFormFraction'] < 0.03].LegalForm)
data['LegalForm'] = np.where(np.isin(data['LegalForm'], LegalForm_helper_underrepresented),
                                        'Other',
                                        data['LegalForm'])

# RodzajRejestru
RodzajRejestru_helper = data.groupby('RodzajRejestru').count()[['NIP']].reset_index(level=0)
RodzajRejestru_helper['RodzajRejestruFraction'] = RodzajRejestru_helper['NIP'] / len(data)
RodzajRejestru_helper_underrepresented = list(RodzajRejestru_helper[RodzajRejestru_helper['RodzajRejestruFraction'] < 0.01].RodzajRejestru)
data['RodzajRejestru'] = np.where(np.isin(data['RodzajRejestru'], RodzajRejestru_helper_underrepresented),
                                        'Other',
                                        data['RodzajRejestru'])

# FormaWlasnosci
FormaWlasnosci_helper = data.groupby('FormaWlasnosci').count()[['NIP']].reset_index(level=0)
FormaWlasnosci_helper['FormaWlasnosciFraction'] = FormaWlasnosci_helper['NIP'] / len(data)
FormaWlasnosci_helper_underrepresented = list(FormaWlasnosci_helper[FormaWlasnosci_helper['FormaWlasnosciFraction'] < 0.03].FormaWlasnosci)
data['FormaWlasnosci'] = np.where(np.isin(data['FormaWlasnosci'], FormaWlasnosci_helper_underrepresented),
                                        'Other',
                                        data['FormaWlasnosci'])

# SpecialLegalForm
SpecialLegalForm_helper = data.groupby('SpecialLegalForm').count()[['NIP']].reset_index(level=0)
SpecialLegalForm_helper['SpecialLegalFormFraction'] = SpecialLegalForm_helper['NIP'] / len(data)
SpecialLegalForm_helper_underrepresented = list(SpecialLegalForm_helper[SpecialLegalForm_helper['SpecialLegalFormFraction'] < 0.03].SpecialLegalForm)
data['SpecialLegalForm'] = np.where(np.isin(data['SpecialLegalForm'], SpecialLegalForm_helper_underrepresented),
                                        'Other',
                                        data['SpecialLegalForm'])

# MainPKD
MainPKD_helper = data.groupby('MainPKD').count()[['NIP']].reset_index(level=0)
MainPKD_helper['MainPKDFraction'] = MainPKD_helper['NIP'] / len(data)
MainPKD_helper_underrepresented = list(MainPKD_helper[MainPKD_helper['MainPKDFraction'] < 0.03].MainPKD)
data['MainPKD'] = np.where(np.isin(data['MainPKD'], MainPKD_helper_underrepresented),
                                        'Other',
                                        data['MainPKD'])

# MainNAICSCodes
MainNAICSCodes_helper = data.groupby('MainNAICSCodes').count()[['NIP']].reset_index(level=0)
MainNAICSCodes_helper['MainNAICSCodesFraction'] = MainNAICSCodes_helper['NIP'] / len(data)
MainNAICSCodes_helper_underrepresented = list(MainNAICSCodes_helper[MainNAICSCodes_helper['MainNAICSCodesFraction'] < 0.03].MainNAICSCodes)
data['MainNAICSCodes'] = np.where(np.isin(data['MainNAICSCodes'], MainNAICSCodes_helper_underrepresented),
                                        'Other',
                                        data['MainNAICSCodes'])

# Voivodeship
Voivodeship_helper = data.groupby('Voivodeship').count()[['NIP']].reset_index(level=0)
Voivodeship_helper['VoivodeshipFraction'] = Voivodeship_helper['NIP'] / len(data)
Voivodeship_helper_underrepresented = list(Voivodeship_helper[Voivodeship_helper['VoivodeshipFraction'] < 0.03].Voivodeship)
data['Voivodeship'] = np.where(np.isin(data['Voivodeship'], Voivodeship_helper_underrepresented),
                                        'Other',
                                        data['Voivodeship'])

### PREPROCESSING ###
dataset = deepcopy(data)
missing_cols = []
cols_to_impute = []
null_perc_dict = {}
# CACLULATE VALUES IMPUTATION #
for i in list(dataset):
    n_miss = dataset[i].isnull().sum()
    perc = round(n_miss / len(dataset) * 100, 3)
    null_perc_dict[i] = perc
    if perc > 0:
        cols_to_impute.append(i)
    if perc > 25:
        missing_cols.append(i)
    print(f"> {i}, Missing: {n_miss} ({perc}%)")

#dataset.drop(missing_cols, axis=1, inplace=True)
# MISSING VALUES IMPUTATION #
X_cols = [col for col in list(dataset) if col != 'Label' and col != 'DataUpadlosci' and col not in missing_cols]
y_col = 'Label'
X = dataset[X_cols]
y = dataset[y_col]
datestamps = dataset['DataUpadlosci']

cols_to_impute = [c for c in cols_to_impute if c not in missing_cols]
ready_cols = list(set(X_cols) - set(cols_to_impute))
X_inpute = X[cols_to_impute]

print('Missing values before imputation:', X_inpute.isnull().sum().sum())
imputer = KNNImputer(n_neighbors=3, weights='uniform')
imputer.fit(X_inpute)
print('Values imputed')
X_inputed = imputer.transform(X_inpute)
X_inputed_df = pd.DataFrame(X_inputed)
print('Missing values after imputation:', X_inputed_df.isnull().sum().sum())
X_inputed_df.columns = cols_to_impute
dataset_inputed = pd.concat([y, datestamps, X[ready_cols], X_inputed_df], axis=1)
dataset_inputed.to_csv(r'dataset_plot.csv', index=False)

### ONE-HOT ENCODING AND STANDARIZATION ###
dummy_cols = [
    'Voivodeship', 'LegalForm', 'EMISLegalForm', 'RodzajRejestru',
    'FormaWlasnosci', 'SpecialLegalForm', 'MainPKD', 'RyzykownaDziałalnoscGlowna',
    'RyzykowneDzialalnosciDodatkowe', 'NoWebsite', 'PublicMail', 'NoMail',
    'NoFax', 'AdresBiuroWirtualne', 'AdresLokal', 'CAACImport', 'CAACEksport',
    'EntityListedInVATRegistry', 'VirtualAccountsPresence', 'RiskyRemovalBasis',
    'PhoneNotPresent', 'MainNAICSCodes', 'DescriptionNull']

num_cols = [
    'Wiek', 'JednostkiLokalne', 'SecondaryPKDCount', 'ActiveLicenses', 'RevertedLicenses', 'ExpiredLicenses',
    'RemovalDaysAgo', 'DeclaredAccountsCount',  'RepresentationCount', 'NumberOfEmployees',
    'LatestMarketCapitalization', 'ExecutivesCount', 'OwnersCount', 'AffiliatesCount', 'ExternalIdsOthers',
    'RegisteredCapitalValue', 'AuditDaysAgo', 'PreviousNamesCount',
    'PreviousNameChangeYearsAgo', 'DividendSum', 'NetSalesRevenue',
    'OperatingProfitEBIT', 'EmployeeBenefitExpense', 'TotalAssets', 'NetProfitLossForThePeriod',
    'PropertyPlantAndEquipment', 'CashandCashEquivalents', 'TotalEquity', 'IssuedCapital',
    'WorkingCapital', 'RetainedEarnings', 'TotalLiabilities', 'CurrentLiabilities',
    'NonCurrentLiabilities', 'ProfitBeforeIncomeTax', 'IncomeTax', 'DepreciationImpairment',
    'DepreciationAmortization', 'CurrentAssets', 'ROE', 'ROA', 'ROS', 'A1', 'A2', 'A3', 'A4', 'A5',
    'P3', 'X8', 'X9', 'X10', 'X11', 'X13', 'X14', 'BruttoMargin'
    #,'P4', 'X6', 'RevenueToCash', 'RevenueToWages'
    ]

final_data_dummies = pd.get_dummies(dataset_inputed,
                                    columns=dummy_cols)

scaler = StandardScaler()
final_data_dummies[num_cols] = scaler.fit_transform(final_data_dummies[num_cols])
final_data_dummies_valid = final_data_dummies.dropna()


### CNN UNDERSAMPLING ###
X_cols = [col for col in list(final_data_dummies_valid) if col != 'Label']
y_col = 'Label'

X = final_data_dummies_valid[X_cols]
y = final_data_dummies_valid[y_col]

counter = Counter(y)
print(counter)

# undersample full data
#data_dat_under = pd.concat([X_dat_under, y_dat_under], axis=1)
#data_under.to_excel(r'dataset_fs_undersampled_no_vat.xlsx')

# define the undersampling method
undersample = RandomUnderSampler(sampling_strategy=0.56, random_state=100)
X_under, y_under = undersample.fit_resample(X, y)
data_under = pd.concat([X_under, y_under], axis=1)
data_under['Label'].value_counts(normalize=True)
data_under.to_excel(r'dataset_undersampled_inputed_no_vat.xlsx', index=False)
#undersample = CondensedNearestNeighbour(n_neighbors=1)
#Xu, yu = undersample.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(X_under, y_under,
                                                    test_size=0.2,
                                                    random_state=100,
                                                    stratify=y_under)

data_train = pd.concat([X_train, y_train], axis=1)
final_cols = [col for col in data_train if col not in [
    'EntityListedInVATRegistry', 'EntityListedInVATRegistry_NIE',
    'EntityListedInVATRegistry_TAK', 'RiskyRemovalBasis', 'RiskyRemovalBasis_BrakDanych',
    'RiskyRemovalBasis_LikelyFraudulent', 'RiskyRemovalBasis_NaturalReason',
    'RiskyRemovalBasis_NeverRemoved', 'RemovalDaysAgo', 'DividendCount',
    'SecondaryNAICSCount', 'MainNAICSCount', 'SegmentName_Other',
    'SegmentName_Not listed', 'MainProductsNull_NIE', 'MainProductsNull_TAK']]
data_train = data_train[final_cols]
data_train.to_csv(r'data_train_under_inputed.csv', index=False)

data_test = pd.concat([X_test, y_test], axis=1)[final_cols]
data_test.to_csv(r'data_test_under_inputed.csv', index=False)
