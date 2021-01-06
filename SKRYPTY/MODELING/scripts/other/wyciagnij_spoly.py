#import datetime as d
#import csv
import os
import json
import pandas as pd
import shutil
#import time as t

"""
from emis import flatten_json, parse_employees, parse_field, parse_naics,\
                 cols_drop, employees_cols_drop, cols_to_drop_list, output_rename,\
                 known_cols, len_guids, cols_guids_to_drop
"""

################## USER PART ##################
######## DEFINE INPUT NAD OUTPUT PATHS ########
PATH_TO_JSONS = r'C:/Users/mmandziej001/Desktop\Projects/FAIT/Prediction Module/POLAND_DANE/WHITELISTA/CLOSED & LIQUIDATED/'
XLXS_OUTPUT_PATH = r'C:/Users/mmandziej001/Desktop/Projects/VATCHECK/OUTPUT_API/OUT/'
############# END OF USER PART ################

def collect_jsons(jsons_path: str) -> list:
    nips_jsons = {}
    nips_errors = {}
    nips = [file[9:15] for file in os.listdir(jsons_path) if
            file.endswith('.json') and "INVALID" not in file]
    jsons_valid = [file for file in os.listdir(jsons_path) if
                   file.endswith('.json') and "INVALID" not in file]
    count = 0
    for nip, file in zip(nips, jsons_valid):
        with open(os.path.join(PATH_TO_JSONS, file), encoding="utf8") as json_file:
            try:
                json_text = json.load(json_file)
                nips_jsons[nip] = json_text
            except:
                nips_errors[nip] = file
        count += 1
        print('Loaded ', str(count), 'out of ', len(nips))
    return nips_jsons, nips_errors

############### GET OUTPUT ##################
jsons_loaded, jsons_invalid = collect_jsons(PATH_TO_JSONS)

data = jsons_loaded['download.j']['data']['resultList']
data1 = jsons_loaded['downloa1.j']['data']['resultList']
data2 = jsons_loaded['downloa2.j']['data']['resultList']
data3 = jsons_loaded['downloa3.j']['data']['resultList']
data4 = jsons_loaded['downloa4.j']['data']['resultList']
data5 = jsons_loaded['downloa5.j']['data']['resultList'] 
data6 = jsons_loaded['downloa6.j']['data']['resultList'] #45+
dataL = jsons_loaded['downloaL.j']['data']['resultList']
dataI = jsons_loaded['downloaI.j']['data']['resultList']


isics = []
for i in dataL:
    isics.append(i['isic'])
nips_isics = dict((str(idx+1), str(v)) for (idx, v) in enumerate(isics))

d = dict((i,j) for i,j in enum)
jsons_trunc = {}
for key, val in jsons_loaded.items():
    jsons_trunc[key] = val['data']


jsons_2018 = jsons_trunc['EMIS_2018.']['resultList']
jsons_2019 = jsons_trunc['EMIS_2019.']['resultList']


nips_jsons_loaded = {}
path_to_json = r'C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\JSONS\MERGED_JSONS'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json') and
              'INVALID' not in pos_json]
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        print(index, ' out of ', len(json_files))
        try:
            nips_jsons_loaded[index] = json.load(json_file)
        except:
            print(js + ' invalid file')

isic_nip = {}
isic_krs = {}
isic_regon = {}
for k, v in nips_jsons_loaded.items(): #nips_jsons
    for j in v['externalIdList']:
        if j['classCode'] == 'PL-FISCAL':
            isic_nip[v['isic']] = j['externalId']
        elif j['classCode'] == 'PL-KRS':
            isic_krs[v['isic']] = j['externalId']
        elif j['classCode'] == 'PL-REGON':
            isic_regon[v['isic']] = j['externalId']

df = pd.DataFrame(
    {'ISIC': list(isic_nip.keys()),
     'NIP': list(isic_nip.values())})

df1 = pd.DataFrame(
    {'ISIC': list(isic_krs.keys()),
     'KRS': list(isic_krs.values())})

df2 = pd.DataFrame(
    {'ISIC': list(isic_regon.keys()),
     'REGON': list(isic_regon.values())})

merged_df = df.merge(df1, on='ISIC', how='outer')
merged_df = merged_df.merge(df2, on='ISIC', how='outer')
merged_df.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Investigated\Investigated_all.xlsx')

nips_isics = {}
nips_errors = {}
for i in list(isic_krs)[11999:]:
    nips_isics[isic_krs[i]] = str(i)

### MERGE ADV SCREENER FILES ###
d1 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L1.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d2 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L2.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d3 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L3.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d4 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L4.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d5 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L5.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d6 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L6.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d7 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L7.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d8 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L8.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d9 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L9.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
d10 = pd.read_excel(r"C:\Users\mmandziej001\Desktop\L10.xlsx")[['NIP', 'REGON', 'KRS', 'Fiscal Year']]
data = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10])

data.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\FINANCE\liquidated_adv_screener.xlsx')
