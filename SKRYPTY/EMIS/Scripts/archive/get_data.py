import json
import numpy as np
import pandas as pd
from urllib.request import Request, urlopen

######## DEFINE USER NAME AND PASSWORD #########
user_name = 'wojciech.wyszkowski@pwc.com'
password = 'emispwc15' 

### DEFINE METHOD, FINANCIAL YEAR AND PATHS ####
method = 'getStatementByCode'
financial_year = '2015'
input_file = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\NIP_list.xlsx'
JSON_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\\'

############## REQUEST SESSION ID ##############

def get_session_id(user_name, password):
    request = Request('https://api.emis.com/company/Auth/login/?username=' + user_name + '&password=' + password, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    data = response.read()
    data_decoded = data.decode('utf-8')
    session_id = json.loads(data_decoded)['data']['sessionId']
    return session_id

################## GET NIP LIST ################

def get_nip_list(input_file):
    nip_df = pd.read_excel(input_file, header = None, names = ['NIP'])
    nip_list = nip_df['NIP'].tolist()
    return nip_list

################## REQUEST ISIC ################

def request_single_isic(nip, session_id):
    url = 'https://api.emis.com/company/Search/queryCompany/?filter[]=country:PL&filter[]=external_id_class:PL-FISCAL&filter[]=external_id:' + nip + \
    '&sessionId=' + session_id
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    data = response.read()
    data_decoded = data.decode('utf-8')
    return data_decoded

################# GET ISIC LIST ################

def get_isic_list(nip_list, session_id):
    isic_valid = []
    nips_valid = []
    error_list = []
    nips_invalid = []
    for nip in nip_list:
        try:
            nip = str(nip)
            result_decoded = request_single_isic(nip, session_id)
            json_table = json.loads(result_decoded)
            data = json_table['data']
            result_list = data['resultList']
            dic = result_list[0]
            isic = dic['isic']
            isic = str(isic)
            isic_valid.append(isic)
            nips_valid.append(nip)
        except:
            error_list.append('No data in EMIS')
            nips_invalid.append(nip)
    isic_nip_df = pd.DataFrame({'ISIC' : isic_valid,
                                'NIP' : nips_valid})
    
    nips_invalid_df = pd.DataFrame({'NIP' : nips_invalid,
                                    'ISIC' : np.nan,
                                    'ErrorMessage' : error_list})
    return isic_nip_df, nips_invalid_df

################# REQUEST DATA ################

def request_data(isic, method, year, session_id): 
    if method == 'getCompanyLatestStatement':
        url = 'https://api.emis.com/company/Statements/getCompanyLatestStatement/?isic=' + isic + '&sessionId=' + session_id
    elif method == 'getStatementByCode':
        url = 'https://api.emis.com/company/Statements/getStatementByCode/?isic=' + isic + '&year=' + year + '&period=Y&consolidated=N&currency=local&sessionId=' + session_id
        
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    data = response.read()
    data_decoded = data.decode('utf-8')
    return data_decoded

################## GET DATA ##################

def get_data(valid_isic_list, method, session_id, year = '2017'):
    isic_list = valid_isic_list[0]['ISIC'].values.tolist()
    vlook_up_df = valid_isic_list[0]
    nips_invalid_df = valid_isic_list[1]
    method = str(method)
    year = str(year)
    if method == 'getCompanyLatestStatement':
        json_valid_guid = 'EMIS_Latest_Statement'
    elif method == 'getStatementByCode':
        json_valid_guid = 'EMIS_Financial_Statement_' + year
    if method == 'getStatementByCode':
        json_invalid_guid = 'EMIS_Invalid_' + method + '_' + year
    else:
        json_invalid_guid = 'EMIS_Invalid_' + method 
    isic_down = []
    nips_down = []
    jsons_valid_list = []
    isic_invalid = []
    nips_invalid = []
    error_list = []
    for isic in isic_list:
        try:    
            result_decoded = request_data(isic, method, year, session_id)
            json_table = json.loads(result_decoded)       
            
            isic_df = pd.DataFrame([isic], columns = ['ISIC'])
            isic_nip_df = isic_df.merge(vlook_up_df, on ='ISIC')
            nip = isic_nip_df.iloc[0]['NIP']
            nip = str(nip)        
            with open(JSON_OUTPUT_PATH + nip + '_{}.json'.format(json_valid_guid), 'w') as f:
                json.dump(json_table, f)
            jsons_valid_list.append(json_table)
            isic_down.append(isic)
            nips_down.append(nip)
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
            error_list.append(error)
            error_dict = {"isic": isic,
                          "error": error}
            
            isic_df = pd.DataFrame([isic], columns = ['ISIC'])
            isic_nip_df = isic_df.merge(vlook_up_df, on ='ISIC')
            nip = isic_nip_df.iloc[0]['NIP']
            nip = str(nip)        
            
            with open(JSON_OUTPUT_PATH + nip + '_{}.json'.format(json_invalid_guid), 'w') as f:
                json.dump(error_dict, f)
            isic_invalid.append(isic)
            nips_invalid.append(nip)
            
    valid_jsons = pd.DataFrame(
            {'ISIC': isic_down,
             'NIP': nips_down,
             'ValidJSONs': jsons_valid_list})
    invalid_codes =  pd.DataFrame(
            {'ISIC': isic_invalid,
             'NIP': nips_invalid,
             'ErrorMessage': error_list})
                
    invalid_jsons = pd.concat([invalid_codes, nips_invalid_df], sort = True)
    return valid_jsons, invalid_jsons

################ GET OUTPUT ################

session_id = get_session_id(user_name, password)
nip_list = get_nip_list(input_file)
isic_list = get_isic_list(nip_list, session_id)
output = get_data(isic_list, method, session_id, year = '2015')

