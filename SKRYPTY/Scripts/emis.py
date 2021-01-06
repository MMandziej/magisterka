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

######### GET NIP NAME LIST  ###########
def get_nip_name(input_file, id_class):
    valid_ids_list = []
    invalid_ids_list = []
    id_name_valid = []
    id_name_invalid = []
    
    data = pd.read_excel(input_file, dtype=str, header=None)
    if len(data.columns)==2:
        data.columns=[str(id_class), 'NazwaPodmiotu']
        data_dedup = data.drop_duplicates(subset=str(id_class))
        duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
        id_list = data_dedup[str(id_class)].tolist()
        name_list = data_dedup['NazwaPodmiotu'].tolist()

                                
    elif len(data.columns)== 1:
        data.columns=[str(id_class)]
        print("Company names not found.")
        name_list = []
        data_dedup = data.drop_duplicates(subset=str(id_class))
        duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
        id_list = data_dedup[str(id_class)].tolist()
        for i in id_list:
            name_list.append(None)
            
    if id_class.upper()=='NIP':
        for nip, company_name in zip(id_list, name_list):
            nip_valid_dic, nip_invalid_dic = clean_nip_name(nip, company_name)
            if nip_valid_dic:
                id_name_valid.append(nip_valid_dic)
                valid_ids_list.append(nip)
            else:
                id_name_invalid.append(nip_invalid_dic)
                invalid_ids_list.append(nip)
    elif id_class.upper()=='REGON':
        for regon, company_name in zip(id_list, name_list):
            regon_valid_dic, regon_invalid_dic = clean_regon_name(regon, company_name)
            if regon_valid_dic:
                id_name_valid.append(regon_valid_dic)
                valid_ids_list.append(regon)
            else:
                id_name_invalid.append(regon_invalid_dic)
                invalid_ids_list.append(regon)            
    elif id_class.upper()=='KRS':
        for krs, company_name in zip(id_list, name_list):
            krs_valid_dic, krs_invalid_dic = clean_krs_name(krs, company_name)
            if krs_valid_dic:
                id_name_valid.append(krs_valid_dic)
                valid_ids_list.append(krs)
            else:
                id_name_invalid.append(krs_invalid_dic)
                invalid_ids_list.append(krs)            

    log_df = pd.DataFrame({"ValidNIP" : pd.Series(valid_ids_list),
                           "InvalidNIP" : pd.Series(invalid_ids_list),
                           "DuplicatedNIP" : pd.Series(duplicates)})
    
    args = {'arg1':len(id_name_valid),
            'arg2':id_class}
    print("{arg1} unique valid company ids detected. Chosen company id " \
          "class: {arg2}.".format(**args))
    
    if valid_ids_list < invalid_ids_list:
        print("Please assure that chosen ID class is correct")
    
    return id_name_valid, id_name_invalid, log_df

############# GET SQL DATA #####################
def get_sql_data(project_name):
    nip_name_invalid = []
    nip_name_valid = []
    valid_nip_list = []
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=cz-prgfts008;'
                          'Database=PL_FTS;'
                          'UID=pl_fts_user;'
                          'PWD=Call0fCtulu;')
    cursor = conn.cursor()

    for row in cursor.execute('select Nazwa, praw_nip, Typ from {} \
                              where praw_nip is not null \
                              UNION \
                              select Nazwa, fiz_nip, Typ from {} \
                              where praw_nip is null \
                              order by praw_nip asc, typ asc'.format(project_name, project_name)):
        nip, name = row.praw_nip, row.Nazwa
        nip_valid_dic, nip_invalid_dic = clean_nip_name(nip, name)
        if nip_valid_dic:
            nip_name_valid.append(nip_valid_dic)
            valid_nip_list.append(nip)
        else:
            nip_name_invalid.append(nip_invalid_dic)
    return nip_name_valid, nip_name_invalid, valid_nip_list

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
        nip_valid_dic[clean_nip] = '"' + name.upper() + '"' if name is not None else None
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
    
    if clean_regon==9:
        for i, j in zip(regon_factorized, weights_9):
            total += int(i)*j
    elif clean_regon==14:
        for i, j in zip(regon_factorized, weights_14):
            total += int(i)*j                
    if re.search(r"[A-Z]", regon, re.IGNORECASE) is not None and re.search("PL", regon, re.IGNORECASE) is None:
        regon_invalid_dic[regon] = name
    elif int(regon_factorized[-1]) == total % 11:
        if name is not None:
            trans = name.maketrans("-;", "  ", "'\"")
            name = name.translate(trans).strip()
            name = re.sub(r' +', " ", name)
            for form in legal_forms:
                m = re.search(unidecode(form), unidecode(name), re.IGNORECASE)
                if m:
                    name = name[:m.start()] + name[m.end():]
            name = re.sub(r' +', " ", name).strip()
        regon_valid_dic[regon] = '"' + name.upper() + '"' if name is not None else None
    else:
        regon_invalid_dic[regon] = 'n/a' if name == 'nan' else name
    return regon_valid_dic, regon_invalid_dic

def clean_krs_name(krs,name):
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
        krs_valid_dic[clean_krs] = '"' + name.upper() + '"' if name is not None else None
    else:
        krs_invalid_dic[krs] = 'n/a' if name == 'nan' else name
    return krs_valid_dic, krs_invalid_dic
############# LEGAL FORMS ##############
legal_forms = [
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SPÓŁKA KOMANDYTOWA", "Sp\.z o\.o\.",
    "P\.P\.U\.H.", "PPUH", "PRZEDSIĘBIORSTWO HANDLOWO PRODUKCYJNE", "PHU", "P\.H\.U.",
    "SPÓŁKA CYWILNA", "SPÓŁKA JAWNA", "SPÓŁKA KOMANDYTOWA", "SPÓŁKA AKCYJNA",
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
    for dic in nip_name_valid:
        for nip, name in dic.items():
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
            'startDate=' + date + '&term="' + isic + '"%20' + search + '&token=' + token
    request = Request(url, headers={'User-Agent':'Mozilla/5.0'})
    response = urlopen(request)
    data_decoded = response.read().decode('utf-8')
    return data_decoded

############## GET COMPANY INFO ###############
def get_company_info(method, nips_isics, nips_errors, session_id, output_path):
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
                      nip +
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
def parse_employees(result):
    if result['employeeNumber'] != None:
        result['NumberOfEmployees'] = result['employeeNumber']
    elif 'employeeNumberRange' in result:
        result['NumberOfEmployees'] = None
    else:
        if result['employeeNumberRange_min'] != None and result['employeeNumberRange_max'] != None:
            result['NumberOfEmployees'] = str(floor(mean([int(result['employeeNumberRange_min']), int(result['employeeNumberRange_max'])])))
        elif result['employeeNumberRange_min'] != None and result['employeeNumberRange_max'] == None:
            result['NumberOfEmployees'] = result['employeeNumberRange_min']
        elif result['employeeNumberRange_min'] == None and result['employeeNumberRange_max'] != None:
            result['NumberOfEmployees'] = result['employeeNumberRange_max']
        else:
            result['NumberOfEmployees'] = None
    
    result['FewEmployees'] = 1 if (result['NumberOfEmployees'] is not None and
        int(result['NumberOfEmployees']) <= 5) else 0 
    for k in ['employeeNumber', 'employeeNumberRange', 'employeeNumberRange_min',
    'employeeNumberRange_max', 'employeeNumberRange__type']:
        result.pop(k, None)
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
    owners_merged = ', '.join(owners_dedup)

    #result['OwnersMerged'] = owners_merged
    result['Shareholders'] = owners_merged
    result['OwnersCount'] = owners_count
    #result['OwnersInEMIS'] = owners_isics
    #result['OwnersForeign'] = owners_foreign
    
    # Drop unnecessary keys
    owners_keys_drop = []
    for col in ['_ownerCountry', '_ownerExternalId', '_ownerExternalIdClass',
    '_ownerIsic', '_ownerNameLocal', '_ownerName', '_ownerType', '_ownershipPercentage',
    '_ownershipType', '__type']:
        for key in result.keys():
            if key.startswith('ownerList_') and key.endswith(col):
                owners_keys_drop.append(key)
    for i in owners_keys_drop:
        result.pop(i, None)
    return result


################# PARSE EXECUTIVES ################
def parse_executives(result: dict) -> dict:
    # PARSE AFFILIATES
    executives_count = 0
    executives = []
    for key, value in result.items():
        if key.endswith('_executiveNameLocal'):
            executives_count += 1
            #executive = 'Name: ' + value
            #for i, j in {
            #        ', Position: ' : '_executiveUserDefinedPosition',
            #        ', Code: ' : '_executiveCode',
            #        ', GlobalCode: ' : '_globalExecutiveCode'}.items():
            #    key_processed = key[:15] + j if len(key) == 34 else key[:16] + j
            #    info = i + result[key_processed]
            #    executive += info
            executive = value
            key_processed = key[:len(key)-19] + '_executiveUserDefinedPositionLocal'
            executive += ' (' + result[key_processed] + ')'
            executives.append(executive)

    executives_dedup = list(set(executives))
    executives_merged = ', '.join(executives_dedup)

    result['ExecutivesCount'] = executives_count
    result['KeyExecutives'] = executives_merged if executives_merged.split() else 'n/a'
    #result['ExecutivesMerged'] = executives_merged if executives_merged.split() else 'n/a'

    # Drop unnecessary keys
    executives_keys_drop = []
    for col in ['_executiveCode', '_executiveNameLocal',
    '_executiveUserDefinedPosition', '_globalExecutiveCode',
    '_executiveUserDefinedPositionLocal', '_executiveName', '__type']:
        for key in result.keys():
            if key.endswith(col):
                executives_keys_drop.append(key)
    for i in executives_keys_drop:
        result.pop(i, None)
    return result


################# PARSE EXTERNAL IDS ################
def parse_external_ids(result: dict) -> dict:
    external_ids = {}
    all_ids = []
    other_ids = 0
    for key in result.keys():
        if key.startswith('externalIdList_') and key.endswith('_classCode'):
            key_processed = key[:17] + 'externalId'
            company_id = result[key] + '(' + result[key_processed] + ')'
            all_ids.append(company_id)
            if result[key] in ['PL-KRS', 'PL-REGON']:
                external_ids[result[key][3:]] = result[key_processed]
            elif result[key] == 'PL-FISCAL':
                external_ids['NIP'] = result[key_processed]
            else:
                other_ids += 1

    all_ids_dedup = list(set(all_ids))
    result['NationalFiscalIDs'] = ', '.join(all_ids_dedup)
    #external_ids['ExternalIdsOthers'] = other_ids
    #for key, value in external_ids.items():
    #    result[key] = value

    # Drop unnecessary keys
    external_ids_keys_drop = []
    for col in ['_classCode', '_externalId']:
        for key in result.keys():
            if key.endswith(col):
                external_ids_keys_drop.append(key)
    for key in external_ids_keys_drop:
        result.pop(key, None)
    return result


def parse_naics(result: dict) -> dict:
    naics_codes = []
    for key in result.keys():
        if '_naics' in key:
            code = result[key]
            value = naics_slownik[code]
            code_label = code + ' (' + value +')'
            naics_codes.append(code_label)

    naics_codes_dedup = list(set(naics_codes))
    result['Industry'] = ', '.join(naics_codes_dedup)
    
    # Drop unnecessary keys
    naics_ids_keys_drop = []
    for col in ['_naics', '_induClass', '_induCode']:
        for key in result.keys():
            if key.startswith('mainActivityList_') or key.startswith('secondaryActivityList_') and key.endswith(col):
                naics_ids_keys_drop.append(key)
    for key in naics_ids_keys_drop:
        result.pop(key, None)
    return result


################ COLS TO DROP ################
cols_drop = [
    '_type', 'affiliateList', 'auditorDate', 'auditorName', 'companyName',
    'companyLocalName', 'companySizeRevenue', 'companySizeType', 'companySizeYear',
    'description', 'descriptionLocal', 'displayName', 'dividendList', 'employeeNumberType',
    'globalLegalForm', 'mainProducts', 'latestMarketCapitalization',
    'latestMarketCapitalizationCurrency', 'mainProducts', 'mainProductsLocal',
    'outstandingSharesList', 'previousNameList', 'ratingList', 'secondaryActivityList',
    'segmentList', 'status']

############### GUIDS TO DROP  ###############

len_guids = [-34, -29, -27, -25, -24, -23, -22, -21, -20, -19, -18,
             -17, -16, -15, -14, -13, -12, -11, -10, -9, -6]

cols_guids_to_drop = [
    '__type', '_outstandingShareDate', '_outstandingShareSeriesName',
    '_outstandingShareValue', '_previousNameName', '_previousNameLocalName',
    '_previousNameChangeYear', '_ownershipType', '_ownerNameLocal', '_ownershipPercentage',
    '_affiliateExternalId', '_affiliateExternalIdClass', '_affiliateName',
    '_affiliateshipType', '_affiliateCountry', '_affiliateIsic', '_affiliateNameLocal',
    '_affiliateshipPercentage', '_dividendCurrency', '_dividendPayDate', '_dividendType',
    '_dividendValue', '_segmentName', '_segmentStockExchangeId', '_segmentStockName']

################ COKS TO DROP  ###############
cols_to_drop_list = ['address_address', 'address_city', 'address_region']

################ COKS TO RENAME ##############
output_rename = {
    'nip': 'NIP',
    'isic': 'EMISID',
    'displayNameLocal': 'CompanyName',
    'address_regionLocal': 'Województwo',
    'address_addressLocal': 'Adress',
    'address_cityLocal': 'City',
    'address_postalCode': 'PostalCode',
    'countryCode': 'Country',
    'address_url': 'Website',
    'address_email': 'EmailAdress',
    'address_fax': 'Fax',
    'address_phone': 'Phone',
    'profileUpdateDate': 'ProfileUpdateDate',
    'incorporationYear': 'IncorporationYear',
    'legalForm': 'LegalForm',
    'companyType': 'CompanyType',
    'companySizeYear' : 'CompanySizeYear',
    'employeeNumberDate': 'EmployeesNumberDate',
    'employeeNumber': 'EmployeesNumber',
    'employeeNumberRange_min': 'EmployeesNumberMin',
    'employeeNumberRange_max': 'EmployeesNumberMax',
    'registeredCapitalDate': 'RegisteredCapitalDate',
    'registeredCapitalValue': 'RegisteredCapitalValue',
    'registeredCapitalCurrency': 'RegisteredCapitalCurrency'}

################# KNOWN COLS #################
known_cols = [
    'NIP', 'EMISID', 'CompanyName', 'Data rozpoczęcia współpracy', 'Województwo',
    'Adress', 'City', 'PostalCode', 'Country', 'Website', 'EmailAdress', 'Fax',
    'Phone', 'ProfileUpdateDate', 'IncorporationYear', 'LegalForm', 'CompanyType',
    'EmployeesNumberDate', 'NumberOfEmployees', 'RegisteredCapitalDate',
    'RegisteredCapitalValue', 'RegisteredCapitalCurrency', 'KeyExecutives',
    'Shareholders', 'NationalFiscalIDs', 'Industry']

financial_data_cols_unprocessed = [
    'nip', 'Data rozpoczęcia współpracy', 'NS', 'OP', 'PERSON',
    'TS', 'NP', 'TANG', 'CE', 'SE', 'ISSUED', 'FiscalYear', 'consolidated']

financial_data_cols = [
    'emisid', 'nip', 'Data rozpoczęcia współpracy', 'NetSalesRevenue',
    'OperatingProfitEBIT', 'EmployeeBenefitExpense', 'TotalAssets',
    'NetProfitLossForThePeriod', 'PropertyPlantAndEquipment', 'CashandCashEquivalents',
    'TotalEquity', 'IssuedCapital', 'FiscalYear', 'consolidated']

accounts = ['NS', 'OP', 'PERSON', 'TS', 'NP', 'TANG', 'CE', 'SE', 'ISSUED']

cols_rename = {
    'NS':'NetSalesRevenue',
    'OP':'OperatingProfitEBIT',
    'PERSON':'EmployeeBenefitExpense',
    'TS':'TotalAssets',
    'NP':'NetProfitLossForThePeriod',
    'TANG':'PropertyPlantAndEquipment',
    'CE':'CashandCashEquivalents',
    'SE':'TotalEquity',
    'ISSUED':'IssuedCapital'}

cols_to_str = [
    'NIP', 'EMISID', 'CompanyName', 'Województwo', 'Adress', 'City', 'PostalCode',
    'Country', 'Website', 'EmailAdress', 'Fax', 'Phone', 'LegalForm', 'CompanyType',
    'RegisteredCapitalValue', 'RegisteredCapitalCurrency', 'KeyExecutives',
    'Shareholders', 'NationalFiscalIDs', 'Industry']
