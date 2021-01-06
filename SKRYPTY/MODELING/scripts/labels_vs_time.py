import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_excel(r'data/processed/monitoring/cib_pc_20200713.xlsx', sheet_name='labels')
data['Label'] = np.where(data['Score'] < 100, 1, 0)
data = data.sort_values(by=['checklist_submission'], ascending=True)
data['week'] = (data['checklist_submission'] -
                data['checklist_submission'].dt.weekday * np.timedelta64(1, 'D')).dt.normalize()


data_grouped = data.groupby(['week', 'Label']).size().unstack(fill_value=0)
data_grouped.reset_index(inplace=True)
data_grouped.columns = ['week', '0', '1']
data_grouped['error_ratio'] = data_grouped['1'] / (data_grouped['0'] + data_grouped['1'])


#data_grouped.plot(x='week', y=['0', '1'], kind="bar")#, position=1)
#data_grouped.plot.line(x="week", y='error_ratio')#, position=0)
data_grouped.set_index('week', inplace=True)
data_grouped.index = data_grouped.index.strftime('%Y-%m-%d')


myFmt = mdates.DateFormatter('%d')
ax.xaxis.set_major_formatter(myFmt)

fig, ax = plt.subplots(figsize=(15, 10))
data_grouped['error_ratio'].plot(kind='line', marker='o', ax=ax)#, secondary_y=True)
data_grouped[['0', '1']].plot(kind='bar', color=['g', 'r'], ax=ax, secondary_y=True)
plt.axvline(56.6, 0, 1, linewidth=3, label='Start of monitoring stage', color='orange')
plt.xlabel('Week')
plt.ylabel('CasesCount')
ax.tick_params(axis ='x', rotation=80)
plt.xticks(rotation=80)
plt.show()



plt.figure()
N = 10
width = 0.35 # the width of the bars
ind = np.arange(N)
#plt.ylim(0.0, 65.0)
plt.bar(ind, data_grouped['0'], width, color='g', label='NoErrors')
plt.bar(ind+width, data_grouped['1'], width, color='r', label='Errors')
#plt.bar(ind, menMeans, width, color='r', yerr=menStd, label='Men means')
#plt.bar(ind+width, womenMeans, width, color='y', yerr=womenStd, label='Women means')


x = np.linspace(0, N)
y = np.sin(x)
axes2 = plt.twinx()
axes2.plot(x, y, color='k', label='Sine')
axes2.set_ylim(-1, 1)
axes2.set_ylabel('Line plot')

plt.show()