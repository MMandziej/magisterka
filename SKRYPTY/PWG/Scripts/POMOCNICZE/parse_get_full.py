import datetime
import json
import os 
import pandas as pd
from pandas.io.json import json_normalize
import time as t

t = t.time()

######### DEFINE INPUT NAD OUTPUT PATHS ##########
INPUT = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\GET_FULL\\'
database_name = 'MMandziej'
table_name = 'PWG_getFull'

############ COLLECT JSONS  ###################### 

def collect_json_names():
    files = os.listdir(INPUT)
    json_names= []
    [json_names.append(i) for i in files if i[-4:] == 'json']
    return(json_names)

collect = collect_json_names()

def load_json(json_names):
    valid_files = []
    invalid_files = []
    valid_nips = []
    invalid_nips = []
    for file in json_names:
        try:
            with open(INPUT + '\\' + file, encoding="utf8") as f:
                data = json.load(f)
                
                if len(data['result']['data']) != 0:
                    company_info = data['result']['data']
                    nip = data['result']['data']['nip']
                    valid_files.append(company_info)
                    valid_nips.append(nip)
                else:
                    invalid_files.append(file + ' - empty')
                    invalid_nips.append(nip)            
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            invalid_nips.append(file[0:10])
            invalid_files.append(file + ' - faulty')
                 
    valid_jsons = [valid_nips, valid_files]
    invalid_jsons = [invalid_nips, invalid_files]
    return valid_jsons, invalid_jsons

load = load_json(collect_json_names())

############# PARSING JSONS TO DF ##############

def create_df(valid_json):
    dfs = []
    for i in valid_json:
        (keys,values) = zip(*i.items())
        keys = pd.Series(keys)
        values = pd.Series(values,index=keys)
        dfs.append(values)
    df = pd.DataFrame(dfs, columns=keys)
    return df

spolki = create_df(load_json(collect_json_names())[0][1])

##################################################

def create_outer_table(df, table):
    temp = []
    nip = []
    for row in range(0, len(df[table])):
        try:
            temp.append(json_normalize(df.loc[row, table]))
            nip.append(df.loc[row, 'nip'])
        except:
            pass
        
    for i in range(0, len(temp)):
        temp[i]['nip'] = nip[i]
        
    temp = pd.concat(temp, sort=True)
    temp.reset_index(drop=True ,inplace=True)
    return temp

##################################################

def create_aktywnosc(df, table):
    temp = []
    nip = []
    for row in range(0, len(df[table])):
        try:
            temp.append(json_normalize(df.loc[row, table]))
            nip.append(df.loc[row, 'nip'])
        except:
            pass
    
    for i in range(0, len(temp)):
        temp[i].rename(columns = {'nip': 'nip_entity'}, inplace=True)
        temp[i]['nip'] = ''
        temp[i]['nip'] = nip[i]
        
    temp = pd.concat(temp, sort=True)
    temp.reset_index(drop=True ,inplace=True)
    return temp

##################################################
    
def create_zaleglosci(df, table):
    temp = []
    nip = []
    for row in range(0, len(df[table])):
        try:
            temp.append(json_normalize(df.loc[row, table]))
            nip.append(df.loc[row, 'nip'])
        except:
            pass
    
    for i in range(0, len(temp)):
        temp[i]['nip'] = nip[i]
        
    temp = pd.concat(temp, sort=True)
    temp.reset_index(drop=True ,inplace=True)
    return temp

################# GET TABLES ################

aktywnosc = create_aktywnosc(create_df(load_json(collect_json_names())[0][1]), 'aktywnosc')
zaleglosci = create_zaleglosci(create_df(load_json(collect_json_names())[0]), 'zaleglosci')

zalezne = create_outer_table(create_df(load_json(collect_json_names())[0][1]), 'zalezne')
rola = create_outer_table(create_df(load_json(collect_json_names())[0][1]), 'roles')
rola_h = create_outer_table(create_df(load_json(collect_json_names())[0][1]), 'roleshistory')
uokik = create_outer_table(create_df(load_json(collect_json_names())[0][1]), 'uokik')


rola.drop(['pstan'], axis=1, inplace=True) #######
rola_h.drop(['pstan'], axis=1, inplace=True) #######



test = spolki['zaleglosci']
asd = json_normalize(test)
hui = test.to_dict()[0]
lista = []
for i in hui:
    lista.append(i)

