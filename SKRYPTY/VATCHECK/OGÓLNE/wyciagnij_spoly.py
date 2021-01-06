#import datetime as d
#import csv
import os
import json
import pandas as pd
#import time as t

"""
from emis import flatten_json, parse_employees, parse_field, parse_naics,\
                 cols_drop, employees_cols_drop, cols_to_drop_list, output_rename,\
                 known_cols, len_guids, cols_guids_to_drop
"""

################## USER PART ##################
######## DEFINE INPUT NAD OUTPUT PATHS ########
PATH_TO_JSONS = r'C:/Users/mmandziej001/Desktop/'
XLXS_OUTPUT_PATH = r'C:/Users/mmandziej001/Desktop/'
############# END OF USER PART ################

def collect_jsons(jsons_path: str) -> list:
    nips_jsons = {}
    nips_errors = {}
    nips = [file[:10] for file in os.listdir(jsons_path) if
            file.endswith('.json') and "INVALID" not in file]
    jsons_valid = [file for file in os.listdir(jsons_path) if
                   file.endswith('.json') and "INVALID" not in file]

    for nip, file in zip(nips, jsons_valid):
        with open(os.path.join(PATH_TO_JSONS, file), encoding="utf8") as json_file:
            try:
                json_text = json.load(json_file)
                nips_jsons[nip] = json_text
            except:
                nips_errors[nip] = file
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
path_to_json = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Closed\ALL55K'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json') and
              'INVALID' not in pos_json]
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        print(index)
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
merged_df.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Closed\closed_all.xlsx')

nips_isics = {}
nips_errors = {}
for i in list(isic_krs)[11999:]:
    nips_isics[isic_krs[i]] = str(i)


"""
isic_status = {}

closed = jsons_trunc['download_C']
for i in closed['resultList']:
    isic_status[i['isic']] = 'Closed'
        
liquidated = jsons_trunc['Liquidated']
for i in liquidated['resultList']:
    isic_status[i['isic']] = 'Liquidated'
    
investigated = jsons_trunc['Investigat']
for i in investigated['resultList']:
    isic_status[i['isic']] = 'Investigated'
    
operational1 = jsons_trunc['download_O']
for i in operational1['resultList']:
    isic_status[i['isic']] = 'Operational'
    
operational2 = jsons_trunc['download_X']
for i in operational2['resultList']:
    isic_status[i['isic']] = 'Operational'
    
df = pd.DataFrame.from_dict(isic_status, orient='index')
df.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\EMIS\Poland\Poland_Full.xlsx')

isic_nip = {}
isic_krs = {}
isic_regon = {}
for i in investigated['resultList']:
    for j in i['externalIdList']:
        if j['classCode'] == 'PL-FISCAL':
            isic_nip[i['isic']] = j['externalId']
        elif j['classCode'] == 'PL-KRS':
            isic_krs[i['isic']] = j['externalId']
        elif j['classCode'] == 'PL-REGON':
            isic_regon[i['isic']] = j['externalId']

df_nip = pd.DataFrame.from_dict(isic_nip, orient='index')
df_krs = pd.DataFrame.from_dict(isic_krs, orient='index')
df_regon = pd.DataFrame.from_dict(isic_regon, orient='index')

df_nip.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\Kamil\ISIC_NIP.xlsx')
df_krs.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\Kamil\ISIC_KRS.xlsx')
df_regon.to_excel(r'C:\Users\mmandziej001\Desktop\Projects\Kamil\ISIC_REGON.xlsx')

    
    

