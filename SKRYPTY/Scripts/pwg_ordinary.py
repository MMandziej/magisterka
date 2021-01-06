"""
Libary used for scripts used to retrieve data for PWG. Contain objects and
 functions which are imported to the main scripts.
"""

import datetime as dt
import json
import os
import pandas as pd
import re
import time as t

from hashlib import md5
from math import floor
from urllib.request import Request, urlopen

from keys_coded import PRIVATE_KEY, PUBLIC_KEY

########### GET NIP LIST ############

def get_nip_list(input_file):
    nip_df = pd.read_excel(input_file, header=None, names=['nip'], dtype=str)
    nip_list = nip_df['nip'].tolist()
    nip_list.sort()
    return nip_list

####### GET NIP LIST FROM TXT ########

def get_nip_txt(input_file):
    nip_list = []
    with open(input_file) as file:
        for line in file:
            nip_list.extend(line.split())
    nip_list.sort()
    return nip_list

########### GET NIP LIST ############

def get_regon_list(input_file):
    regon_df = pd.read_excel(input_file, header=None, names=['regon'], dtype=str)
    regon_list = regon_df['regon'].tolist()
    regon_list.sort()
    deduplicated_regon_list = list(set(regon_list))
    return regon_list, deduplicated_regon_list

######### GET CASEID LIST ###########

def get_regon_caseid(input_file):
    data = pd.read_excel(input_file, header=None, names=['regon', 'caseid'], dtype=str)
    regon_list = data['regon'].tolist()
    case_list = data['caseid'].tolist()
    regon_cases = dict(zip(regon_list, case_list))
    regon_cases_sorted = {}
    for key in sorted(regon_cases.keys()):
        regon_cases_sorted[key] = regon_cases[key]
    regon_list = list(regon_cases_sorted.keys())
    deduplicated_regon_list = list(set(regon_list))
    return regon_list, regon_cases_sorted, deduplicated_regon_list

########### REQUEST DATA ############

def request_data(method, company_id, fiscal_year):
    timestamp = str(floor(t.time()))
    secure_key = PRIVATE_KEY + timestamp
    secure_key_encoded = md5(secure_key.encode('utf-8')).hexdigest()
    basic = 'https://api.pwginfo.pl/?ts=' + timestamp + \
            '&key=' + PUBLIC_KEY + \
            '&sec=' + secure_key_encoded + \
            '&method='
    if method in ('getFull', 'getFirma'):
        url = basic + method + \
        '&params[]=' + company_id + \
        '&params[]=1'

    elif method == 'getFinance':
        if fiscal_year == '':
            url = basic + method + \
                '&params%5B0%5D=' + company_id
        else:
            url = basic + method + \
                '&params%5B0%5D=' + company_id + \
                '&params%5B1%5D=' + fiscal_year

    elif method in ('setUpdateFirma', 'setUpdateFinance',
                    'getLastUpdate', 'getLastDoc', 'getFinanceStatus'):
        url = basic + method + \
            '&params[]=' + company_id
    elif method == 'getCountDown':
        url = basic + method + \
            '&params[]='       

    request = Request(url, headers={'User-Agent':'Mozilla/5.0'})
    data_decoded = urlopen(request).read().decode('utf-8')
    return data_decoded

############# GET DATA ##############

def get_data(method, company_id_list, output_path, fiscal_year=''):
    json_guid = 'PWG_' + method
    company_ids_jsons = {}
    company_ids_errors = {}
    for company_id in company_id_list:
        try:
            result_decoded = request_data(method, company_id, fiscal_year)
            json_table = json.loads(result_decoded)['result']
            with open(output_path +
                      company_id +
                      '_{}.json'.format(json_guid), 'w') as file:
                json.dump(json_table, file)

            company_ids_jsons[company_id] = json_table
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            company_ids_errors[company_id] = error
            error_dict = {"nip": company_id, "error": error}

            with open(output_path +
                      company_id +
                      '_{}.json'.format(json_guid + '_INVALID'), 'w') as file:
                json.dump(error_dict, file)
    return company_ids_jsons, company_ids_errors

def get_data_register(output_path, method, nip_list):
    try:
        os.mkdir(output_path + method + '\\')
    except FileExistsError:
        print("Directory " + output_path + method + '\\' + " already exists.")

    jsons_path = output_path + method + '\\'

    json_valid_guid = 'PWG_' + method
    json_invalid_guid = 'PWG_' + method + '_INVALID'
    nips_jsons = {}
    nips_errors = {}
    for nip in nip_list:
        try:
            result_decoded = request_data(method, nip, fiscal_year='2017')
            json_table = json.loads(result_decoded)['result']
            nips_jsons[nip] = json_table

            """if method == 'getFull' or method == 'getFinance':
                with open(nip + '_{}.json'.format(json_valid_guid), 'w') as f:
                    json.dump(json_table, f)"""

            with open(jsons_path +
                      nip +
                      '_{}.json'.format(json_valid_guid), 'w') as file:
                json.dump(json_table, file)

        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            nips_errors[nip] = error
            error_dict = {"nip": nip, "error": error}

            """if method == 'getFull' or method == 'getFinance':
                with open(nip + '_{}.json'.format(json_invalid_guid), 'w') as f:
                    json.dump(error_dict, f)"""

            with open(jsons_path +
                      nip +
                      '_{}.json'.format(json_invalid_guid), 'w') as file:
                json.dump(error_dict, file)
    return nips_jsons, nips_errors

def get_data_financial(output_path, method, nip_year_dict):
    try:
        os.mkdir(output_path + method + '\\')
    except FileExistsError:
        print("Directory " + output_path + method + '\\' + " already exists.")

    jsons_path = output_path + method + '\\'

    nips_jsons = {}
    nips_errors = {}
    for nip, fiscal_year in nip_year_dict.items():
        json_valid_guid = 'PWG_' + method + fiscal_year
        json_invalid_guid = 'PWG_' + method + fiscal_year + '_INVALID'

        try:
            result_decoded = request_data(method, nip, fiscal_year)
            json_table = json.loads(result_decoded)['result']
            nips_jsons[nip] = json_table
            """if method == 'getFull' or method == 'getFinance':
                with open(nip + '_{}.json'.format(json_valid_guid), 'w') as f:
                    json.dump(json_table, f)"""

            with open(jsons_path +
                      nip +
                      '_{}.json'.format(json_valid_guid), 'w') as file:
                json.dump(json_table, file)

        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            nips_errors[nip] = error
            error_dict = {"nip": nip, "error": error}
            """if method == 'getFull' or method == 'getFinance':
                with open(nip + '_{}.json'.format(json_invalid_guid), 'w') as f:
                    json.dump(error_dict, f)"""

            with open(jsons_path +
                      nip +
                      '_{}.json'.format(json_invalid_guid), 'w') as file:
                json.dump(error_dict, file)
    return nips_jsons, nips_errors

############ FLATTEN NESTED JSONS ##############

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

############# PARSE SET UPDATE ##############

def parse_set_update(setUpdateFirma_output, log_output_path):
    regon_code_dict = {}
    for regon, table in setUpdateFirma_output[0].items():
    #for regon, table in setUpdateFirma_output.items():
        try:
            regon_code_dict[regon] = [table['data']['code'], table['data']['message']]
        except:
            regon_code_dict[regon] = ['', 'EmptyJson']

    output = pd.DataFrame.from_dict(regon_code_dict, orient='index')
    output.reset_index(level=0, inplace=True)
    output.columns = ['REGON', 'Code', 'Message']
    output.to_excel(log_output_path +
                    'SetUpdate_PARSED_' +
                    str(dt.date.today()) +
                    '.xlsx', index=False)
    return output, regon_code_dict

############# PARSE LAST UPDATE ##############

def parse_last_update(getLastUpdate_output, log_output_path):
    regon_date_dict = {}
    for regon, table in getLastUpdate_output[0].items():
    #for regon, table in getLastUpdate_output.items():
        try:
            regon_date_dict[regon] = [table['data']['last_update'],
                                      table['data']['last_doc_date']]
        except:
            regon_date_dict[regon] = ['', '']

    output = pd.DataFrame.from_dict(regon_date_dict, orient='index')
    output.reset_index(level=0, inplace=True)
    output.columns = ['REGON', 'UpdateDate', 'LL_LastDocDate']
    output.to_excel(log_output_path +
                    'LastUpdate_PARSED_' +
                    str(dt.date.today()) +
                    '.xlsx', index=False)
    return output, regon_date_dict

########### OUTPUT FINANCE COLS ############

cols_finance_keep = ['03.01', #NetSalesRevenue
                     '03.02.05', #EmployeeBenefitExpense
                     '03.06', #OperatingProfitEBIT
                     '03.14', #NetProfitLossForThePeriod
                     '01.01.02', #PropertyPlantAndEquipment
                     '01.02.03.01.03', #CashandCashEquivalents
                     '01.03', '01.05', #TotalAssets
                     '01.04.01', '01.06', #IssuedCapital
                     '01.04', '01.06.01', '01.06.51', #TotalEquity
                     '01.04.51',
                     '02.01',
                     '02.09']


cols_finance_rename = {'03.01': 'NetSalesRevenue',
                       '03.02.05': 'EmployeeBenefitExpense',
                       '03.06': 'OperatingProfitEBIT',
                       '03.14': 'NetProfitLossForThePeriod',
                       '01.01.02': 'PropertyPlantAndEquipment',
                       '01.02.03.01.03': 'CashandCashEquivalent',
                       '01.05': 'TotalAssets',
                       '01.06.51': 'TotalEquity',
                       '01.06': 'IssuedCapital'}

cols_finance = [
    'NIP', 'LastUpdate', 'NetSalesRevenue', 'OperatingProfitEBIT',
    'EmployeeBenefitExpense', 'TotalAssets', 'NetProfitLossForThePeriod',
    'PropertyPlantAndEquipment', 'CashandCashEquivalent',  'TotalEquity',
    'IssuedCapital', 'FiscalYear']

########### OUTPUT REGISTER COLS ############

cols_register_keep = [
    'krs', 'nip', 'regon', 'nazwa', 'status', 'data_zakonczenia', 'data_rejestracji',
    'forma_pr', 'adres', 'miasto', 'numer', 'lokal', 'kod_pocztowy', 'poczta', 'wojew',
    'kapital', 'liczba_zatrud', 'main_pkd', 'pkd', 'last_update', 'finance_year',
    'negatywne', 'negatywne_txt', 'phone', 'www', 'email', 'udzialowcy', 'egzekucje',
    'dotacje', 'zalezne', 'roles', 'roleshistory', 'rubryka_kurator', 'uokik',
    'zaleglosci', 'zakazy', 'ograniczenia', 'uprawnienia', 'aktywnosc'
    ]

cols_register_rename = {
    'nip': 'NIP',
    'nazwa': 'NazwaPodmiotu',
    'krs': 'KRS',
    'regon': 'REGON',
    'data_rejestracji': 'DataRejestracji',
    'status': 'Status',
    'data_zakonczenia': 'DataZakończeniaDziałalności',
    'forma_pr': 'FormaPrawna',
    'miasto': 'Miasto',
    'adres': 'Ulica',
    'numer': 'Numer',
    'lokal': 'Lokal',
    'kod_pocztowy': 'KodPocztowy',
    'poczta': 'Poczta',
    'wojew': 'Województwo',
    'kapital':'Kapitał',
    'liczba_zatrud':'LiczbaPracowników',
    'main_pkd': 'GłównaDziałalność',
    'pkd': 'DodatkoweDziałalności',
    'last_update': 'DataAktualizacji',
    'finance_year': 'LataFinansowe',
    'www': 'StronaInternetowa',
    'phone': 'Telefon',
    'email': 'Email'}

cols_register = [
    'NIP', 'NazwaPodmiotu', 'KRS', 'REGON', 'DataRejestracji', 'Status',
    'DataZakończeniaDziałalności', 'FormaPrawna', 'Miasto', 'Ulica', 'Numer', 'Lokal',
    'KodPocztowy', 'Poczta', 'Województwo', 'Kapitał', 'LiczbaPracowników',  'Executives',
    'Shareholders', 'LataFinansowe', 'GłównaDziałalność', 'DodatkoweDziałalności',
    'DataAktualizacji', 'Negatywne', 'Negatywne_txt', 'Telefon', 'StronaInternetowa',
    'Email', 'Udzialowcy', 'Egzekucje', 'Dotacje', 'Zalezne', 'Role', 'RoleHistoryczne',
    'RubrykaKurator', 'UOKIK', 'Zaleglosci', 'Zakazy', 'Ograniczenia', 'Uprawnienia',
    'Aktywnosc']

all_cols = [
    'NIP', 'NazwaPodmiotu', 'KRS', 'REGON', 'DataRejestracji', 'Status',
    'DataZakończeniaDziałalności', 'FormaPrawna', 'Miasto', 'Ulica', 'Numer', 'Lokal',
    'KodPocztowy', 'Poczta', 'Województwo', 'Kapitał', 'LiczbaPracowników',
    'GłównaDziałalność', 'DodatkoweDziałalności', 'DataAktualizacji', 'LataFinansowe',
    'Negatywne', 'Negatywne_txt', 'Telefon', 'StronaInternetowa', 'Email', 'Udzialowcy',
    'Egzekucje', 'Dotacje', 'Zalezne', 'Role', 'RoleHistoryczne', 'RubrykaKurator',
    'UOKIK', 'Zaleglosci', 'Zakazy', 'Ograniczenia', 'Uprawnienia', 'Aktywnosc',
    'FiscalYear', 'LastUpdate', 'NetSalesRevenue', 'EmployeeBenefitExpense',
    'OperatingProfitEBIT', 'NetProfitLossForThePeriod', 'PropertyPlantAndEquipment',
    'CashandCashEquivalent', 'TotalAssets', 'TotalEquity', 'IssuedCapital'
    ]

cols_to_str = [
    'NIP', 'NazwaPodmiotu', 'KRS', 'REGON', 'Status', 'FormaPrawna', 'Miasto', 'Ulica',
    'Numer', 'Lokal', 'KodPocztowy', 'Poczta', 'Województwo', 'GłównaDziałalność',
    'DodatkoweDziałalności', 'DataAktualizacji', 'LataFinansowe', 'Negatywne',
    'Negatywne_txt', 'Telefon', 'StronaInternetowa', 'Email', 'Udzialowcy', 'Egzekucje',
    'Dotacje', 'Zalezne', 'Role', 'RoleHistoryczne', 'RubrykaKurator', 'UOKIK',
    'Zaleglosci', 'Zakazy', 'Ograniczenia', 'Uprawnienia', 'Aktywnosc', 'LastUpdate'
    'Executives', 'Shareholders']

######### PARSE RESGISTER NESTED FIELDS ###########
############# NEGATYWNE #############
def parse_negative(negative_field):
    if isinstance(negative_field, dict):
        company_negative = ', '.join(['{} - {}'.format(k, v) for k, v in negative_field.items()])
    elif not negative_field:
        company_negative = 'n/a'
    return company_negative

############ NEGATYWNE TXT ###########
def parse_negative_txt(negative_txt_field):
    if not negative_txt_field:
        company_negative_txt = 'n/a'
    else:
        if isinstance(negative_txt_field, list):
            company_negative_txt = ", ".join(negative_txt_field).strip()
        elif isinstance(negative_txt_field, dict):
            company_negative_txt = ", ".join(str(value) for value in negative_txt_field.values())     
        else:
            company_negative_txt = 'n/a'
    return company_negative_txt
############# UDZIALOWCY #############
def parse_shareholders(shareholders_field):
    fait_shareholders = []
    company_shareholders = []
    company_press = []
    shareholders_krs = []
    if shareholders_field:
        for field in shareholders_field:
            if field['typ'] == 'firma':               
                full = field['nazwa'] + \
                    ' (' + str(field['wartosc']) + ' PLN - ' + field['procent'] + '%)'
                company_press.append(field['nazwa'])
                fait_shareholders.append(full)
            elif field['typ'] == 'niezarejestrowani':
                full = field['nazwa'] + \
                    ' (' + str(field['wartosc']) + ' PLN - ' + field['procent'] + '%)'
                fait_shareholders.append(full)
            elif field['typ'] == 'person':
                full = field['imie'] + ' ' + field['nazwa'] + \
                    ' PESEL: ' + field['pesel'] + \
                    ' (' + str(field['wartosc']) + \
                    ' PLN - ' + field['procent'] + '%)'
                owner_person = field['imie'] + ' ' + field['nazwa'] + \
                    ' (' + str(field['wartosc']) + \
                    ' PLN - ' + field['procent'] + '%)'
                fait_shareholders.append(owner_person)
            company_shareholders.append(full)
    else:
        company_shareholders.append('n/a')
    company_shareholders = ', '.join(company_shareholders)
    fait_shareholders_merged = ', '.join(fait_shareholders)
    return company_shareholders, fait_shareholders_merged, company_press

############# EGZEKUCJE #############
def parse_executions(executions_field):
    company_executions = []
    if executions_field:
        if isinstance(executions_field['egzekucje_nazwa_data_sygnatura'], dict):
            for value in executions_field['egzekucje_nazwa_data_sygnatura'].values():
                company_executions.append(value)
        if isinstance(executions_field['egzekucje_nazwa_data_sygnatura'], list):
            if executions_field['egzekucje_nazwa_data_sygnatura']:
                for field in executions_field['egzekucje_nazwa_data_sygnatura']:
                    company_executions.append(field)
            else:
                company_executions.append('n/a')
    else:
        company_executions.append('n/a')
    company_executions = (', '.join(company_executions))
    return company_executions

############# DOTACJE #############
def parse_grants(grants_field):
    company_grants = []
    if grants_field:
        for field in grants_field:
            full = 'Title: ' + field['title'] + \
                ', TotalAmount: ' + field['amount'] + \
                ', GrantAmount: ' + field['amount_grant'] + \
                ', StartDate: ' + field['started'] + \
                ', EndDate: ' + field['finished']
            company_grants.append(full)
    else:
        company_grants.append('n/a')
    company_grants = (', '.join(company_grants))
    return company_grants

############# ZALEZNE #############
def parse_dependent(dependent_field):
    company_dependent = []
    if dependent_field:
        for field in dependent_field:
            full = field['nazwa'] + ' (' + field['nip'] + ') ' + \
                ', Involvement: ' + field['wartosc'] + \
                ' (' + field['procent'] + '%)'
            company_dependent.append(full)
    else:
        company_dependent.append('n/a')
    company_dependent = (', '.join(company_dependent))
    return company_dependent

############# ROLES AND HISTORY ROLES #############
def parse_roles(roles_field):
    company_roles = []
    if roles_field:
        for field in roles_field:
            full = 'StartDate: ' + field['start'] + \
                ', EndDate: ' + field['koniec'] + \
                ', Names: ' + field['name'] +\
                ', Surname: ' + field['surname'] + \
                ', PESEL: ' + field['ident'] + \
                ', Rola: ' + field['rola'] + \
                ', Rola2: ' + field['rola2'] + \
                ', pstan: ' + field['pstan']
            company_roles.append(full)
    else:
        company_roles.append('n/a')
    company_roles = (', '.join(company_roles))
    return company_roles

############# ROLES AND HISTORY ROLES #############
def parse_executives(roles_field):
    ref_date = dt.date.today()
    executives = []
    if roles_field:
        for field in roles_field:
            start_date = dt.date.fromisoformat(field['start'])
            end_date = dt.date.fromisoformat(field['koniec'])
            if ref_date > start_date and ref_date < end_date: 
                person = field['name'] + ' ' + field['surname'] + ' (' + field['rola'] + ')'
            executives.append(person)
    else:
        executives.append('n/a')
    executives_merged = (', '.join(executives))
    return executives_merged

############# KURATOR #############
def parse_custodian(custodian_field):
    company_custodian = []
    if custodian_field:
        for field in custodian_field:
            kurator = 'KuratorKRS: ' + field['kurator_krs'] if field['kurator_krs'] is not None else 'KuratorKRS: Unknown'
            end_date = ', EndDate: ' + field['kurator_data_koniec'] if field['kurator_data_koniec'] is not None else ', EndDate: Current'
            full = kurator + ', StartDate: ' + \
                field['kurator_data_powolania'] + \
                end_date + ', PodstawaZakres: ' + field['kurator_podstawa_zakres']
            company_custodian.append(full)
    else:
        company_custodian.append('n/a')
    company_custodian = (', '.join(company_custodian))
    return company_custodian

############# UOKIK #############
def parse_uokik(uokik_field):
    company_uokik = []
    if uokik_field:
        for field in uokik_field:
            full = 'Date: ' + field['data'] + \
                ', Kara: ' + field['kara'] + \
                ', Odwolanie: ' + field['odwolanie']
            company_uokik.append(full)
    else:
        company_uokik.append('n/a')
    company_uokik = (', '.join(company_uokik))
    return company_uokik

############# ZALEGLOSCI #############
def parse_bad_debt(bad_debt_field):
    company_debt = []
    if bad_debt_field:
        for field in bad_debt_field.values():
            full = 'Type: ' + field['zaleglosci_charakter'] + \
                ', Creditor: ' + field['zaleglosci_organ'] + \
                ', Amount: ' + field['zaleglosci_wysokosc']
            end_date = ', EndDate: ' + field['zaleglosci_zakonczenie'] if field['zaleglosci_zakonczenie'] is not None else ', EndDate: Current'
            company_debt.append(full + end_date)
    else:
        company_debt.append('n/a')
    company_debt = (', '.join(company_debt))
    return company_debt

############# ZAKAZY #############
def parse_prohibition(prohibition_field):
    company_prohibition = []
    if prohibition_field:
        for field in prohibition_field['InformacjaOZakazie']:
            full = 'DataUprawomocnieniaOrzeczenia: ' + field['DataUprawomocnieniaOrzeczenia'] + \
                ', DataWydaniaOrzeczenia: ' + field['DataWydaniaOrzeczenia'] +\
                ', Nazwa: ' + field['Nazwa'] + \
                ', OkresNaJakiZostalOrzeczonyZakaz: ' + field['OkresNaJakiZostalOrzeczonyZakaz'] + \
                ', Opis: ' + field['Opis'] + \
                ', Typ: ' + field['Typ'] + \
                ', ZakazWydal: ' + field['ZakazWydal']
            company_prohibition.append(full)
    else:
        company_prohibition.append('n/a')
    company_prohibition = (', '.join(company_prohibition))
    return company_prohibition

############# OGRANICZENIA / UPRAWNIENIA #############
def parse_restriction_privilige(parsed_field, guid):
    company_privilige = []
    if parsed_field:
        for field in parsed_field[guid]:
            company_privilige.append(field)
    else:
        company_privilige.append('n/a')
    company_privilige = (', '.join(company_privilige))
    return company_privilige

############# AKTYWNOSC ##############
def parse_activity(activity_field):
    company_activity = []
    if activity_field:
        for field in activity_field:
            company = 'Nazwa: ' + field['nazwa'] + \
                ' (NIP: ' + field['nip'] + ')' + \
                ', Type: ' + field['rola2']
            amount = ', Wartosc: ' + field['wartosc'] if field['wartosc'] is not None else ' ,Wartosc: Unknown'
            timeline = ', StartDate: ' + field['start'] + \
                ', EndDate: ' + field['koniec']
            company_activity.append(company + amount + timeline)
    else:
        company_activity.append('n/a')
    company_activity = (', '.join(company_activity))
    return company_activity

################ PESELE ##################
def check_pesel(pesel):
    #Sprawdzanie regexem
    if (re.match('[0-9]{11}$', pesel)):
        pass
    else:
        return False
    # Sprawdzenie sumy kontrolnej...
    l = int(pesel[10])
    suma = ((l*int(pesel[0]))+(3*int(pesel[l]))+(7*int(pesel[2]))+(9*int(pesel[3]))+((l*int(pesel[4])))+(3*int(pesel[5]))+(7*int(pesel[6]))+(9*int(pesel[7]))+(l*int(pesel[8]))+(3*int(pesel[9])))
    kontrolka = 10 - (suma % 10)
    if kontrolka == 10:
        kontrolka = 0
    else:
        kontrolka = kontrolka
    
    #kontrolka i sprawdzenie zgodnosci
    if (kontrolka == 10 or kontrolka == 0):
        return False
    else:
        return True

def get_birth_date(pesel):
    r = int(pesel[0:2])
    m = pesel[2:4]
    d = pesel[4:6]
    # sprawdzamy rok urodzenia
    if (r <= 99 and r > 10):
        pr = 1900
    else:
        pr = 2000
    return dt.date.fromisoformat(str(pr+r) + '-' + m + '-' + d)
