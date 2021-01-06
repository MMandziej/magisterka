#!/usr/bin/env python
# coding: utf-8

# ## <font color='DEEPPINK'> Set path for input JSON files, path for XLSX output and name for XLSX output </font>

# Set output type:  
# For Person (PESEL): 1  
# For Company (NIP): 2  
# For Person&Company (PESEL & NIP): 3  

# In[24]:


JSON_DIR = r'C:\Users\mmandziej001\Desktop\JSONs'


# In[25]:


OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\JSONs\OUTPUT\\'


# In[26]:


OUTPUT_NAME = 'output_i2'


# In[27]:


OUTPUT_TYPE = 2


# ## <font color='DEEPPINK'> Select output columns and set order </font>

# ### <font color='DEEPPINK'> PERSON </font>

# In[28]:


columns_order_1 = ['name', 'surname', 'wiek', 'person_id', 'nazwa', 'adres', 'lokal', 'numer', 'poczta', 
       'kod_pocztowy',  'miasto', 'kapital',  'nip', 'krs', 'regon', 
        'company_id', 'rola', 'start', 'koniec']


# ### <font color='DEEPPINK'> COMPANY </font>

# In[29]:


columns_order_2 = [ 'id', 'ilosc', 'wartosc','kapital',  
                   'nazwa','krs', 'regon', 'nazwa_main','nip', 'rola_2', 'start_2', 'koniec_2']


# ### <font color='DEEPPINK'> PERSON & COMPANY </font>

# In[30]:


columns_order_3 = ['id', 'ilosc', 'kapital', 'wartosc', 'nazwa', 'regon', 'krs', 'rola_2', 'start_2', 'koniec_2', 
                  'company_id', 'person_id','name', 'surname', 'pesel', 'wiek', 'adres', 'miasto','numer', 'lokal', 'poczta', 'kod_pocztowy',
                  'rola', 'start', 'koniec', 'nazwa_main', 'nip']


# ## <font color='LIGHTSEAGREEN'> Import libraries </font>

# In[31]:


import os
import json
import pandas as pd
from pandas.io.json import json_normalize


# ## <font color='LIGHTSEAGREEN'> Define functions </font>

# In[32]:


def collect_json_names():
    files = os.listdir(JSON_DIR)
    json_names = []
    invalid_files_list = []
    [json_names.append(i) for i in files if i[-4:] == 'json' and len(i) > 11]
    [invalid_files_list.append(i) for i in files if len(i) <= 11]
    print('Invalid files: ' + str(invalid_files_list))
    return(json_names)
    

def load_json(json_names):
    json_files = []
    faulty = []
    for file in json_names:
        try:
            with open(JSON_DIR + '\\' + file, encoding="utf8") as f:
                data = json.load(f)
                data = data['result']['data']
                data['pesel'] = file[0:11]
                if type(data) is not list:
                    json_files.append(data)
                else:
                    faulty.append(file + ' - empty')
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            faulty.append(file + ' - faulty')
    files = [json_files, faulty]        
    return(files)


def parse_person(valid_json):
    lvl_1 = json_normalize(valid_json, record_path='firmy', meta = ['name', 'person_id', 'surname', 'wiek', 'pesel'])
    lvl_1.rename(columns = {0:'company_id'}, inplace = True)
    return lvl_1


def parse_role_date(role_date):
    roles = []
    for column in role_date_columns:
        for row in range(0, len(role_date)):
            try:
                role = json_normalize(role_date.loc[row, column])
                role['person_id'] = role_date.loc[row, 'person_id']
                role['company_id'] = role_date.loc[row, 'company_id']
                roles.append(role)
            except:
                pass
    roles = pd.concat(roles)          
    roles.reset_index(drop=True ,inplace=True)  
    return roles


def parse_company(firmy):
    lista_df = []    
    for firma in firmy:
        keys = firma.keys()
        for key in keys:
            lista_df.append(json_normalize(firma[key], meta='rola'))
    firmy_df = pd.concat(lista_df)
    firmy_df.reset_index(drop=True ,inplace=True)
    return firmy_df


def create_df(valid_json):
    dfs = []
    for i in valid_json:
        (keys,values) = zip(*i.items())
        keys = pd.Series(keys)
        values = pd.Series(values,index=keys)
        dfs.append(values)
    df = pd.DataFrame(dfs, columns=keys)
    return df


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
        
    temp = pd.concat(temp)
    temp.reset_index(drop=True ,inplace=True)
    df.drop([table], axis=1, inplace=True)
    return temp


# ## <font color='LIGHTSEAGREEN'> Load data </font>

# In[33]:


files_json = load_json(collect_json_names())
faulty_json = files_json[1]
valid_json = files_json[0]

valid_json_pesel = list(filter(lambda i: len(i) <= 6, valid_json))
valid_json_comapny = list(filter(lambda i: len(i) > 6, valid_json))


# ## <font color='LIGHTSEAGREEN'> Create PERSON </font>

# In[36]:


person = parse_person(valid_json_pesel)

firmy = []
[firmy.append(i['firmy']) for i in valid_json_pesel]

company = parse_company(firmy)

person_company = person.merge(company, left_index=True, right_index=True, how='inner')
person_company.drop(['company_id_x'], axis=1, inplace=True)
person_company.rename(columns = {'company_id_y':'company_id'}, inplace = True)

role_date_columns = ['rola.dg.daty',
        'rola.organ_nadzoru.daty', 'rola.prokura.daty',
       'rola.wspolnik.daty', 'rola.zarzad.daty']

role_date = person_company[role_date_columns + ['person_id', 'company_id']]
person_company.drop(role_date_columns, axis=1, inplace=True)

role = parse_role_date(role_date)

person_company_role = person_company.merge(role, left_on=['person_id', 'company_id'], right_on=['person_id', 'company_id'], how='inner')
person_company_role['koniec'].replace('9999-12-31', 'obecnie', regex=True, inplace=True)
person_company_role.rename(columns = {'nazwa':'nazwa_main'}, inplace = True)


# ## <font color='LIGHTSEAGREEN'> Create COMPANY </font>

# In[35]:

 
spolki = create_df(valid_json_comapny)
spolki.rename(columns = {'nazwa':'nazwa_main'}, inplace = True)

aktywnosc = create_outer_table(spolki, 'aktywnosc')
aktywnosc.rename(columns = {'rola2':'rola_2'}, inplace = True)
aktywnosc.rename(columns = {'koniec':'koniec_2'}, inplace = True)
aktywnosc.rename(columns = {'start':'start_2'}, inplace = True)

aktywnosc['koniec_2'].replace('9999-12-31', 'obecnie', regex=True, inplace=True)
aktywnosc = spolki[['nip', 'nazwa_main']].merge(aktywnosc, left_on=['nip'], right_on=['nip'], how='left')


# ## <font color='LIGHTSEAGREEN'> Create XLSX output </font>

# In[ ]:


if OUTPUT_TYPE == 1:
    person_company_role[columns_order_1].to_excel(OUTPUT_PATH + OUTPUT_NAME + '.xlsx')
elif OUTPUT_TYPE == 2:
    aktywnosc[columns_order_2].to_excel(OUTPUT_PATH + OUTPUT_NAME + '.xlsx')
elif OUTPUT_TYPE == 3:
    final = aktywnosc.append(person_company_role)
    final[columns_order_3].to_excel(OUTPUT_PATH + OUTPUT_NAME + '.xlsx')


