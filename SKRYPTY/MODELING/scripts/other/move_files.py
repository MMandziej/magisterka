
data_all = pd.read_excel(r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\Closed_all.xlsx",
                         converters={'NIP': str})[['NIP']]
data_vat = pd.read_excel(r"C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\OUT\CLOSED_INVESTIGATED_2020-07-31.xlsx",
                         converters={'NIP': str})[['NIP']]

data_all = data_all[~pd.isnull(data_all['NIP'])]

#data_all['NIP'] = data_all['NIP'].astype(int).astype(str)
nips_all = list(data_all['NIP'])
nips_vat = list(data_vat['NIP'])

nips_missing = list(set(nips_all) - set(nips_vat))


import os
import shutil
shutil.move(r'C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\JSONS',
            r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\WHITELISTA\OPERATIONAL_SINGLE')

source = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\JSONS_FINANCE\\'
dest1 = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\FINANCE\Operational\ALL\\'

files = os.listdir(source)

for f in files:
    try:
        shutil.move(source+f, dest1)
    except:
        pass