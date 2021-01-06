import pandas as pd
import pyodbc
import seaborn as sns

from datetime import datetime, timedelta

server = 'localhost\SQLEXPRESS01'
database = 'pred_qc_lion_king'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                       SERVER=' + 'localhost\SQLEXPRESS01' + '; \
                       DATABASE=' + database + ';\
                       Trusted_Connection=yes;')
cursor = cnxn.cursor()

data = pd.read_sql('SELECT * FROM [monitoring].[monitoring_production_dataset]', cnxn).sort_values(by='pqc_timestamp')
cols = ['GRID', 'Experience_proj', 'Experience_team', 'Population_match', 'pqc_timestamp']
data = data[cols]

data['Week'] = data['pqc_timestamp'] - data['pqc_timestamp'].dt.weekday.astype('timedelta64[D]')
data['Week'] = data['Week'].dt.date

a = data.groupby(by='Week').agg({'GRID': 'count', 'Population_match': 'sum'})
a['MismatchPerc'] = (a['GRID'] - a['Population_match']) / a['GRID']

a = a.reset_index()

plt.bar(a['Week'],
        a['MismatchPerc'])
plt.show()

###
train = pd.read_csv(r"C:\Users\mmandziej001\Desktop\FCU\SCRIPTS\predictive_qc_lion_king\model_training\data\DR\dataset_dummy_grouped_time_train_nominor.csv")
test = pd.read_csv(r"C:\Users\mmandziej001\Desktop\FCU\SCRIPTS\predictive_qc_lion_king\model_training\data\DR\dataset_dummy_grouped_time_test_nominor.csv")

full = pd.concat([train, test])

plot_data =  pd.read_excel(r"model_training\results\DR\nn\nn_check_results_nominor.xlsx")[
    ['Unique', 'Major_last_10_checklistsDR', 'Score', 'Label']]

ax = sns.scatterplot(x='Major_last_10_checklistsDR',
                     y='Score',
                     data=plot_data)

ax = sns.lineplot(x='Major_last_10_checklistsDR',
                     y='Score',
                     data=plot_data)