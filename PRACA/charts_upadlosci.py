import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
sns.set_style("whitegrid", {"xtick.major.size": 8, "ytick.major.size": 8})

data = pd.read_excel(r'C:\Users\marcinmandziej\Desktop\Faktury\MGR\charts.xlsx')

data_plot = data.melt(id_vars='Rok').rename(columns={'variable': 'Legenda',
                                                     'value': 'Liczba firm'})

ax = sns.barplot(x="Rok", y="Liczba firm", hue='Legenda', data=data_plot)
ax.set_xlabel('')
ax.set_ylabel('')
