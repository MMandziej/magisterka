import datetime as d
import json
import pandas as pd
import time as t
import urllib.parse

from urllib.parse import quote
from urllib.request import Request, urlopen

from emis import get_date_ago, get_nip_list, get_nip_name

START = t.time()
######## DEFINE USER NAME, PASSWORD AND METHOD #########
USER_NAME = 'wojciech.wyszkowski@pwc.com'
PASSWORD = 'emispwc15' 
YEARS = 10
METHOD = 'getDocuments_Name'
START_DATE = get_date_ago(YEARS)
END_DATE = d.date.today().isoformat()
SEARCH25 = 'NEAR25(%22przest%C4%99p*%20VAT*%22%20OR%20%22przest%C4%99p*%20podat*%22%20OR%20%22przest%C4%99p*%20karuzel*%22%20OR%20%22nadu%C5%BCy*%20podat*%22%20OR%20%22nadu%C5%BCy*%20VAT*%22%20OR%20%22karuzel*%20podat*%22%20OR%20%22karuzel*%20VAT*%22%20OR%20%22wy%C5%82udz*%20VAT*%22%20OR%20%22wy%C5%82udz*%20podat*%22%20OR%20%22oszu*%20VAT*%22%20OR%20%22oszu*%20podat*%22)'
SEARCH50 = 'NEAR50(%22przest%C4%99p*%20VAT*%22%20OR%20%22przest%C4%99p*%20podat*%22%20OR%20%22przest%C4%99p*%20karuzel*%22%20OR%20%22nadu%C5%BCy*%20podat*%22%20OR%20%22nadu%C5%BCy*%20VAT*%22%20OR%20%22karuzel*%20podat*%22%20OR%20%22karuzel*%20VAT*%22%20OR%20%22wy%C5%82udz*%20VAT*%22%20OR%20%22wy%C5%82udz*%20podat*%22%20OR%20%22oszu*%20VAT*%22%20OR%20%22oszu*%20podat*%22)'
TOKEN = 'c95ba1694eafb8da346497423c52f2f60e70f3abeb0b8409c5d7ccd0e5193e0bb7f0294d24d8aa37b203be74957c5151c6c582cb793a3be63523d77177974278'

INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\NIP_list.xlsx'
JSON_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\JSONS_PRESS\\'

################# REQUEST DATA ################

def request_data(method, start_date, end_date, name, search, token): 
    if method == 'getDocuments_ID':
        url = 'https://api.emis.com/news//Search/query/?countries=PL&languages=pl&companies=' + name + '&limit=100&token=' + token
    elif method == 'getDocuments_Name':
        url = 'https://api.emis.com/news//Search/query/?countries=PL&'\
        'languages=pl'\
        '&skipDuplicates=0'\
        '&formats[]=1'\
        '&formats[]=2'\
        '&formats[]=3'\
        '&publicationTypes[]=TN&'\
        '&includeBody=1'\
        '&limit=100'\
        '&startDate=' + start_date +\
        '&endDate=' + end_date +\
        '&term=' + name +\
        '%20' + search +\
        '&token=' + token
    request = Request(url, headers={'User-Agent':'Mozilla/5.0'})
    data_decoded = urlopen(request).read().decode('utf-8')
    return data_decoded

########## GET DOCUMENTS LINKS ###########

def get_documents_links(method, nip_names_dict, output_path):
    json_valid_guid = 'EMIS_PRESS'
    json_valid_guid1 = 'EMIS_PRESS25'
    json_valid_guid2 = 'EMIS_PRESS50'
    json_invalid_guid = 'EMIS_PRESS_Invalid'
    
    nips_jsons = {}
    nips_errors = {}
    nips_jsons25 = {}
    nips_errors25 = {}
    nips_jsons50 = {}
    nips_errors50 = {}

    for nip, name in nip_names_dict.items():
        try:
            name_encoded = quote(name)
            result_decoded = request_data(method, START_DATE, END_DATE, name_encoded, '', TOKEN)
            json_table = json.loads(result_decoded)['data']  
            json_table = {key:json_table[key] for key in ['documents', 'duplicates', 'results', 'total']}
            with open(output_path + nip + '_{}.json'.format(json_valid_guid), 'w') as f:
                json.dump(json_table, f)              
            nips_jsons[nip] = json_table
                
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
            nips_errors[nip] = error
            error_dict = {"name": name, "nip": nip, "error": error}               
            with open(output_path + nip + '_{}.json'.format(json_invalid_guid), 'w') as f:
                json.dump(error_dict, f)       
        
        try:
            name_encoded = quote(name)
            result_decoded25 = request_data(method, START_DATE, END_DATE, name_encoded, SEARCH25, TOKEN)
            json_table25 = json.loads(result_decoded25)['data']  
            json_table25 = {key:json_table25[key] for key in ['documents', 'duplicates', 'results', 'total']}
            with open(output_path + nip + '_{}.json'.format(json_valid_guid1), 'w') as f:
                json.dump(json_table25, f)              
            nips_jsons25[nip] = json_table25
                
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
            nips_errors25[nip] = error
            error_dict25 = {"name": name, "nip": nip, "error": error}               
            with open(output_path + nip + '_{}.json'.format(json_invalid_guid), 'w') as f:
                json.dump(error_dict25, f)
        
        try:
            name_encoded = quote(name)
            result_decoded50 = request_data(method, START_DATE, END_DATE, name_encoded, SEARCH50, TOKEN)
            json_table50 = json.loads(result_decoded50)['data']  
            json_table50 = {key:json_table50[key] for key in ['documents', 'duplicates', 'results', 'total']}
            with open(output_path + nip + '_{}.json'.format(json_valid_guid2), 'w') as f:
                json.dump(json_table50, f)              
            nips_jsons50[nip] = json_table50
                
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
            nips_errors50[nip] = error
            error_dict50 = {"name": name, "nip": nip, "error": error}               
            with open(output_path + nip + '_{}.json'.format(json_invalid_guid), 'w') as f:
                json.dump(error_dict50, f)
                        
    return nips_jsons, nips_errors, nips_jsons25, nips_errors25, nips_jsons50, nips_errors50

############# PARSING JSONS TO DF ##############

def parse_get_documents(nips_jsons, nips_jsons25, nips_jsons50):
    nips_articles_links = {}
    nips_articles_links25 = {}
    nips_articles_links50 = {}

    for nip, table in nips_jsons.items():
        if '_type' in table:
            table.pop('_type')
        documents = table['documents']
        single_articles_ids = []
        for i in documents:
            single_articles_ids.append(str(i['id']))
        nips_articles_links[nip] = single_articles_ids
    
    for nip, table in nips_jsons25.items():
        if '_type' in table:
            table.pop('_type')
        documents = table['documents']
        single_articles_ids = []
        for i in documents:
            single_articles_ids.append(str(i['id']))
        nips_articles_links25[nip] = single_articles_ids
    
    for nip, table in nips_jsons50.items():
        if '_type' in table:
            table.pop('_type')
        documents = table['documents']
        single_articles_ids = []
        for i in documents:
            single_articles_ids.append(str(i['id']))
        nips_articles_links50[nip] = single_articles_ids
        
    test = {}
    press = [nips_articles_links, nips_articles_links25, nips_articles_links50]        
    for dictionary in press:
        for k, v in dictionary.items():
            if dictionary == nips_articles_links:
                test[k] = [len(v)]
            else:
                test[k].append(len(v))
    
    press_df = pd.DataFrame.from_dict(test, orient='index').reset_index()
    press_df.columns = ['NIP', 'Press', 'BadPress25','BadPress50']
    press_df.sort_values(by = ['NIP'], inplace=True, na_position='last')
    press_df = press_df.apply(pd.to_numeric)
    
    press_df.to_excel('EMIS_PRESS_' + str(d.date.today()) + '.xlsx', sheet_name = 'Press', index = False)
    return press_df

###########################################
nip_names_dict = get_nip_name(INPUT_FILE)[1]
nips_jsons, nips_errors, nips_jsons25, nips_errors25, nips_jsons50, nips_errors50 = get_documents_links(METHOD, nip_names_dict, JSON_OUTPUT_PATH)
output  = parse_get_documents(nips_jsons, nips_jsons25, nips_jsons50) 

faitcloud =  pd.read_excel('PWG_FAITCLOUD.xlsx')
final_output = faitcloud.merge(output, how='outer', on='NIP').reset_index(drop=True) 
final_output = final_output.sort_values(by=['NIP'], na_position='last').reset_index(drop=True)
final_output.to_excel('FAITCLOUD_PRESS.xlsx', sheet_name = 'FullOutput')

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))
