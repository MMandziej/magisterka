"""
Script used as library for importing objects and functions to main scripts
which are used to retrieve and parse data from EMIS API.

Data are processed and exported and used for investigating
analysis purposes.
"""

from datetime import date, datetime
import json
import numpy as np
import pandas as pd
import pyodbc
import re
import ssl
import time as t

from copy import deepcopy
from fake_useragent import UserAgent
from math import floor, ceil
from random import randint
from statistics import mean
from time import sleep
from unidecode import unidecode
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

######### GET NIP NAME LIST  ###########
def get_nip_name(input_file, id_class):
    valid_ids_list = []
    invalid_ids_list = []
    valid_ids_keys = []

    data = pd.read_excel(input_file, dtype=str, header=None)
    if len(data.columns)==2:
        data.columns=[str(id_class), 'NumeryRachunków']
        data_dedup = data.drop_duplicates(subset=str(id_class))
        duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
        id_list = data_dedup[str(id_class)].tolist()
        name_list = data_dedup['NumeryRachunków'].tolist()

    elif len(data.columns)== 1:
        data.columns=[str(id_class)]
        print("Account numbers not found.")
        name_list = []
        data_dedup = data.drop_duplicates(subset=str(id_class))
        duplicates = list(set([i for i in data[str(id_class)].tolist() if
                               data[str(id_class)].tolist().count(i) > 1]))
        id_list = data_dedup[str(id_class)].tolist()

    if id_class.upper()=='NIP':
        for nip in id_list:
            nip_valid, nip_invalid = clean_nip_name(nip)
            if nip_valid:
                valid_ids_list.append(nip)
            else:
                invalid_ids_list.append(nip)

    elif id_class.upper()=='REGON':
        for regon in id_list:
            regon_valid, regon_invalid = clean_regon_name(regon)
            if regon_valid:
                valid_ids_list.append(regon)
            else:
                invalid_ids_list.append(regon)

    log_df = pd.DataFrame({"ValidNIP" : pd.Series(valid_ids_list),
                           "InvalidNIP" : pd.Series(invalid_ids_list),
                           "DuplicatedNIP" : pd.Series(duplicates)})

    ### GET NIPS AND ACCOUNTS ###
    valid_ids_accounts = {}
    if name_list:
        for company_id, acc_nums in zip(id_list, name_list):
            if acc_nums == 'nan':
                valid_ids_accounts[company_id] = None
            else:
                valid_ids_accounts[company_id] = acc_nums.replace(" ", "").split(",")

    args = {'arg1':len(valid_ids_list),
            'arg2':id_class}
    print("{arg1} unique valid company ids detected. Chosen company id " \
          "class: {arg2}.".format(**args))

    if valid_ids_list < invalid_ids_list:
        print("Please assure that chosen ID class is correct")
        
    ### DIVIDE INPUT INTO BATCHES ###
    for i in valid_ids_list:
        valid_ids_keys.append(i)

    sliced_valid_ids_list = []
    start_param = 0
    if len(valid_ids_keys) >= 30:
        end_param = 30
        if len(valid_ids_keys) < 300:
            print("Input shall be divided into %s batches." % ceil(len(valid_ids_keys)/30))
        else:
            print("""Input shall be divided into {} batches.
                  Warning: According to doccumentation input to big to collect all data.
                  Please downsize to 300 entites at most.""".format(ceil(len(valid_ids_keys)/30)))
    else:
        end_param = len(valid_ids_keys)
        sliced_valid_ids_list.append(','.join(valid_ids_keys[start_param:end_param]))

    while len(valid_ids_keys) > end_param:
        sliced_ids = ','.join(valid_ids_keys[start_param:end_param])
        sliced_valid_ids_list.append(sliced_ids)
        start_param += 30
        if len(valid_ids_keys) - end_param <= 30:
            end_param = len(valid_ids_keys)
            sliced_ids = ','.join(valid_ids_keys[start_param:end_param])
            sliced_valid_ids_list.append(sliced_ids)
            print("Input successfully divided into {} batches.".format(len(sliced_valid_ids_list)))
            break
        else:
            end_param += 30
    return sliced_valid_ids_list, invalid_ids_list, log_df, valid_ids_accounts

############ CLEAN_NAME_NIP ###################
def clean_nip_name(nip):
    nip_invalid_list = []
    nip_valid_list = []
    total = 0
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    clean_nip = re.sub(r'[A-Z]', "", nip)
    nip_factorized = list(clean_nip)
    for i, j in zip(nip_factorized, weights):
        total += int(i)*j
    if re.search(r"[A-Z]", nip, re.IGNORECASE) is not None and re.search("PL", nip, re.IGNORECASE) is None:
        nip_invalid_list.append(nip)
    elif int(nip_factorized[-1]) == total % 11 and len(clean_nip) == 10:
        nip_valid_list.append(clean_nip)
    else:
        nip_invalid_list.append(nip)
    return nip_valid_list, nip_invalid_list

def clean_regon_name(regon):
    regon_valid_list = []
    regon_invalid_list = []
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
        regon_invalid_list.append(regon)
    elif int(regon_factorized[-1]) == total % 11:
        regon_valid_list.append(regon)
    else:
        regon_invalid_list.append(regon)
    return regon_valid_list, regon_invalid_list

################# REQUEST DATA ################
def request_data(id_class, company_ids_list):
    #ua = UserAgent()
    #browser_client = str(ua.random)
    class_lower = id_class.lower()
    td = str(date.today())
    url = 'https://wl-api.mf.gov.pl/api/search/' + class_lower + 's/' + company_ids_list + '/?date=' + td
    # request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # request = Request(url, headers={'User-Agent': browser_client})
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
    response = urlopen(request)
    data_decoded = response.read().decode('utf-8')
    return data_decoded


############### GET VAT STATUS ################
def get_vat_status(id_class, company_ids, output_path):
    json_guid = 'VATCHECK'
    nips_jsons = {}
    nips_errors = {}
    ssl._create_default_https_context = ssl._create_unverified_context
    for i, batch_list in enumerate(company_ids):
        try:
            requests_limit = 0
            result_decoded = request_data(id_class, batch_list)
            json_table = json.loads(result_decoded)['result']['subjects']
            with open(output_path + str(i+1) + '_{}_'.format(json_guid) + str(date.today()) + '.json', 'w') as file:
                json.dump(json_table, file)
            nips_jsons[str(i+1)] = json_table
            # try to workaround limit using sleep 
            #sleep(randint(5, 15))
            #print(randint(5, 15))

        except (TimeoutError, URLError, ConnectionAbortedError) as exc:
            error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
            print("For: ", str(i), str(exc))
            error_dict = {id_class : 'n/a', "error" : error}
            with open(output_path + str(i+1) + '_{}_'.format(json_guid + 'INVALID_') + str(date.today()) + '.json', 'w') as file:
                json.dump(error_dict, file)
            requests_limit += 1

            while requests_limit < 3:
                try:
                    result_decoded = request_data(id_class, batch_list)
                    json_table = json.loads(result_decoded)['result']['subject']
                    with open(output_path + str(i+1) + '_{}_'.format(json_guid) + str(date.today()) + '.json', 'w') as file:
                        json.dump(json_table, file)
                    nips_jsons[str(i+1)] = json_table
                except Exception:
                    requests_limit += 1

        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            print(str(e))
            nips_errors[str(i+1)] = error
            error_dict = {id_class : 'n/a', "error": error}
            with open(output_path + str(i+1) + '_{}_'.format(json_guid + '_INVALID_') + str(date.today()) + '.json', 'w') as file:
                json.dump(error_dict, file)

    collected_nips_count = 0
    for v in nips_jsons.values():
        collected_nips_count += len(v)
    print("VAT status successfully checked for %s companies." % collected_nips_count)
    return nips_jsons, nips_errors


def parse_vat_status(collected_jsons: dict,
                     collected_errors: dict,
                     all_nips: list,
                     client_nips_accounts: dict) -> tuple:
    """ Parse splitted JSONs with register data and errors to list od dicts

    Parameters
    ----------
    collected_jsons : list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    collected_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data

    Returns
    -------
    result_list: list
        a list storing dictionaries with register data for companies
    collected_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data
    """

    # Companies unavailable are treated as not register for VAT
    jsons_all = deepcopy(collected_jsons)
    uncollected_ids = list(set(all_nips) - set(list(jsons_all.keys())))
    for i in uncollected_ids:
        jsons_all[i] = {'nip': i, 'statusVat': 'Niezarejestrowany'}
        for key in initial_cols:
            if key not in jsons_all[i]:
                jsons_all[i].update({key: None})

    result_list = []
    entities_accs = {}
    # Iterate over dictionary {NIP: JSON}
    count = 0
    for company_id, json_table in jsons_all.items():
        try:
            table = deepcopy(json_table)
            flag = np.nan
            for k, v in table.copy().items():
                if isinstance(v, list) and not v:
                    table[k] = ''

                elif isinstance(v, list) and not v and k == 'accountNumbers':
                    if client_nips_accounts.get(company_id, None) is not None:
                        flag = 0

                elif isinstance(v, list) and v and k == 'accountNumbers':
                    entities_accs[company_id] = table[k]
                    table[k] = ', '.join(v)
                    if client_nips_accounts.get(company_id, None) is not None:
                        flag = 0
                        for client_acc in client_nips_accounts[company_id]:
                            if client_acc not in table[k]:
                                flag = 1

                elif isinstance(v, list) and v and k in [
                        'representatives', 'partners', 'authorizedClerks']:
                    for entity in v:
                        for i in list(entity.keys()):
                            if i == 'companyName' and entity[i] is None:
                                entity.pop('companyName', None)
                                entity.pop('nip', None)
                                entity['Imie'] = entity.pop('firstName')
                                entity['Nazwisko'] = entity.pop('lastName')
                                entity['PESEL'] = entity.pop('pesel')
                                if entity['PESEL'] is None:
                                    entity['PESEL'] = 'Nie podano'
                            elif i == 'companyName' and entity[i] is not None:
                                entity.pop('firstName', None)
                                entity.pop('lastName', None)
                                entity.pop('pesel', None)
                                entity['Nazwa'] = entity.pop('companyName')
                                entity['NIP'] = entity.pop('nip')
                                if entity['NIP'] is None:
                                    entity['NIP'] = 'Nie podano'
                            vs = ', '.join('{}: {}'.format(i, j) for i, j in entity.items())
                            table[k] = vs
            table['IncorrectAccountsDetected'] = flag
            table['hasVirtualAccounts'] = 1 if table['hasVirtualAccounts'] else 0
            table['RiskyRemovalBasis'] = score_removal_reason(table['removalBasis'])
            table['EntityListedInVATRegistry'] = 1 if company_id not in uncollected_ids else 0
            table['CheckDate'] = date.today()
            # table['RemovedBefore1MonthAgo'] = calculate_removal_datediff(table['removalDate'], 30)
            # table['RemovedBefore3MonthsAgo'] = calculate_removal_datediff(table['removalDate'], 90)
            # table['RemovedBefore6MonthsAgo'] = calculate_removal_datediff(table['removalDate'], 180)
            # able['RemovedBefore12MonthsAgo'] = calculate_removal_datediff(table['removalDate'], 365)

            result_df = pd.DataFrame([table])
            result_df.rename(columns=cols_rename, inplace=True)
            result_df = result_df[known_cols]
            result_list.append(result_df)
            count += 1 
            print('Parsing ', str(count), 'out of ', len(jsons_all))
        except Exception as exc:
            # Append existing list of errors
            error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
            collected_errors[company_id] = error
    print("Data successfully parsed for %s companies." % len(result_list))
    return result_list, collected_errors, entities_accs


#### CALCULATE DATEDIFFF ####
def calculate_removal_datediff(removal_date, days):
    if removal_date is None:
        return 0
    elif removal_date is not None:
        datediff = (datetime.now() - datetime.strptime(removal_date, '%Y-%m-%d')).days
        if datediff < days:
            score = 1
        else:
            score = 0
        return score


def score_removal_reason(removal_reason):
    removal_reasons = {
        "Art. 96 ust. 6-8": 0, # NatualReason
        "Art. 96 ust. 9": 1,
        "Art. 96 ust. 9 pkt 1": 1,
        "Art. 96 ust. 9 pkt 2": 1, #Potentially
        "Art. 96 ust. 9 pkt 3": 2,
        "Art. 96 ust. 9 pkt 4": 2,
        "Art. 96 ust. 9 pkt 5": 4, # Fraudulent
        "Art. 96 ust. 9 pkt 6": 4, # 
        "Art. 96 ust. 9a pkt 1": 0,
        "Art. 96 ust. 9a pkt 2": 2.5, # LikelyFraudulent
        "Art. 96 ust. 9a pkt 3": 1,
        "Art. 96 ust. 9a pkt 4": 3, # LikelyFraudulent
        "Art. 96 ust. 9a pkt 5": 3}

    score = None
    if removal_reason is not None:
        for reason, score_result in removal_reasons.items():
            if removal_reason == reason:
                score = score_result
    return score


def slice_export_jsons(collected_jsons: dict, output_path: str) -> dict:
    """ Split collected JSONs with data collected for single batches into single JSONs with data for single company each
     and export to output directory.

    Parameters
    ----------
    collected_jsons: list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    output_path: string
        a directory to which splitted JSONs are to be exported

    Returns
    -------
    single_jsons : dictionary(company_id : json_table)
        a dictionary storing company ID (key) and JSON dictionary (value) parsed from merged JSONs
    """

    single_jsons = {}
    for jsons_list in collected_jsons.values():
        for json_file in jsons_list:
            company_id = json_file["nip"]
            with open(output_path + company_id + '_VATCHECK_' + str(date.today()) + '.json', 'w') as file:
                json.dump(json_file, file)
                single_jsons[company_id] = json_file
    print("Collected data successfully sliced and exported into separated files (%s files)." % len(single_jsons))
    return single_jsons


def check_shared_accs(nips_accounts: dict) -> tuple:
    """ Split collected JSONs with data collected for single batches into single JSONs with data for single company each
     and export to output directory.

    Parameters
    ----------
    nips_accounts : dict (str: list)
        a dictionary storing company id (key) and bank accounts numbers (as a list) assigned to the company (value).
        Object stores only companies which do have accounts numbers assigned.

    Returns
    -------
    all_accs_list : list (of dicts)
        a dictionary storing company ID (key) and JSON dictionary (value) parsed from merged JSONs
    shared_accs : list (of strings)
        list storing bank accounts number which are shared by at least two entities which may indicate fraud
    """

    result_list = []
    all_accs_list = []
    for company_id, acc_list in nips_accounts.items():
        for acc in acc_list:
            all_accs_list.append(acc)
            acc_company_id = {}
            acc_company_id.update(acc=company_id)
            result_list.append(acc_company_id)

    shared_accs = list(set([acc for acc in all_accs_list if all_accs_list.count(acc) > 1]))
    return all_accs_list, shared_accs


def create_output(result_list: list, parsed_errors: dict) -> tuple:
    """ Create output tables in pandas DataFrames from parsed JSONs and format it to further export

    Parameters
    ----------
    result_list: list(of dicts)
         list of parsed dictionaries storing processed register data prepared
         for output
    parsed_errors: dictionary
        a dictionary storing NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data and parsing JSONS

    Returns
    -------
    full_output: pd.DataFrame
        a DataFrame storing aggregated both valid nad ivalid collected register data
    output : pd.DataFrame
        a DataFrame storing only valid collected register data
    invalid_output: pd.DataFrame
    a DataFrame storing errors collected while collecting EMIS IDs / JSONS and
    parsing register data
    """

    if result_list:
        # Concat all rows into output table
        output = pd.concat(result_list, ignore_index=True, sort=False)
        output = output.sort_values(by=['NIP'], na_position='last')
    else:
        # Create empty DataFrame if there is no valid output
        output = pd.DataFrame(columns=known_cols)

    # Fill null values and change type of columns

    str_cols = ['CompanyName', 'NIP', 'REGON', 'KRS', 'PESEL', 'StatusVAT', 'AccountNumbers',
                'AddressResidence', 'AdressWorking', 'Reprezentacja', 'Proxy', 'AuthorizedClerks',
                'RegistrationLegalDate', 'RegistrationDenialDate', 'RegistrationDenialBasis',
                'RemovalDate', 'RemovalBasis', 'RestorationDate', 'RestorationBasis']
    num_cols = [
        'EntityListedInVATRegistry', 'IncorrectAccountsDetected', 'VirtualAccountsPresence', 'RiskyRemovalBasis']
    # output[str_cols] = output[str_cols].astype(str)
    output[num_cols] = output[num_cols].apply(pd.to_numeric, errors='ignore')

    if parsed_errors:
        # Create DataFrame from list of errors
        invalid_output = pd.DataFrame.from_dict(parsed_errors, orient='index').reset_index()
        invalid_output.columns = ['NIP', 'Error']
        invalid_output.sort_values(by=['NIP'], inplace=True, na_position='last')
        # Merge both outputs
        full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort=True)
        full_output.drop_duplicates(keep='first', subset='NIP', inplace=True)
        full_output.reset_index(drop=True)
        full_output = full_output[known_cols].sort_values(by=['NIP'], na_position='last')
    else:
        # Create empty DataFrame if there is no valid output
        invalid_output = pd.DataFrame(columns=[known_cols]).reset_index(drop=True)
        full_output = output
    print("Output successfully created.")
    return full_output, output, invalid_output


def export_output(output_parsed: pd.DataFrame, log_df: pd.DataFrame, output_path: str):
    """ Split parsed register data into separated tables and
    export each into Excel sheet in defined file. Exports also EMIS_input table
    which is later used for FAIT purposes.

    Parameters
    ----------
    output_parsed : pd.DataFrame
        a DataFrame storing aggregated parsed financial data merged with invalid output

    """

    try:
        output_list = [i for i in output_parsed]
        sheet_names = ['FullOutput', 'ValidOutput', 'InvalidOutput']

        with pd.ExcelWriter(output_path + 'VATCHECK_' + str(date.today()) + '.xlsx') as writer:
            for sheet_name, table in zip(sheet_names, output_list):
                table.to_excel(writer, sheet_name, index=False)
            log_df.to_excel( writer, sheet_name="LOG", index=False)
        print("Output successfully exported to declared location: " + output_path[:-2])
    except PermissionError:
        print("Close previous output file.")
    except Exception as exc:
        # Raise exception and print Error if export unsuccessful
        error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
        print(error)


def export_vatcheck_to_sql(project_name: str,
                           creds: str,
                           vatchek_output: pd.DataFrame) -> str:
    """ Export previously collected financial data to SQL Database

    Parameters
    ----------
    project_name: string
        Name of the project imported from directories file,
        also used as a schema name in the SQL
    creds: string
        Credentials used to connect with the SQL DB,
        imported from encoded text file in keys_coded file
    vatchek_output: DataFrame
        Pandas module dataframe containing EMIS-structure financial output

    Returns
    -------
    table_name : name of the table object in SQL DB the data has been saved to
    """

    # TODO: testowanie;
    # zrobienie bardziej eleganckiego insert statement (translation table?);

    conn = pyodbc.connect(creds)
    cursor = conn.cursor()  # Establish connection with the database
    table_name = "%s.vat_whitelist" % project_name

    # If project schema does not exist - create it
    create_schema_statement = ("IF NOT EXISTS (SELECT schema_name FROM information_schema.schemata"
                               " WHERE schema_name = '{0}') BEGIN EXEC"
                               " sp_executesql N'CREATE SCHEMA {0}' END").format(project_name)

    create_table_statement = ("IF NOT(EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE "
                              "TABLE_SCHEMA = '{}' AND TABLE_NAME = 'vat_whitelist'))"
                              "SELECT * INTO {} FROM dbo.vat_whitelist_template".format(project_name,
                                                                                        table_name))
    cursor.execute(create_schema_statement)
    try:
        cursor.execute(create_table_statement)
    except pyodbc.ProgrammingError:
        print("Table {} already exists." % table_name)
    cursor.commit()

    sql_cols = ['CompanyName', 'NIP', 'REGON', 'KRS', 'PESEL', 'EntityListedInVATRegistry', 'StatusVAT',
                'VirtualAccountsPresence',	'AddressResidence',	'AddressWorking', 'Representatives', 'Proxy',
                'AuthorizedClerks', 'RegistrationLegalDate', 'RegistrationDenialDate', 'RegistrationDenialBasis',
                'RemovalDate', 'RemovalBasis', 'RiskyRemovalBasis', 'RestorationDate', 'RestorationBasis', 'CheckDate']

    sql_output = vatchek_output[sql_cols[:]]
    insert_values_list = []
    for num, a in sql_output.iterrows():
        single_insert_list = [x for x in sql_output.loc[num]]
        list_to_str = "', '".join(str(elem) for elem in single_insert_list)
        single_values = "('{}')".format(list_to_str)
        single_values = single_values.replace(", 'nan'", ", NULL").replace("'None'", "NULL").replace(", ''", ", NULL").replace(".0'", "'")
        insert_values_list.append(single_values)

    insert_values = ", \n".join(str(val) for val in insert_values_list)
    all_cols = ", ".join('[' + str(header) + ']' for header in sql_output)
    insert_statement = "INSERT INTO {} ({}) VALUES {}".format(table_name, all_cols, insert_values)
    try:
        cursor.execute(insert_statement)
    except pyodbc.ProgrammingError:
        print("Could not insert values into {} table." % table_name)
    cursor.commit()
    return table_name, insert_statement


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

initial_cols = ['accountNumbers', 'authorizedClerks', 'hasVirtualAccounts',
    'krs', 'name', 'nip', 'partners', 'pesel', 'registrationDenialBasis',
    'registrationDenialDate', 'registrationLegalDate', 'regon',
    'removalBasis', 'removalDate', 'representatives', 'residenceAddress',
    'restorationBasis', 'restorationDate', 'workingAddress']

cols_rename = {
    'accountNumbers': 'AccountNumbers',
    'authorizedClerks': 'AuthorizedClerks',
    'hasVirtualAccounts': 'VirtualAccountsPresence',
    'krs': 'KRS',
    'name': 'CompanyName',
    'nip': 'NIP',
    'partners': 'Proxy',
    'pesel': 'PESEL',
    'registrationLegalDate': 'RegistrationLegalDate',
    'registrationDenialBasis': 'RegistrationDenialBasis',
    'registrationDenialDate': 'RegistrationDenialDate',
    'regon': 'REGON',
    'removalBasis': 'RemovalBasis',
    'removalDate': 'RemovalDate',
    'representatives': 'Representatives',
    'residenceAddress': 'AddressResidence',
    'restorationBasis': 'RestorationBasis',
    'restorationDate': 'RestorationDate',
    'statusVat':'StatusVAT',
    'workingAddress':'AddressWorking'}

known_cols = [
    'CompanyName', 'NIP', 'REGON', 'KRS', 'PESEL', 'EntityListedInVATRegistry', 
    'StatusVAT', 'AccountNumbers', 'IncorrectAccountsDetected', 'VirtualAccountsPresence',
    'AddressResidence', 'AddressWorking', 'Representatives', 'Proxy', 'AuthorizedClerks',
    'RegistrationLegalDate', 'RegistrationDenialDate', 'RegistrationDenialBasis',
    'RemovalDate', 'RemovalBasis', 'RiskyRemovalBasis', 'RestorationDate', 'RestorationBasis', 'CheckDate']
