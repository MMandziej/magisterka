"""
Script used as library for importing objects and functions to main scripts
which are used to retrieve and parse data from EMIS API.

Data are processed and exported and used for investigating
analysis purposes.
"""

import datetime as d
import json
import pandas as pd
import pyodbc
import re

from math import floor
from statistics import mean
from unidecode import unidecode
from urllib.error import URLError
from urllib.request import Request, urlopen

from naics_slownik import naics_slownik

############ GET DATE X YEARS AGO #############
def get_date_ago(years):
    data = d.date.today() - d.timedelta(days=years*365)
    if data.month == 2 and data.day == 29:
        data = data.replace(day=28)
    data = data.isoformat()
    return data

############## REQUEST SESSION ID ##############
def get_session_id(user_name, password):
    request = Request('https://api.emis.com/company/Auth/login/?username=' +
                      user_name +
                      '&password=' +
                      password,
                      headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    data = response.read()
    data_decoded = data.decode('utf-8')
    session_id = json.loads(data_decoded)['data']['sessionId']
    return session_id

############# GET_PRESS_WHITELIST ###############   
def get_press_whitelist(creds):
    whitelist_dic={}

    conn = pyodbc.connect(creds)
    cursor=conn.cursor()
                
    for a,row in enumerate(cursor.execute("select * from Emis_press_whitelist")):
        single_whitelist_dic={}
        single_whitelist_dic={'NIP':row.NIP, 
                              'REGON':row.REGON, 
                              'NAME':row.Name, 
                              'KEYWORDS':row.Keywords, 
                              'ID':row.ID}
        whitelist_dic[a]=single_whitelist_dic
        
    return whitelist_dic

############# GET SQL DATA ##############
def get_sql_data(project_name, creds):
    valid_ids_dic={}
    invalid_ids_dic={}
    duplicated_ids_dic={}
    press_whitelist={}
    
    conn = pyodbc.connect(creds)
    cursor=conn.cursor()
    
    for row in cursor.execute("Select top 500 Nazwa, dbo.truncateregon(Regon) as trunc_regon, SilosID from [gus].[RegonGeberalData] where projectname='{}' and Regon is not null order by Regon desc".format(project_name)):
        valid_dic, invalid_dic = clean_regon_name(row.trunc_regon, row.Nazwa)
        if valid_dic:
            cleansed_regon=list(valid_dic.keys())[0]
            if row.SilosID == 2 and cleansed_regon in valid_ids_dic.keys():
                duplicated_ids_dic.update(valid_dic)
            else:
                valid_ids_dic.update(valid_dic)
        else:
            invalid_ids_dic.update(invalid_dic)

    log_df = pd.DataFrame({"ValidNIP" : pd.Series(list(valid_ids_dic.keys())),
                           "InvalidNIP" : pd.Series(list(invalid_ids_dic.keys())),
                           "DuplicatedNIP" : pd.Series(list(duplicated_ids_dic.keys()))})

    return valid_ids_dic, invalid_ids_dic, press_whitelist, log_df


######### GET NIP NAME LIST  ###########
def get_nip_name(input_file, id_class, param):
    valid_ids_dic = {}
    invalid_ids_dic = {}

    data = pd.read_excel(input_file, dtype=str, header=None)
    if len(data.columns)== 1:
        data.columns=[str(id_class)]
        print("Company names not found.")
        name_list = []
        data_dedup = data.drop_duplicates(subset=str(id_class))
        duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
        id_list = data_dedup[str(id_class)].tolist()
        for i in id_list:
            name_list.append(None)

    elif len(data.columns)==2:
        if param == 0:
            data.columns=[str(id_class), 'NazwaPodmiotu']
            data_dedup = data.drop_duplicates(subset=str(id_class))
            duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
            id_list = data_dedup[str(id_class)].tolist()
            name_list = data_dedup['NazwaPodmiotu'].tolist()
            for ids, name in zip(id_list,name_list):
                single_valid_dic, single_invalid_dic = clean_name_id(id_class, ids, name)
                if single_valid_dic:
                    valid_ids_dic.update(single_valid_dic)
                else:
                    valid_ids_dic.update(single_invalid_dic)

        elif param == 1:
            data.columns = [str(id_class), 'Obrot']
            data_dedup = data.drop_duplicates(subset=str(id_class))
            duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
            id_list = data_dedup[str(id_class)].tolist()
            turnover_list = [round(float(i), 2) for i in list(data_dedup['Obrot'])]
            # Cleanse nip
            for nip, turn_val in zip(id_list, turnover_list):
                nip_invalid_dic = {}
                nip_valid_dic = {}
                total = 0
                weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
                clean_nip = re.sub(r'[A-Z]', "", nip)
                nip_factorized = list(clean_nip)
                for i, j in zip(nip_factorized, weights):
                    total += int(i)*j
                if re.search(r"[A-Z]", nip, re.IGNORECASE) is not None and re.search("PL", nip, re.IGNORECASE) is None:
                    nip_invalid_dic[nip] = turn_val
                    invalid_ids_dic.update(nip_invalid_dic)
                elif int(nip_factorized[-1]) == total % 11 and len(clean_nip) == 10:
                    nip_valid_dic[nip] = turn_val
                    valid_ids_dic.update(nip_valid_dic)
                else:
                    nip_invalid_dic[nip] = 'n/a'
                    invalid_ids_dic.update(nip_invalid_dic)

    log_df = pd.DataFrame({"ValidNIP" : pd.Series(list(valid_ids_dic.keys())),
                           "InvalidNIP" : pd.Series(list(invalid_ids_dic.keys())),
                           "DuplicatedNIP" : pd.Series(duplicates)})

    args = {'arg1':len(valid_ids_dic.keys()),
            'arg2':id_class}
    print("{arg1} unique valid company ids detected. Chosen company id " \
          "class: {arg2}.".format(**args))

    if valid_ids_dic.keys() <= invalid_ids_dic.keys():
        print("Please assure that chosen ID class is correct")
    return valid_ids_dic, invalid_ids_dic, log_df

################ CLEAN NAME ID #################
def clean_name_id(id_class, company_id, company_name):
    if id_class.upper()=='NIP':
        single_valid_dic, single_invalid_dic = clean_nip_name(company_id, company_name)
    elif id_class.upper()=='REGON':
        single_valid_dic, single_invalid_dic = clean_regon_name(company_id, company_name)
    elif id_class.upper()=='KRS':
        single_valid_dic, single_invalid_dic = clean_krs_name(company_id, company_name)
        
    return single_valid_dic, single_invalid_dic

############ CLEAN_NAME_NIP ###################
def clean_nip_name(nip, name):
    nip_invalid_dic = {}
    nip_valid_dic = {}
    total = 0
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    
    clean_nip = re.sub(r'[A-Z]', "", nip)
    nip_factorized = list(clean_nip)
    for i, j in zip(nip_factorized, weights):
        total += int(i)*j
    if re.search(r"[A-Z]", nip, re.IGNORECASE) is not None and re.search("PL", nip, re.IGNORECASE) is None:
        nip_invalid_dic[nip] = name
    elif int(nip_factorized[-1]) == total % 11 and len(clean_nip) == 10:
        if name is not None:
            trans = name.maketrans("-;", "  ", "'\"")
            name = name.translate(trans).strip()
            name = re.sub(r' +', " ", name)
            for form in legal_forms:
                m = re.search(unidecode(form), unidecode(name), re.IGNORECASE)
                if m:
                    name = name[:m.start()] + name[m.end():]
            name = re.sub(r' +', " ", name).strip()
        nip_valid_dic[clean_nip] = ['"' + name.upper() + '"' if name is not None else None]
    else:
        nip_invalid_dic[nip] = 'n/a' if name == 'nan' else name
    return nip_valid_dic, nip_invalid_dic

def clean_regon_name(regon, name):
    regon_invalid_dic = {}
    regon_valid_dic = {}
    total = 0
    weights_9 = [8, 9, 2, 3, 4, 5, 6, 7]
    weights_14 = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
    clean_regon = re.sub(r'[A-Z]', "", regon)
    regon_factorized = list(clean_regon)
    
    if len(clean_regon)==9:
        for i, j in zip(regon_factorized, weights_9):
            total += int(i)*j
    elif len(clean_regon)==14:
        for i, j in zip(regon_factorized, weights_14):
            total += int(i)*j                
    if re.search(r"[A-Z]", regon, re.IGNORECASE) is not None and re.search("PL", regon, re.IGNORECASE) is None:
        regon_invalid_dic[regon] = name
    elif regon_factorized[-1] == str(total % 11)[-1]:
        if name is not None:
            trans = name.maketrans("-;", "  ", "'\"")
            name = name.translate(trans).strip()
            name = re.sub(r' +', " ", name)
            for form in legal_forms:
                m = re.search(unidecode(form), unidecode(name), re.IGNORECASE)
                if m:
                    name = name[:m.start()] + name[m.end():]
            name = re.sub(r' +', " ", name).strip()
        regon_valid_dic[regon] = ['"' + name.upper() + '"' if name is not None else None]
    else:
        regon_invalid_dic[regon] = 'n/a' if name == 'nan' else name
    return regon_valid_dic, regon_invalid_dic

def clean_krs_name(krs, name):
    krs_invalid_dic = {}
    krs_valid_dic = {}

    clean_krs = re.sub(r'[A-Z]', "", krs)
    if re.search(r"[A-Z]", krs, re.IGNORECASE) is not None and re.search("PL", krs, re.IGNORECASE) is None:
        krs_invalid_dic[krs] = name
    elif len(clean_krs) == 10:
        if name is not None:
            trans = name.maketrans("-;", "  ", "'\"")
            name = name.translate(trans).strip()
            name = re.sub(r' +', " ", name)
            for form in legal_forms:
                m = re.search(unidecode(form), unidecode(name), re.IGNORECASE)
                if m:
                    name = name[:m.start()] + name[m.end():]
            name = re.sub(r' +', " ", name).strip()
        krs_valid_dic[clean_krs] = ['"' + name.upper() + '"' if name is not None else None]
    else:
        krs_invalid_dic[krs] = 'n/a' if name == 'nan' else name
    return krs_valid_dic, krs_invalid_dic

############# LEGAL FORMS ##############
legal_forms = [
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SPÓŁKA KOMANDYTOWA", "Sp\.z o\.o\.",
    "P\.P\.U\.H.", "PPUH", "PRZEDSIĘBIORSTWO HANDLOWO PRODUKCYJNE", "PHU", "P\.H\.U.",
    "SPÓŁKA CYWILNA", "SPÓŁKA JAWNA"," SP\. J\.", "SPÓŁKA KOMANDYTOWA", "SPÓŁKA AKCYJNA",
    "PRZEDSIĘBIORSTWO HANDLOWO USŁUGOWE", "SPÓŁKA KOMANDYTOWO AKCYJNA","SP Z O\.O\.",
    "Przedsiębiorstwo wielobranżowe", "SPÓŁKA KOMANDYTOWO AKCYJNA","SP\.K\.",
    "SPÓŁKA PARTNERSKA", "FIRMA TRANSPORTOWO HANDLOWA", "SPÓŁKA KOMANDYTOWO   AKCYJNA",
    "ZAKŁAD PRODUKCYJNO USŁUGOWY", "PRZEDSIĘBIORSTWO WIELOBRANŻOWE", "Sp\. z o\.o\.",
    "FIRMA HANDLOWO USŁUGOWA", "PRZEDSIEBIORSTWO PRODUKCYJNO USLUGOWO HANDLOWE",
    "PRZEDSIEBIORSTWO WIELOBRANZOWE", "SPOLKA KOMANDYTOWO AKCYJNA", " S\.C\.",
    "SP\. Z O\.O\.", "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZILNOŚCIĄ", " S\.A\.",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOIŚCIĄ", "PPHU", "P\.P\.P\.U\.",
    "PRZEDSIĘBIORSTWO PRODUKCYJNO HANDLOWO USŁUGOWE", " S\.K\." "SPÓŁKA Z O\.O",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNO0ŚCIĄ", "SPOLKA Z O\.O\.", " SP\.J\.",
    "SPÓŁKA Z OGRANICZONĄ OSPOWIEDZIALNOŚCIĄ", "FIRMA HANDLOWO USŁUGOWA",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIELNOŚCIĄ", "SPÓŁKI JAWNEJ", "SPÓŁKA Z O\.O\.",
    "SPÓŁKA KOMANDYTWO AKCYJNA", "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALANOŚCIĄ",
    "SPOLKA Z ORGANICZONA ODPOWIEDZIALNOSCIA", "SPÓŁKA OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
    "SPÓŁKA ZOGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZILANOŚCIĄ",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNŚCIĄ", "SPÓŁKA Z OGRANICZONĄ ODOWIEDZIALNOŚCIĄ",
    "SPÓŁKA Z OGRANICZONĄ 0ODPOWIEDZIALNOŚCIĄ","SP\.ZOO",
    "SPÓŁKA HANDLOWO USŁUGOWA", "SPÓŁKA Z ODPOWEDZIALNOŚCIĄ", "W LIKWIDACJI",
    "SPÓŁKA Z OGRANICZONĄ OODPOWIEDZIALNOŚCIĄ", "W UPADŁOŚCI LIKWIDACYJNEJ",
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZALNOŚCIĄ", "Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ"]

################## FORMAT PRESS INPUT ###################

def format_press_input(name_list):
    search_term=''
    
    if len(name_list)==1:
        search_term = name_list[0]
    elif len(name_list)>1:
        for name in name_list:
            search_term += ' OR '  + name
    search_term ='(' + search_term.replace(' OR ', '', 1) + ')'
    
    return search_term
    
################## REQUEST ISIC ################
def request_single_isic(nip, session_id, id_class):
    if id_class == 'NIP':
        id_type = 'PL-FISCAL'
    elif id_class == 'KRS':
        id_type = 'PL-KRS'
    elif id_class == 'REGON':
        id_type = 'PL-REGON'
    
    url = 'https://api.emis.com/company/Search/queryCompany/?' + \
        'filter[]=country:PL&filter[]=external_id_class:' + id_type + \
        '&filter[]=external_id:' + nip + \
        '&sessionId=' + session_id
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    data = response.read()
    data_decoded = data.decode('utf-8')
    return data_decoded

################# GET ISIC LIST ################
def get_isic_list(nip_name_valid, session_id, id_class):
    nips_isics = {}
    nips_errors = {}
    #for dic in nip_name_valid:
    for nip, name in nip_name_valid.items():
        try:
            result_decoded = request_single_isic(nip, session_id, id_class)
            json_table = json.loads(result_decoded)['data']['resultList']
            if json_table:
                isic = str(json_table[0]['isic'])
                nips_isics[nip] = isic
            else:
                nips_errors[nip] = 'No data in EMIS'
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            nips_errors[nip] = error
                
    print("Data in EMIS available for %s companies." % len(nips_isics))
    return nips_isics, nips_errors

################# REQUEST DATA ################
def request_data(method, isic, session_id, token, date, search, fiscal_year=''):
    if method == 'getFullCompany':
        url = 'https://api.emis.com/company/Companies/getFullCompany/?' + \
            'isic=' + isic + '&sessionId=' + session_id
    elif method == 'getStatementByCode':
        url = 'https://api.emis.com/company/Statements/getStatementByCode/?' + \
            'isic=' + isic + \
            '&year=' + fiscal_year + \
            '&period=Y&consolidated=N&currency=local&sessionId=' + session_id
    elif method == 'getDocuments_ID':
        url = 'https://api.emis.com/news//Search/query/?countries=PL&languages=pl&' + \
            'companies=' + isic + '&limit=300&token=' + token
    elif method == 'getDocuments_Name':
        url = 'https://api.emis.com/news//Search/query/?countries=PL&languages=pl&' + \
            'skipDuplicates=0&formats[]=1&formats[]=2&includeBody=1&limit=100&' + \
            'startDate=' + date + '&term=' + isic + '%20' + search + '&token=' + token
    request = Request(url, headers={'User-Agent':'Mozilla/5.0'})
    response = urlopen(request)
    data_decoded = response.read().decode('utf-8')
    return data_decoded

############## GET COMPANY INFO ###############
def get_company_info(nips_isics, nips_errors, session_id, output_path, method):
    json_guid = 'EMIS_REGISTER'
    nips_jsons = {}
    for nip, isic in nips_isics.items():
        requests_limit = 0
        try:
            result_decoded = request_data(method, isic, session_id, '', '', '')
            json_table = json.loads(result_decoded)['data']
            with open(output_path +
                      nip +
                      '_{}.json'.format(json_guid), 'w') as file:
                json.dump(json_table, file)

            nips_jsons[nip] = json_table

        except (TimeoutError, URLError, ConnectionAbortedError) as exc:
            error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
            error_dict = {"isic" : isic, "nip" : nip, "error" : error}
            with open(output_path +
                      nip +
                      '_{}.json'.format(json_guid + '_INVALID'), 'w') as file:
                json.dump(error_dict, file)
            requests_limit += 1
            
            while requests_limit < 3:
                try:
                    result_decoded = request_data(method, isic, session_id, '', '', '')
                    json_table = json.loads(result_decoded)['data']
                    with open(output_path +
                              nip +
                              '_{}.json'.format(json_guid), 'w') as file:
                        json.dump(json_table, file)
                    nips_jsons[nip] = json_table
                except Exception:
                    requests_limit += 1

        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            nips_errors[nip] = error
            error_dict = {"isic": isic, "nip": nip, "error": error}

            with open(output_path +
                      str(nip) +
                      '_{}.json'.format(json_guid + '_INVALID'), 'w') as file:
                json.dump(error_dict, file)
    print("Data successfully acquired for %s companies." % len(nips_jsons))
    return nips_jsons, nips_errors

############ FLATTEN NESTED JSONS ##############
def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out


############### PARSE EMPLOYEES ##############
def parse_employees(result: dict) -> dict:
    # Parse employees number
    if result['EmployeeNumberType'] == 'real_fixed':
        result['Number of Employees'] = result['EmployeeNumber']

    elif result['EmployeeNumberType'] == 'real_range': # and 'employeeNumberRange_min' in result and 'employeeNumberRange_max' in result:
        if result['employeeNumberRange_min'] is not None and result['employeeNumberRange_max'] is not None:
            result['Number of Employees'] = str(floor(mean([int(result['employeeNumberRange_min']), int(result['employeeNumberRange_max'])])))
        elif result['employeeNumberRange_min'] is not None and result['employeeNumberRange_max'] is None:
            result['Number of Employees'] = result['employeeNumberRange_min']
        elif result['employeeNumberRange_min'] is None and result['employeeNumberRange_max'] is not None:
            result['Number of Employees'] = result['employeeNumberRange_max']

    elif result['EmployeeNumberType'] is None:
        result['Number of Employees'] = None
    else:
        result['Number of Employees'] = None

    # Parse employees number date
    if result['EmployeeNumberDate'] is not None:
        result['EmployeesNumberDate3YearsAgo'] = 0 if d.datetime.strptime(result['EmployeeNumberDate'], '%Y-%m-%d') > d.datetime.now() - d.timedelta(days=3*365) else 1
    else:
        result['EmployeesNumberDate3YearsAgo'] = 'n/a'

    # Drop unnecessary keys
    for key in ['EmployeeNumber', 'employeeNumberRange', 'employeeNumberRange_min', 'employeeNumberRange_max']:
        result.pop(key, None)
    return result

################# PARSE AFFILIATES ################
def parse_affiliates(result: dict) -> dict:
    # PARSE AFFILIATES
    affiliates = []
    affiliates_percentage = []
    affiliates_count = 0
    affiliates_foreign = 0
    affiliates_emis = 0
    affiliateship_total = 0
    affiliateship_type = 0
    for key, value in result.items():
        if key.startswith('affiliateList_') and key.endswith('_affiliateNameLocal'):
            affiliates_count += 1
            for i, j in {
                    ', ExternalID: ' : '_affiliateExternalId',
                    ', ISIC: ' : '_affiliateIsic',
                    ', Percentage: ' : '_affiliateshipPercentage',
                    ', Type: ' : '_affiliateshipType'}.items():
                key_processed = key[:15] + j if len(key) == 34 else key[:16] + j
                affiliate = 'Name: ' + value
                info = i + str(result[key_processed])
                affiliate += info
            affiliates.append(affiliate)
        if key.startswith('affiliateList_') and key.endswith('_affiliateCountry'):
            if value is not None and value != 'PL':
                affiliates_foreign = 1
        if key.startswith('affiliateList_') and key.endswith('_affiliateshipPercentage'):
            if value is not None:
                affiliates_percentage.append(float(value))
            if value == '100':
                affiliateship_total = 1
        if key.startswith('affiliateList_') and key.endswith('_affiliateIsic'):
            if value is not None:
                affiliates_emis += 1
        if key.startswith('affiliateList_') and key.endswith('_affiliateshipType'):
            if value != 'Total':
                affiliateship_type = 1

    affiliates_dedup = list(set(affiliates))
    affiliates_merged = ', '.join(affiliates_dedup)

    # Add new variables to output
    result['AffiliatesMerged'] = affiliates_merged if affiliates_merged.split() else 'n/a'
    result['AffiliatesCount'] = affiliates_count
    result['AffiliatesForeign'] = affiliates_foreign
    result['AffiliatesEMIS'] = affiliates_emis
    result['AffilatteshipMin'] = min(affiliates_percentage, default='n/a')
    result['AffilatteshipMax'] = max(affiliates_percentage, default='n/a')
    if affiliates_percentage:
        result['AffilatteshipAvg'] = mean(affiliates_percentage)
    else:
        result['AffilatteshipAvg'] = 'n/a'
    result['AffilatteshipsTotal'] = affiliateship_total
    #result['AffilatteshipsType'] = affiliateship_type

    # Drop unnecessary keys
    affiliates_keys_drop = []
    for col in ['_affiliateCountry', '_affiliateExternalId', '_affiliateExternalIdClass',
        '_affiliateIsic', '_affiliateName', '_affiliateNameLocal', '_affiliateshipPercentage', '_affiliateshipType']:
        for key in result.keys():
            if key.endswith(col) or key.startswith(col):
                affiliates_keys_drop.append(key)
    for key in affiliates_keys_drop:
        result.pop(key, None)
    return result


################# PARSE EXECUTIVES ################
def parse_executives(result: dict) -> dict:
    # PARSE AFFILIATES
    executives = []
    for key, value in result.items():
        if key.endswith('_executiveNameLocal'):
            executive = value
            key_processed = key[:len(key)-19] + '_executiveUserDefinedPositionLocal'
            executive += ' (' + result[key_processed] + ')'
            executives.append(executive)

    executives_dedup = list(set(executives))
    executives_merged = ', '.join(executives_dedup)
    
    result['ExecutivesCount'] = len(executives_dedup)
    result['ExecutivesMerged'] = executives_merged if executives_merged.split() else 'n/a'

    # Drop unnecessary keys
    executives_keys_drop = []
    for col in ['_executiveCode', '_executiveNameLocal', '_executiveUserDefinedPosition',
        '_executiveUserDefinedPositionLocal', '_globalExecutiveCode']:
        for key in result.keys():
            if key.endswith(col):
                executives_keys_drop.append(key)
    for key in executives_keys_drop:
        result.pop(key, None)
    return result


############### PARSE OWNERS ##############
def parse_owners(result: dict) -> dict:
    owners_count = 0
    owners_isics = 0
    owners_foreign = 'null'
    owners = []
    for key, value in result.items():
        if key.startswith('ownerList_') and key.endswith('_ownerIsic'):
            owners_count += 1
            if value is not None:
                owners_isics += 1
        elif key.startswith('ownerList_') and key.endswith('_ownerCountry') and value is not None:
            if value is not None and value == 'PL':
                owners_foreign = 0
            elif value is not None and value != 'PL':
                owners_foreign = 1

        elif key.startswith('ownerList_') and key.endswith('_ownerNameLocal'):
            owner = value
            key_processed = key[:len(key)-15] + '_ownershipPercentage'
            owner += ' (' + str(round(float(result[key_processed]), 2)) + ')'
            owners.append(owner)
    owners_dedup = list(set(owners))

    result['OwnersMerged'] = ', '.join(owners_dedup)
    result['OwnersCount'] = owners_count
    result['OwnersInEMIS'] = owners_isics
    result['OwnersForeign'] = owners_foreign

    # Drop unnecessary keys
    owners_keys_drop = []
    for col in ['__type', '_ownerCountry', '_ownerExternalId', '_ownerExternalIdClass', '_ownerIsic',
        '_ownerNameLocal', '_ownerName', '_ownerType', '_ownershipPercentage', '_ownershipType']:
        for key in result.keys():
            if key.startswith('ownerList_') and key.endswith(col):
                owners_keys_drop.append(key)
    for key in owners_keys_drop:
        result.pop(key, None)
    return result


################# PARSE EXTERNAL IDS ################
def parse_external_ids(result: dict) -> dict:
    external_ids = {}
    other_ids = 0
    for key in result.keys():
        if key.startswith('externalIdList_') and key.endswith('_classCode'):
            key_processed = key[:17] + 'externalId'
            if result[key] in ['PL-KRS', 'PL-REGON']:
                external_ids[result[key][3:]] = result[key_processed]
            elif result[key] == 'PL-FISCAL':
                external_ids['NIP'] = result[key_processed]
            else:
                other_ids += 1

    external_ids['ExternalIdsOthers'] = other_ids
    for key, value in external_ids.items():
        result[key] = value

    # Drop unnecessary keys
    external_ids_keys_drop = []
    for col in ['_classCode', '_externalId']:
        for key in result.keys():
            if key.endswith(col):
                external_ids_keys_drop.append(key)
    for key in external_ids_keys_drop:
        result.pop(key, None)
    return result


############### PARSE OUTSTANDING SHARELIST ##############
def parse_outstanting_shares(result: dict) -> dict:
    shares_value = 0
    shares_dates = []
    for key in result.keys():
        if key.startswith('outstandingSharesList_') and key.endswith('_outstandingShareValue'):
            shares_value += float(result[key])
        if key.startswith('outstandingSharesList_') and key.endswith('_outstandingShareDate'):
            shares_dates.append(d.datetime.strptime(result[key], '%Y-%m-%d'))

    result['OutstandingSharesSum'] = shares_value
    if shares_dates:
        latest_date = max(shares_dates)
        result['OutstandingSharesDate'] = latest_date
        result['OutstandingSharesDateLessThan2YearsAgo'] = 1 if latest_date > d.datetime.now() - d.timedelta(days=2*365) else 0
    else:
        result['OutstandingSharesDate'] = 'n/a'
        result['OutstandingSharesDateLessThan2YearsAgo'] = 0

    # Drop unnecessary keys
    shares_keys_drop = []
    for col in ['_outstandingShareDate', '_outstandingShareSeriesName', '_outstandingShareValue', 'outstandingSharesList']:
        for key in result.keys():
            if key.startswith('outstandingSharesList') and key.endswith(col):
                shares_keys_drop.append(key)
    for key in shares_keys_drop:
        result.pop(key, None)
    return result


############### PARSE DIVIDENDS ##############
def parse_dividends(result: dict) -> dict:
    # Parse dividend
    dividends_types = []
    dividends_currencies = []
    dividends_presence = 1
    dividends_count = 0
    dividends_sum = 0
    dividends_time_horizon = 0

    for key, value in result.items():
        if key.endswith('dividendList'):
            dividends_presence = 0
        elif key.endswith('dividendType'):
            dividends_types.append(value)
            dividends_count += 1
        elif key.endswith('dividendCurrency'):
            dividends_currencies.append(value)
        elif key.endswith('dividendValue'):
            dividends_sum += float(value)
        elif key.endswith('dividendPayDate') and d.datetime.strptime(value, '%Y-%m-%d') > d.datetime.now() - d.timedelta(days=2*365):
            dividends_time_horizon = 1

    dividends_types_dedup = list(set(dividends_types))
    dividend_ccy_dedup = list(set(dividends_currencies))

    result['DividendPresent'] = dividends_presence
    #result['DividendTypes'] = ', '.join(dividends_types_dedup)
    #result['DividendCurrencies'] = ', '.join(dividend_ccy_dedup)
    result['DividendCount'] = dividends_count
    result['DividendSum'] = dividends_sum
    result['DividendDate2YearsAgo'] = dividends_time_horizon

    # Drop unnecessary keys
    dividends_keys_drop = []
    for col in ['_dividendCurrency', '_dividendPayDate', '_dividendType', '_dividendValue', 'dividendList']:
        for key in result.keys():
            if key.endswith(col):
                dividends_keys_drop.append(key)
    for key in dividends_keys_drop:
        result.pop(key, None)
    return result


############### PARSE SEGMENT ##############
def parse_segment(result: dict) -> dict:
    segment_presence = 0
    segment_names = []
    segment_stock_exchange_ids = []
    segment_stock_names = []
    for key, value in result.items():
        if key.startswith('segmentList_') and key.endswith('_segmentName'):
            segment_presence = 1
            segment_names.append(value)
        elif key.startswith('segmentList_') and key.endswith('_segmentStockExchangeId'):
            segment_stock_exchange_ids.append(value)
        elif key.startswith('segmentList_') and key.endswith('_segmentStockName'):
            segment_stock_names.append(value)

    segment_names_dedup = list(set(segment_names))
    segment_names_merged = ', '.join(segment_names_dedup)

    segment_stock_exchange_ids_dedup = list(set(segment_stock_exchange_ids))
    segment_stock_exchange_ids_merged = ', '.join(segment_stock_exchange_ids_dedup)

    segment_stock_names_dedup = list(set(segment_stock_names))
    segment_stock_names_merged = ', '.join(segment_stock_names_dedup)

    result['SegmentPresence'] = segment_presence
    result['SegmentName'] = segment_names_merged if segment_names_merged.strip() else 'n/a'
    result['SegmentStockExchangeId'] = segment_stock_exchange_ids_merged if segment_stock_exchange_ids_merged.strip() else 'n/a'
    result['SegmentStockName'] = segment_stock_names_merged if segment_stock_names_merged.strip() else 'n/a'

    # Drop unnecessary keys
    segment_keys_drop = []
    for col in ['_segmentName', '_segmentStockExchangeId', '_segmentStockName', 'segmentList']:
        for key in result.keys():
            if key.startswith('segmentList') and key.endswith(col):
                segment_keys_drop.append(key)
    for key in segment_keys_drop:
        result.pop(key, None)
    return result


############### PARSE NAICS ##############
def parse_naics(result: dict) -> dict:
    main_naics_list = []
    main_pkd = 'n/a'
    secondary_pkd_list = []
    secondary_naics_list = []
    for key in result.keys():
        # Main activity
        if key.startswith('mainActivityList_') and key.endswith('_naics'):
            main_naics_list.append(result[key][:3])
        if key.startswith('mainActivityList_') and key.endswith('_induClass'):
            key_processed = key[:18] + '_induCode' if len(key) == 28 else key[:19] + '_induCode'
            if result[key] == 'pkd_2007':
                main_pkd = result[key_processed]
        # Secondary activity
        if key.startswith('secondaryActivityList_') and key.endswith('_naics'):
            secondary_naics_list.append(result[key][:3])
        if key.startswith('secondaryActivityList_') and key.endswith('_induClass'):
            key_processed = key[:24] + 'induCode'
            if result[key] == 'pkd_2007':
                secondary_pkd_list.append(result[key_processed])

    main_naics_list_dedup = list(set(main_naics_list))
    main_naics_merged = ', '.join(main_naics_list_dedup)
    sec_naics_list_dedup = list(set(secondary_naics_list))
    sec_naics_merged = ', '.join(sec_naics_list_dedup)
    secondary_pkd_list_dedup = list(set(secondary_pkd_list))
    sec_pkd_merged = ', '.join(secondary_pkd_list_dedup)

    result['MainPKD'] = main_pkd
    result['MainNAICSCount'] = str(len(main_naics_list_dedup))
    result['MainNAICSCodes'] = main_naics_merged if main_naics_merged.strip() else 'n/a'
    result['SecondaryPKD'] = sec_pkd_merged
    result['SecondaryPKDCount'] = str(len(secondary_pkd_list_dedup))
    result['SecondaryNAICSCodes'] = sec_naics_merged if sec_naics_merged.strip() else 'n/a'

    # Drop unnecessary keys
    naics_ids_keys_drop = []
    for col in ['_naics', '_induClass', '_induCode']:
        for key in result.keys():
            if key.startswith('mainActivityList_') or key.startswith('secondaryActivityList_') and key.endswith(col):
                naics_ids_keys_drop.append(key)
    for key in naics_ids_keys_drop:
        result.pop(key, None)
    return result


############### PARSE PREVIOUS NAMES ##############
def parse_previous_names(result: dict, nip_names_dict: dict, nips_isics: dict, class_id: str) -> dict:
    prev_names_count = 0
    prev_names_changes_dates = []
    key_ID = [ids for ids, isic in nips_isics.items() if isic == result['EMISID']][0]
    
    for key, value in result.items():
        if key.startswith('previousNameList_'):
            if key.endswith('_previousNameLocalName'):
                cleansed_dic, inv_dic  = clean_name_id(class_id, key_ID, value)
                name = cleansed_dic[key_ID][0]
                if not nip_names_dict[key_ID][0].replace('"','') in name.replace('"',''):
                    nip_names_dict[key_ID].append(name)
            if key.endswith('_previousNameChangeYear'):
                prev_names_count += 1
                if value is not None:
                    prev_names_changes_dates.append(d.datetime.now().year - int(value))

    result['PreviousNamesCount'] = prev_names_count
    result['PreviousNameChangeYearsAgo'] = min(prev_names_changes_dates) if prev_names_changes_dates else 'n/a'

    # Drop unnecessary keys
    previous_names_keys_drop = []
    for col in ['_previousNameChangeYear', '_previousNameLocalName', 'previousNameList']:
        for key in result.keys():
            if key.startswith('previousNameList') and key.endswith(col):
                previous_names_keys_drop.append(key)
    for key in previous_names_keys_drop:
        result.pop(key, None)
    return result, nip_names_dict


################ COLS TO DROP ################
cols_drop = [
    '_type', 'auditorName', 'companyName', 'companyLocalName',
    'companySizeRevenue', 'companySizeType', 'companySizeYear',
    'displayName', 'globalLegalForm', 'latestMarketCapitalizationCurrency',
    'mainProductsLocal', 'ratingList']


OUTPUT_RENAME = {
    'address_addressLocal': 'Address',
    'address_cityLocal': 'City',
    'address_email': 'EmailAddress',
    'address_fax': 'Fax',
    'address_phone': 'Phone',
    'address_postalCode': 'PostalCode',
    'address_regionLocal': 'Region',
    'address_url': 'Website',
    'auditorDate': 'AuditDate',
    'auditorName': 'AuditorName',
    'displayNameLocal': 'CompanyName',
    'companySizeRevenue': 'CompanyRevenue',
    'companySizeYear': 'CompanyRevenueYear',
    'companyType': 'CompanyType',
    'countryCode': 'Country',
    'description': 'Description',
    'employeeNumber': 'EmployeeNumber',
    'employeeNumberDate': 'EmployeeNumberDate',
    'employeeNumberType': 'EmployeeNumberType',
    'globalLegalForm': 'GlobalLegalForm',
    'incorporationYear': 'IncorporationYear',
    'isic': 'EMISID',
    'latestMarketCapitalization': 'LatestMarketCapitalization',
    'legalForm': 'LegalForm',
    'mainProducts': 'MainProducts',
    'profileUpdateDate': 'ProfileUpdateDate',
    'registeredCapitalDate': 'RegisteredCapitalDate',
    'registeredCapitalValue': 'RegisteredCapitalValue',
    'status': 'Status'}

PUBLIC_DOMAINS = [
    '@gmail', '@wp', '@poczta.onet', '@onet.', '@op.pl', '@gazeta.pl', '@go2',
    '@yahoo', '@o2', '@autograf.pl', '@buziaczek.pl', '@tlen.', '@hotmail',
    '@interia.', '@vp', '@gery.pl', '@akcja.pl', '@czateria.pl', '@1gb.pl', '@2gb.pl',
    '@os.pl', '@skejt.pl', '@fuks.pl', '@ziomek.pl', '@oferujemy.info', '@twoj.info',
    '@twoja.info', '@boy.pl', '@najx.com', '@adresik.com', '@e-mail.net.pl', '@iv.pl',
    '@bajery.pl', '@gog.pl', '@os.pl', '@serwus.pl', '@aol.pl', '@poczta.fm',
    '@lycos.co%', '@windowslive.com', '@spoko.pl', '@outlook.com']

######### OUTPUT COLUMNS ###########
FULL_REGISTER_COLS = [
    'NIP', 'EMISID', 'KRS', 'REGON', 'CompanyName', 'Data rozpoczęcia współpracy',
    'Region', 'Address', 'AddresFlat', 'City', 'PostalCode', 'Country', 'CountryForeign', 
    'Website', 'WebsiteNotPresent', 'EmailAddress', 'EmailAdressNotPresent', 'EmailAdressPublic',
    'Fax', 'FaxNotPresent', 'Phone', 'PhoneNotPresent', 'ProfileUpdateDate',
    'IncorporationYear', 'IncYearsAgo', 'IncLessThan1YearsAgo', 'IncLessThan3YearsAgo',
    'IncLessThan5YearsAgo', 'IncLessThan10YearsAgo', 'LegalForm', 'GlobalLegalForm',
    'CompanyType', 'Number of Employees', 'EmployeeNumberDate', 'EmployeesNumberDate3YearsAgo',
    'LatestMarketCapitalization', 'MarketCapNull', 'ExecutivesCount', 'ExecutivesMerged',
    'OwnersCount', 'OwnersForeign', 'OwnersInEMIS', 'OwnersMerged', 'AffiliatesMerged',
    'OutstandingSharesSum', 'OutstandingSharesDate', 'OutstandingSharesDateLessThan2YearsAgo',
    'ExternalIdsOthers', 'MainNAICSCodes', 'MainNAICSCount', 'MainPKD', 'SecondaryNAICSCodes',
    'SecondaryPKD', 'SecondaryPKDCount', 'MainProducts', 'MainProductsNull', 'Description',
    'DescriptionNull', 'Status', 'RegisteredCapitalValue', 'RegisteredCapitalDate',
    'CompanyRevenue', 'CompanyRevenueYear', 'CompanyRevenue2YearsAgo',
    'AuditorName', 'AuditDate', 'AuditDateNull', 'AuditDateYearsAgo',
    'PreviousNamesCount', 'PreviousNameChangeYearsAgo',
    'DividendCount', 'DividendDate2YearsAgo', 'DividendPresent', 'DividendSum',
    'SegmentName', 'SegmentPresence', 'SegmentStockExchangeId', 'SegmentStockName',
    'AffilatteshipAvg', 'AffilatteshipMax', 'AffilatteshipMin', 'AffilatteshipsTotal',
    'AffiliatesCount', 'AffiliatesEMIS', 'AffiliatesForeign']


############### GUIDS TO DROP  ###############
"""
len_guids = [-34, -29, -27, -25, -24, -23, -22, -21, -20, -19, -18,
             -17, -16, -15, -14, -13, -12, -11, -10, -9, -6]
"""
cols_guids_to_drop = [
    '__type', '_executiveName', '_executiveNameLocal', '_executiveUserDefinedPositionLocal',
    '_executiveUserDefinedPosition', '_executiveCode', '_globalExecutiveCode', '_ownerIsic',
    '_ownerCountry', '_ownerExternalId', '_ownerExternalIdClass', '_ownerIsic', '_ownerName',
    '_ownerType', '_outstandingShareDate', '_outstandingShareSeriesName',
    '_outstandingShareValue', '_previousNameName', '_previousNameLocalName',
    '_previousNameChangeYear', '_ownershipType', '_ownerNameLocal', '_ownershipPercentage',
    '_affiliateExternalId', '_affiliateExternalIdClass', '_affiliateName',
    '_affiliateshipType', '_affiliateCountry', '_affiliateIsic', '_affiliateNameLocal',
    '_affiliateshipPercentage', '_dividendCurrency', '_dividendPayDate', '_dividendType',
    '_dividendValue', '_segmentName', '_segmentStockExchangeId', '_segmentStockName',
    '_classCode', '_externalId', '_naics', '_induClass', '_induCode']

################# KNOWN COLS #################
known_cols = [
    'NIP', 'EMISID', 'CompanyName', 'Data rozpoczęcia współpracy', 'Województwo',
    'Adress', 'City', 'PostalCode', 'Country', 'Website', 'EmailAdress', 'Fax',
    'Phone', 'ProfileUpdateDate', 'IncorporationYear', 'LegalForm', 'CompanyType',
    'EmployeesNumberDate', 'Number of Employees', 'RegisteredCapitalDate',
    'RegisteredCapitalValue', 'RegisteredCapitalCurrency', 'KeyExecutives',
    'Shareholders', 'NationalFiscalIDs', 'Industry']

financial_data_cols_unprocessed = [
    'NIP', 'Data rozpoczęcia współpracy', 'NS', 'OP', 'PERSON',
    'TS', 'NP', 'TANG', 'CE', 'SE', 'ISSUED', 'FiscalYear', 'consolidated']

financial_data_cols = [
    'EMISID', 'NIP', 'Data rozpoczęcia współpracy', 'NetSalesRevenue',
    'OperatingProfitEBIT', 'EmployeeBenefitExpense', 'TotalAssets',
    'NetProfitLossForThePeriod', 'PropertyPlantAndEquipment', 'CashandCashEquivalents',
    'TotalEquity', 'IssuedCapital', 'FiscalYear', 'consolidated']

accounts = ['NS', 'OP', 'PERSON', 'TS', 'NP', 'TANG', 'CE', 'SE', 'ISSUED']

cols_rename = {
    'NS': 'NetSalesRevenue',
    'OP': 'OperatingProfitEBIT',
    'PERSON': 'EmployeeBenefitExpense',
    'TS': 'TotalAssets',
    'NP': 'NetProfitLossForThePeriod',
    'TANG': 'PropertyPlantAndEquipment',
    'CE': 'CashandCashEquivalents',
    'SE': 'TotalEquity',
    'ISSUED': 'IssuedCapital'}

cols_to_str = [
    'NIP', 'EMISID', 'CompanyName', 'Województwo', 'Adress', 'City', 'PostalCode',
    'Country', 'Website', 'EmailAdress', 'Fax', 'Phone', 'LegalForm', 'CompanyType',
    'RegisteredCapitalValue', 'RegisteredCapitalCurrency', 'KeyExecutives',
    'Shareholders', 'NationalFiscalIDs', 'Industry']

PUBLIC_DOMAINS = [
    '@gmail', '@wp', '@poczta.onet', '@onet.', '@op.pl', '@gazeta.pl', '@go2',
    '@yahoo', '@o2', '@autograf.pl', '@buziaczek.pl', '@tlen.', '@hotmail',
    '@interia.', '@vp', '@gery.pl', '@akcja.pl', '@czateria.pl', '@1gb.pl', '@2gb.pl',
    '@os.pl', '@skejt.pl', '@fuks.pl', '@ziomek.pl', '@oferujemy.info', '@twoj.info',
    '@twoja.info', '@boy.pl', '@najx.com', '@adresik.com', '@e-mail.net.pl', '@iv.pl',
    '@bajery.pl', '@gog.pl', '@os.pl', '@serwus.pl', '@aol.pl', '@poczta.fm',
    '@lycos.co%', '@windowslive.com']


FLATTEN_COLS_DROP = [
    '__type', 'address_address', 'address_city', 'address_region', 'affiliateName', 'descriptionLocal',
    'executiveName', 'executiveUserDefinedPosition', 'mainProductsLocal', 'ownerName', 'previousNameName']
