import numpy as np
import pandas as pd
import pyodbc

from copy import deepcopy
from datetime import date, datetime
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model

file_path = r'data/scoring_input/scoring_input_' + str(date.today()) + '.csv'
final_wf_dr = pd.read_csv(file_path, encoding="utf-8")
final_wf_dr = pd.read_excel(r'data/scoring_input/scoring_input_09062020.xlsx',
                            encoding="utf-8")

### Preparing dataset for sending to model ###
feature_cols = [
    'ScreenedParties', 'OwnershipLayers', 'Experience_proj', 'Experience_team',
    'Hour_numeric', 'Group_cases', 'NO_errors_last_5_days_DR',
    'NO_cases_last_5_days_DR', 'NO_errors_last_month_DR', 'NO_cases_month_DR',
    'PartyType', 'TLAssignedName', 'CDDRiskLevel', 'ProcessingUnit', 'ESR',
    'CRS', 'FATCA', 'GreenlightedDR', 'Day', 'Population_match']
final_wf_dr_score = final_wf_dr[feature_cols]

final_wf_dr_score.rename(columns={'NO_errors_last_5_days_DR': 'NO_errors_last_5_days',
                                  'NO_cases_last_5_days_DR': 'NO_cases_last_5_days',
                                  'NO_errors_last_month_DR': 'NO_errors_last_month',
                                  'NO_cases_month_DR': 'NO_cases_month',
                                  'TLAssignedName': 'TLAssigned'},
                         inplace=True)

# Fixing TL Assigned column
final_wf_dr_score.TLAssigned = final_wf_dr_score.TLAssigned.str.split(',').str[0]

# Selecting columns to be converted into dummy variables
dummy_cols = [
    'TLAssigned', 'PartyType', 'CDDRiskLevel', 'ProcessingUnit',
    'ESR', 'CRS', 'FATCA', 'GreenlightedDR', 'Day', 'Population_match']
final_wf_dr_dummies = pd.get_dummies(final_wf_dr_score,
                                     columns=dummy_cols)

# Generating empty train df
train = pd.DataFrame(columns=[
    'ScreenedParties', 'OwnershipLayers', 'Experience_proj', 'Experience_team',
    'Hour_numeric', 'Group_cases', 'NO_errors_last_5_days',
    'NO_cases_last_5_days', 'NO_errors_last_month', 'NO_cases_month',
    'PartyType_Subsidiary', 'TLAssigned_Makowska', 'TLAssigned_Kolodziejczyk',
    'TLAssigned_Jaszewski', 'TLAssigned_Michalik', 'TLAssigned_Armannsson',
    'TLAssigned_Rybka', 'TLAssigned_Galtie', 'TLAssigned_Skrzynecki',
    'TLAssigned_Holowacz', 'TLAssigned_Gronowski', 'CDDRiskLevel_Normal',
    'CDDRiskLevel_Low', 'CDDRiskLevel_Increased', 'ProcessingUnit_Gdansk',
    'ProcessingUnit_MidCorp', 'ProcessingUnit_DIBA', 'ProcessingUnit_Rotterdam',
    'ProcessingUnit_Not_assigned', 'ProcessingUnit_Midcorp',
    'ESR_No_ESR_needed', 'ESR_ESR_linked', 'CRS_FALSE', 'FATCA_FALSE',
    'GreenlightedDR_FALSE', 'Day_Wednesday', 'Day_Friday', 'Day_Tuesday',
    'Day_Monday', 'Population_match_FALSE'])

# Finding misssing cols on datasets to be scored
missing_cols = set(train.columns) - set(final_wf_dr_dummies.columns)

# Adding zero to missing cols
for c in missing_cols:
    final_wf_dr_dummies[c] = 0

final_wf_dr_dummies_2 = final_wf_dr_dummies[train.columns]
# Fill NA cols with zero
final_wf_dr_dummies_2 = final_wf_dr_dummies_2.fillna(0)
# Define numeric cols
num_cols = [
    'ScreenedParties', 'OwnershipLayers', 'Experience_proj', 'Experience_team',
    'Hour_numeric', 'Group_cases', 'NO_errors_last_5_days',
    'NO_cases_last_5_days', 'NO_errors_last_month', 'NO_cases_month']

# Normalizing cols
scaler = StandardScaler()
final_wf_dr_dummies_2[num_cols] = scaler.fit_transform(final_wf_dr_dummies_2[num_cols])

# load the best model from h5 file
model = load_model("final_model_DR.h5")
model.summary()

### Running model for prediction ###
# calculate cut off for 80% cases selected on development dataset
# development_data = pd.read_csv(r"data/archive/developement_dataset.csv")
# cut_of_08 = development_data['scored_df.pqc'].quantile(1-0.8)

ynew = model.predict_proba(final_wf_dr_dummies_2)
pqc = pd.DataFrame(ynew, columns=['pqc'])
scored_wf = pd.concat([final_wf_dr, pqc], axis=1)
scored_wf['pqc'] = round(scored_wf['pqc'], 6)
number_of_qc_cases = round(0.8 * len(scored_wf)) - 1
cut_off = scored_wf.sort_values(by=['pqc'], ascending=False).iloc[number_of_qc_cases]['pqc']
scored_wf['pqc_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
scored_wf['Should_be_send_to_QC'] = np.where(scored_wf['pqc'] >= cut_off, 1, 0)
#scored_wf['Should_be_send_to_QC'] = [1 if pqc >= scored_wf['pqc'].quantile(0.2) else 0 for pqc in scored_wf['pqc']]

str_cols = [
    'GRID', 'ProcessingUnit', 'AnalystAssignedName', 'QCAssignedName',
    'TLAssignedName', 'CDDStatus', 'CDDRiskLevel', 'ESR', 'FirstAnalystDR',
    'FirstAnalystPC', 'FirstSignatoryDR', 'FirstSignatoryPC',
    'LegalUltimateParentGRID', 'EconomicUltimateParentGRID', 'PartyType',
    'WPI', 'HT_TL', 'Hour', 'Day', 'PSStatus']

int_cols = [
    'PriorityScore', 'MLROEffortAnalystCount', 'MLROEffortSignatoryCount',
    'COEffortSignatoryCount', 'COEffortAnalystCount', 'ScreenedParties',
    'OwnershipLayers', 'DRReworkCount', 'DRReworkCompletedCount',
    'PCReworkCount', 'PCReworkCompletedCount', 'COEffortReworkCount',
    'COEffortReworkCompletedCount', 'FrontPagerCount',
    'FrontPagerSignatoryCount', 'ScreenedPartiesDR', 'OwnershipLayersDR',
    'Label', 'DateJoiningTeam', 'Population_match', 'NO_errors_last_5_days_DR',
    'NO_cases_last_5_days_DR', 'NO_errors_last_month_DR', 'NO_cases_month_DR',
    'DateJoiningProject', 'Group_cases', 'Hour_numeric', 'Experience_team',
    'Experience_proj', 'Should_be_send_to_QC']

bool_cols = ['FATCA', 'CRS', 'MLRORequest', 'GreenlightedDR', 'GreenlightedCO']

date_cols = ['DRSentToQCDate_match', 'check_date']

datetime_cols = [
    'BackupTime', 'CDDStatusChangeDate', 'Created', 'DRSentToQCDate',
    'PCSenttoQCDate', 'DRCompletedDate', 'PCCompletedDate', 'PCHandoverDate',
    'pqc_timestamp']


scored_wf[str_cols] = scored_wf[str_cols].astype(str)
scored_wf.loc[:, str_cols] = scored_wf.loc[:, str_cols].replace('nan', '')

scored_wf[int_cols] = scored_wf[int_cols].apply(pd.to_numeric,
                                                errors='ignore',
                                                downcast='integer')

scored_wf['pqc'] = pd.to_numeric(scored_wf['pqc'], downcast='float')

scored_wf[date_cols] = scored_wf[date_cols].apply(pd.to_datetime,
                                                  errors='coerce',
                                                  format='%Y-%m-%d')

scored_wf[datetime_cols] = scored_wf[datetime_cols].apply(pd.to_datetime,
                                                          errors='coerce',
                                                          format='%Y-%m-%d %H:%M:%S')
scored_wf = scored_wf.fillna('')

# reorder data
reoder_cols = [
    'BackupTime', 'GRID', 'ProcessingUnit', 'PriorityScore', 'AnalystAssignedName',
    'QCAssignedName', 'TLAssignedName', 'CDDStatus', 'CDDStatusChangeDate',
    'Created', 'DRSentToQCDate', 'PCSenttoQCDate', 'DRCompletedDate',
    'PCCompletedDate', 'PCHandoverDate', 'CDDRiskLevel', 'FATCA', 'CRS', 'ESR',
    'MLROEffortAnalystCount', 'MLROEffortSignatoryCount', 'MLRORequest',
    'COEffortSignatoryCount', 'COEffortAnalystCount', 'ScreenedParties',
    'OwnershipLayers', 'DRReworkCount', 'DRReworkCompletedCount',
    'PCReworkCount', 'PCReworkCompletedCount', 'COEffortReworkCount',
    'COEffortReworkCompletedCount', 'FrontPagerCount', 'FrontPagerSignatoryCount',
    'FirstAnalystDR', 'FirstAnalystPC', 'FirstSignatoryDR', 'FirstSignatoryPC',
    'GreenlightedDR', 'GreenlightedCO', 'ScreenedPartiesDR', 'OwnershipLayersDR',
    'LegalUltimateParentGRID', 'EconomicUltimateParentGRID', 'PartyType',
    'WPI', 'DRSentToQCDate_match', 'Label', 'DateJoiningTeam', 'Population_match',
    'NO_errors_last_5_days_DR', 'NO_cases_last_5_days_DR', 'NO_errors_last_month_DR',
    'NO_cases_month_DR', 'HT_TL', 'DateJoiningProject', 'Group_cases', 'Hour',
    'Hour_numeric', 'Day', 'Experience_team', 'check_date', 'Experience_proj',
    'pqc', 'pqc_timestamp', 'Should_be_send_to_QC', 'PSStatus']

scored_wf = scored_wf[reoder_cols]

# export full data to excel files
scored_wf.to_excel('data/scoring_output/scored_' + str(date.today()) + '.xlsx',
                   sheet_name=str(date.today()),
                   index=False)

# Create report for MI team and export
result_df = scored_wf[['GRID', 'pqc', 'Should_be_send_to_QC',
                       'AnalystAssignedName', 'QCAssignedName',
                       'TLAssignedName', 'pqc_timestamp']]

result_df.rename(columns={'pqc': 'Score',
                          'pqc_timestamp': 'ScoreTimestamp',
                          'TLAssigned': 'TLAssignedName'},
                 inplace=True)

result_df.to_excel('data/scoring_output/mi_reports/Predictive_qc_results_' +
                   str(date.today()) + '.xlsx', index=False)


# connect with DB

server = 'localhost\SQLEXPRESS01'
database = 'pred_qc_lion_king'

reports_temp_table = '[dbo].[reports_backlog_temp]'
reports_final_table = '[dbo].[reports_backlog]'

cases_temp_table = '[dbo].[scored_cases_backlog_temp]'
cases_final_table = '[dbo].[scored_cases_backlog]'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                       SERVER=' + server + '; \
                       DATABASE=' + database + ';\
                       Trusted_Connection=yes;')
cursor = cnxn.cursor()

data_backlog = pd.read_sql("SELECT * FROM" + reports_final_table, cnxn)
cols = list(data_backlog)

insert_values_list = []
for num, a in result_df.iterrows():
    single_insert_list = [x for x in result_df.loc[num]]
    list_to_str = "', '".join(str(elem) for elem in single_insert_list)
    single_values = "('{}')".format(list_to_str)
    single_values = single_values.replace(", 'nan'", ", NULL")
    insert_values_list.append(single_values)

insert_values = ", \n".join(str(val) for val in insert_values_list)
all_cols = ", ".join('[' + str(header) + ']' for header in cols)
insert_statement = "INSERT INTO {} ({}) VALUES {}".format(reports_final_table,
                                                          all_cols,
                                                          insert_values)

try:
    cursor.execute(insert_statement)
    print("Data sucessfully exported into %s ." % reports_final_table)
except pyodbc.ProgrammingError:
    print("Could not insert values into {} table." % reports_final_table)

#### 
def export_data_to_db(server: str,
                      database: str,
                      table_to_append: pd.DataFrame,
                      temp_table_name: str,
                      final_table_name: str):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                       SERVER=' + server + '; \
                       DATABASE=' + database + ';\
                       Trusted_Connection=yes;')

    cursor = cnxn.cursor()
    # read data from sql table
    data_backlog = pd.read_sql("SELECT * FROM" + final_table_name, cnxn)
    cols = list(data_backlog)
    if final_table_name == '[dbo].[reports_backlog]':
        dedup_cols = deepcopy(cols)
        dedup_cols.remove('ScoreTimestamp')
    elif final_table_name == '[dbo].[scored_cases_backlog]':
        dedup_cols = deepcopy(cols)
        dedup_cols.remove('pqc_timestamp')
    else:
        dedup_cols = cols

    data_all = pd.concat([data_backlog, table_to_append], ignore_index=True)
    data_dedup = data_all.drop_duplicates(subset=dedup_cols,
                                          keep='last',
                                          ignore_index=True)

    insert_values_list = []
    for num, a in data_dedup.iterrows():
        single_insert_list = [x for x in data_dedup.loc[num]]
        list_to_str = "', '".join(str(elem) for elem in single_insert_list)
        single_values = "('{}')".format(list_to_str)
        single_values = single_values.replace(", 'nan'", ", NULL")
        insert_values_list.append(single_values)

    insert_values = ", \n".join(str(val) for val in insert_values_list)
    all_cols = ", ".join('[' + str(header) + ']' for header in cols)
    insert_statement = "INSERT INTO {} ({}) VALUES {}".format(temp_table_name,
                                                              all_cols,
                                                              insert_values)
    try:
        cursor.execute(insert_statement)
        print("Data sucessfully exported into %s ." % temp_table_name)

    except pyodbc.ProgrammingError:
        print("Could not insert values into {} table." % temp_table_name)

    insert_temp_to_final = "INSERT INTO {} \
                SELECT * FROM {} t \
                WHERE NOT EXISTS \
                    (SELECT 1 FROM {} f \
                     WHERE t.GRID = f.GRID AND t.Score = f.Score)".format(
                        final_table_name,
                        temp_table_name,
                        final_table_name)

    try:
        cursor.execute(insert_temp_to_final)
        print("Data sucessfully exported into %s ." % final_table_name)
    except pyodbc.ProgrammingError:
        print("Could not insert values into %s table." % final_table_name)
    cursor.commit()
    cursor.close()
    cnxn.close()
    return data_dedup


reports_exported = export_data_to_db(server,
                                     database,
                                     result_df,
                                     reports_temp_table,
                                     reports_final_table)

cases_exported = export_data_to_db(server,
                                   database,
                                   scored_wf,
                                   cases_temp_table,
                                   cases_final_table)
