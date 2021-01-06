import numpy as np
import pandas as pd
import seaborn as sns

development_data = pd.read_excel(r"data\processed\incremented\cib_pc_15052020.xlsx")
monitoring_data = pd.read_excel(r"data\processed\monitoring\cib_pc_20200713_nojune.xlsx")
development_data['Label'] = np.where(development_data['Score'] < 100, 1, 0)
monitoring_data['Label'] = np.where(monitoring_data['Score'] < 100, 1, 0)

common_cols = [col for col in list(monitoring_data) if col in list(development_data)]
hist_cols = ['Entity', 'DDLevel', 'High_Value_Client']
numeric_cols = ['analyst_cases_processed_all', 'analyst_cases_processed_30days',
                'analyst_cases_processed_90days', 'analyst_cases_average_score_all',
                'analyst_cases_average_score_30days', 'analyst_cases_average_score_90days',
                'analyst_expierence_day']

fig, ax = plt.subplots(figsize=(15, 10))
development_data['analyst_cases_processed_all'].plot(kind='line', marker='o', ax=ax)#, secondary_y=True)
monitoring_data['analyst_cases_processed_all'].plot(kind='line', marker='o', ax=ax)#, secondary_y=True)

#plt.xlabel('Week')
#plt.ylabel('CasesCount')
#ax.tick_params(axis ='x', rotation=80)
#plt.xticks(rotation=80)
plt.show()

fig, ax = plt.subplots(figsize=(15, 10))
sns.distplot(monitoring_data['analyst_expierence_day'], label='Monitoring data', hist=True)
sns.distplot(development_data['analyst_expierence_day'], label='Development data', hist=True)
ax.set_xlim(-1, 550)
plt.legend()
plt.show()

fig, ax = plt.subplots(figsize=(15, 10))
sns.barplot(x = 'Entity', data = monitoring_data, kind = 'bar')
#sns.barplot(development_data['Entity'], label='Development data', hist=True)
#ax.set_xlim(-1, 35)
plt.legend()
plt.show()

fig, ax = plt.subplots(figsize=(13, 13))
sns.catplot(x='DDLevel', data=monitoring_data, col='Label', kind='count')
#sns.catplot(x='DDLevel', data=development_data, col="Label", kind="count")
plt.legend()
plt.show()