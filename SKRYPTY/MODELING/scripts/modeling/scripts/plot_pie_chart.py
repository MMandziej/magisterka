import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys

from copy import deepcopy

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

guids = [str(i) + '_' + j + '/' for i, j in category_mapping.items()]

## MODEL RESULTS ###
# create lists of all results files


nn_train = ['model_training/results/PC/nn/' + guid + 'nn_train_results.csv'
             for guid in guids]
nn_test = ['model_training/results/PC/nn/' + guid + 'nn_test_results.csv'
             for guid in guids]


# load csv files as data frames
nn_train_dfs = []
for file, guid in zip(nn_train, guids):
    df = add_labels_guid(file, guid[:-1])
    nn_train_dfs.append(df)

nn_test_dfs = []
for file, guid in zip(nn_test, guids):
    df = add_labels_guid(file, guid[:-1])
    nn_test_dfs.append(df)

#  merged all categories
nn_train_results = pd.concat(nn_train_dfs)
nn_test_results = pd.concat(nn_test_dfs)

# merge all data
full_data = pd.concat([nn_train_results, nn_test_results]).sort_values(by=['CategoryName', 'Score'],
                                                                       ascending=[True, False]).reset_index(drop=True)


red = [0.35, 0.24, 0.31, 0.13, 0.25, 0.15, 0.19, 0.13, 0.19, 0.29, 0.34, 0.29]
amber = [0.74, 0.55, 0.6, 0.87, 0.72, 0.65, 0.55, 0.28, 0.57, 0.69, 0.73, 0.76]

cats = []
for k, v in enumerate(list(category_mapping.values())):
    cats.append(str(k+1) + '_' + v)

# number_of_qc_cases = round(0.8 * len(scored_wf)) - 1
# cut_off = scored_wf.sort_values(by=['pqc'], ascending=False).iloc[number_of_qc_cases]['pqc']
cat_red_cut_offs = dict(zip(cats, red))
cat_amber_cut_offs = dict(zip(cats, amber))


amber_thresholds = {}
red_thresholds = {}
for cat, cut_off in cat_amber_cut_offs.items():
    temp_df = full_data[full_data['CategoryName'] == cat].sort_values(by=['Score'], ascending=False)
    temp_df = temp_df.reset_index(drop=True)[['Unique', 'Score', 'CategoryName']]

    no_amber_cases = round(cut_off * len(temp_df))
    amber_threshold = temp_df.iloc[no_amber_cases-1]['Score']
    amber_thresholds[cat] = amber_threshold

for cat, cut_off in cat_red_cut_offs.items():
    temp_df = full_data[full_data['CategoryName'] == cat].sort_values(by=['Score'], ascending=False)
    temp_df = temp_df.reset_index(drop=True)[['Unique', 'Score', 'CategoryName']]

    no_red_cases = round(cut_off * len(temp_df))
    red_threshold = temp_df.iloc[no_red_cases-1]['Score']
    red_thresholds[cat] = red_threshold


dfs = []
for cat in cats:
    red_ths = red_thresholds[cat]
    amber_ths = amber_thresholds[cat]

    temp_df = full_data[full_data['CategoryName'] == cat].sort_values(by=['Score'],
                                                                      ascending=False).reset_index(drop=True)[
        ['Unique', 'Score', 'CategoryName']]
    temp_df['RiskBasket'] = np.where(temp_df['Score'] >= amber_ths,
                                     'Orange',
                                     'Green')
    temp_df['RiskBasket'] = np.where(temp_df['Score'] >= red_ths,
                                     'Red',
                                     temp_df['RiskBasket'])

    if cat == '4_ESR':
        print(cat)
        temp_df['RiskBasket'].replace('Orange', 'Green', inplace=True)
        print(temp_df['RiskBasket'].value_counts())
    dfs.append(temp_df)


full_data_baskets = pd.concat(dfs).sort_values(by=['Unique', 'RiskBasket'], ascending=[True, False])
full_data_baskets = full_data_baskets.replace('Orange', 'Amber')
section_baskets = full_data_baskets[np.isin(full_data_baskets['CategoryName'], cats[:9])]
scales_baskets = full_data_baskets[np.isin(full_data_baskets['CategoryName'], cats[-3:])]

# dedup results
# full
full_data_baskets_dedup = full_data_baskets.drop_duplicates(subset='Unique',
                                                            keep='first',
                                                            ignore_index=True)

full_data_baskets_dedup['RiskBasket'].value_counts()

# sections
section_baskets_dedup = section_baskets.drop_duplicates(subset='Unique',
                                                        keep='first',
                                                        ignore_index=True)
sections_dist = section_baskets_dedup['RiskBasket'].value_counts()

# scales
scales_baskets_dedup = scales_baskets.drop_duplicates(subset='Unique',
                                                      keep='first',
                                                      ignore_index=True)
scales_dist = scales_baskets_dedup['RiskBasket'].value_counts()

### PLOT PIE CHARTS
plot = a.plot.pie(y='RiskBasket', autopct='%1.0f%%', figsize=(5, 5), colors=['red', 'orange', 'green'])
plot1 = sections_dist.plot.pie(y='RiskBasket', autopct='%1.0f%%', figsize=(5, 5), colors=['red', 'orange', 'green'])


a = full_data_baskets[['Unique', 'CategoryName', 'RiskBasket']].pivot(
    index='Unique',
    columns='CategoryName',
    values='RiskBasket').reset_index()

a.to_excel(r'model_training\results\heatmap_baskets.xlsx')

heatmap_data = deepcopy(a)
heatmap_data = heatmap_data.replace('Red', 1).replace('Amber', 0.5).replace('Green', 0)
del heatmap_data['Unique']

fig, ax = plt.subplots(figsize=(12, 7))
ttl = ax.title
ttl.set_position([0.5, 1.05])

plt.title('Error scales - heatmap', fontsize=18)
chart = sns.heatmap(heatmap_data[cats[-3:]], cmap='RdYlGn_r') # Reds
#plt.gca().axes.get_xaxis().set_visible(False)
plt.gca().axes.get_yaxis().set_visible(False)
chart.set_xticklabels(['Critical', 'Major', 'Minor'])
#chart.set_xticklabels(['Documentation', 'Risk factors', 'Screening', 'ESR',
#                       'CO', 'Relationship', 'ODD', 'FATCA/CRS', 'Control'])
plt.show()
