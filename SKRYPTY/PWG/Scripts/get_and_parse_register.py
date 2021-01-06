"""
Script used to retrieve and parse register data from PWG API based on
getFull method and list of companies IDs. The following ID types are
allowed: NIP, REGON, KRS, PWG_ID. Processed data are exported to xlsx file
and used for investigating analysis purposes.
"""

import datetime as d
import numpy as np
import pandas as pd
import re

from pwg_ordinary import \
    get_nip_list, get_data, cols_register_keep, cols_register_rename, cols_register, \
    parse_negative, parse_negative_txt, parse_shareholders, parse_executions, \
    parse_grants, parse_dependent, parse_roles, parse_custodian, parse_uokik, \
    parse_bad_debt, parse_prohibition, parse_restriction_privilige, parse_activity, \
    parse_executives, check_pesel, get_birth_date

#################### USER PART ####################
##### DEFINE INPUT, OUTPUT FILES AND METHOD  ######
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\PWG\INPUT_API\NIP_list.xlsx'
JSONS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\GET_FULL\\'
XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_PARSE\\'

############### END OF USER PART ##################
################## DEFINE METHOD ##################
METHOD = 'getFull'

############# PARSE COLLECTED JSONS ###############
def parse_get_full(ids_jsons: dict, ids_errors: dict) -> list:
    """ Parse collected JSONs with register data and errors to DataFrame

    Parameters
    ----------
    ids_jsons : dictionary
        dictionary storing company id (key) and collected JSON (value)
    ids_errors : dictionary
        dictionary storing company id (key) and collected error (value)
        if download was not successfull

    Returns
    -------
    full_output : pd.DataFrame
        a DataFrame storing aggregated parsed register data merged with invalid output
    output : pd.DataFrame
        a DataFrame storing only valid register data correctly downloaded and parsed
    invalid_output : pd.DataFrame
        a DataFrame storing information about companies for which data could not be d
        download and error messages
    nip_finance_year : dictionary
        stores NIP of each company (key) and latest fiscal year (value) if financial data 
        is available for the company
    shareholder_press : dictionary
        stores NIP of each company (key) and list of shareholders (value) if applicable
        (only information about corporate shareholders is extracted)
    """

    result_list = []
    nip_finance_year = {}
    shareholder_press = {}
    # LOOP THROUGH COLLECTED JSONS AND PARSE TO DATAFRAME
    for company_id, table in ids_jsons.items():
        try:
            # KEEP ONLY NECESSARY COLUMNS
            result = {key: table['data'][key] for key in cols_register_keep}
            # PARSE FINANCIAL YEARS AND EXTRACT LATEST
            if result['finance_year']:
                nip_finance_year[company_id] = str(max(result['finance_year']))
            # PARSE BASIC COLUMNS FROM LIST TO STR IF CONTAIN DATA
            for col_name in ['email', 'phone', 'www', 'finance_year']:
                if result[col_name]:
                    result[col_name] = ", ".join(result[col_name]).strip()
                elif not result[col_name]:
                    result[col_name] = 'n/a'
            # PARSE NESTED FIELD
            result['Negatywne'] = parse_negative(result['negatywne'])
            result['Negatywne_txt'] = parse_negative_txt(result['negatywne_txt'])
            result['Udzialowcy'], result['Shareholders'], press_check = parse_shareholders(result['udzialowcy'])
            result['Egzekucje'] = parse_executions(result['egzekucje'])
            result['Dotacje'] = parse_grants(result['dotacje'])
            result['Zalezne'] = parse_dependent(result['zalezne'])
            result['Role'] = parse_roles(result['roles'])
            result['Executives'] = parse_executives(result['roles'])
            result['RoleHistoryczne'] = parse_roles(result['roleshistory'])
            result['RubrykaKurator'] = parse_custodian(result['rubryka_kurator'])
            result['UOKIK'] = parse_uokik(result['uokik'])
            result['Zaleglosci'] = parse_bad_debt(result['zaleglosci'])
            result['Zakazy'] = parse_prohibition(result['zakazy'])
            result['Ograniczenia'] = parse_restriction_privilige(result['ograniczenia'], 'Ograniczenie')
            result['Uprawnienia'] = parse_restriction_privilige(result['uprawnienia'], 'Uprawnienie')
            result['Aktywnosc'] = parse_activity(result['aktywnosc'])
            # ADD SHAREHOLDERS TO PRESS LIST IF APPLICABLE
            if press_check:
                shareholder_press[company_id] = press_check
            # GENERATE DATAFRAME FOR EACH COMPANY AND APPEND TO RESULT LIST
            result_df = pd.DataFrame([result])
            result_list.append(result_df)
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            ids_errors[company_id] = 'Could not parse data. Error: ' + error
    # CREATE OUTPUT DATAFRAME WITH AGGREAGATED VALID DATA FOR ALL COMPANIES
    if result_list:
        output = pd.concat(result_list, ignore_index=True, sort=False)
        output = output.rename(cols_register_rename, axis='columns')
        output = output[cols_register].sort_values(by=['NIP'], na_position='last')
    else:
        # CREATE EMPTY TABLE IF VALID OUTPUT NOT EXIST
        output = pd.DataFrame(columns=cols_register)

    # CREATE OUTPUT DATAFRAME FOR COMPANIES WITH INVALID DATA
    if ids_errors:
        invalid_output = pd.DataFrame.from_dict(ids_errors, orient='index').reset_index()
        invalid_output.columns = ['NIP', 'Error']
        invalid_output.sort_values(by=['NIP'], inplace=True, na_position='last')
    else:
        # CREATE EMPTY TABLE IF INVALID OUTPUT NOT EXIST
        invalid_output = pd.DataFrame(columns=['NIP', 'Error'])

    # MERGE AND PROCESS VALID AND INVALID OUTPUTS
    full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort=True)
    full_output.drop_duplicates(subset='NIP', keep='first', inplace=True)
    full_output = full_output[cols_register].sort_values(by=['NIP'], na_position='last')
    return full_output, output, invalid_output, nip_finance_year, shareholder_press


################# CALCULATE KRS TESTS #################
def calculate_krs_tests(collected_jsons: list):
#Risk 16 Financial statements not submitted to the National Court Register
#Risk 17 Financial statements not submitted to the National Court Register between 2015 and 2018
#Risk 18 Financial statements not available in any available paid sources
    nip_tests = {}
    ref_date = d.date.today()
    ref_fin_yrs = ['2015', '2016', '2017', '2018']
    count = 0
    for company_id, json_table in collected_jsons.items():
        tests_dict = {}
        if json_table['data']:
            table = json_table['data']
            tests_dict['Mała liczba pracowników'] = 1 if (int(table['liczba_zatrud']) > 0 and int(table['liczba_zatrud']) <= 5) else 0
            if table['kapital'] is None:
                tests_dict['Minimalny kapitał KRS'] = np.nan
                tests_dict['Wysoki kapitał KRS'] = np.nan
            else:
                tests_dict['Minimalny kapitał KRS'] = 1 if float(table['kapital']) <= 50000 else 0
                tests_dict['Wysoki kapitał KRS'] = 1 if float(table['kapital']) >= 10000000 else 0

            # testy sprawozdania finansowe
            tests_dict['Brak sprawozdan w KRS'] = 1
            tests_dict['Brak sprawozdan w w KRS (2015-18)'] = 1
            tests_dict['Brak sprawozdan w PWG'] = 1

            if (table['krs'] is None or not table['krs']):
                tests_dict['Brak sprawozdan w KRS'] = np.nan
                tests_dict['Brak sprawozdan w w KRS (2015-18)'] = np.nan
            else: 
                if table['finance_year']:
                    tests_dict['Brak sprawozdan w KRS'] = 0
                    tests_dict['Brak sprawozdan w PWG'] = 0
                    for yr in ref_fin_yrs:
                        if yr in table['finance_year']:
                            tests_dict['Brak sprawozdan w w KRS (2015-18)'] = 0
                
            # testy reprezentacja
            roles = table['roles']
            if roles:
                foreign = 0
                young = 0
                pl_count = 0
                young_pl_count = 0
                for person in roles:
                    pesel = person['pesel']
                    if not re.match('[0-9]{11}$', pesel):
                        foreign = 1
                    if check_pesel(pesel):
                        pl_count += 1
                        date_diff = (ref_date - get_birth_date(pesel)).days/365
                        if (date_diff < 25):
                            young = 1 
                            young_pl_count += 1
                young_all = 1 if (pl_count-young_pl_count == 0) else 0              

                tests_dict['Młoda osoba w reprezentacji'] = young
                tests_dict['Cała młoda reprezentacja'] = young_all
                tests_dict['Obcokrajowiec w reprezentacji'] = foreign
            else:
                tests_dict['Młoda osoba w reprezentacji'] = np.nan
                tests_dict['Cała młoda reprezentacja'] = np.nan
                tests_dict['Obcokrajowiec w reprezentacji'] = np.nan

        else:
            tests_dict['Mała liczba pracowników'] = np.nan
            tests_dict['Minimalny kapitał KRS'] = np.nan
            tests_dict['Wysoki kapitał KRS'] = np.nan
            tests_dict['Brak sprawozdan w KRS'] = np.nan
            tests_dict['Brak sprawozdan w w KRS (2015-18)'] = np.nan
            tests_dict['Brak sprawozdan w PWG'] = np.nan
            tests_dict['Młoda osoba w reprezentacji'] = np.nan
            tests_dict['Cała młoda reprezentacja'] = np.nan
            tests_dict['Obcokrajowiec w reprezentacji'] = np.nan
        nip_tests[company_id] = tests_dict
        count += 1
        
    tests_df = pd.DataFrame(nip_tests).T.reset_index().rename(columns={'index': 'CompanyID'})
    tests_df[tests_df.columns[1:]] = tests_df[tests_df.columns[1:]].apply(pd.to_numeric, errors='coerce')
    tests_df_final = tests_df.sort_values(by=['CompanyID'], na_position='last')
    print("Tests calculated for %d out of %d entities." % (count, len(collected_jsons)))
    return tests_df_final    

################ EXPORT PARSED OUTPUT #################
def export_output(parsed_register_data: list, tests_fait: pd.DataFrame):
    """ Export parsed output into separated Excel sheets in defined file

    Parameters
    ----------
    parsed_register_data : list
        list of DataFrames storing parsed register data merged with invalid output
    """

    merged_df = parsed_register_data[0].merge(tests_fait,
                                                how='left',
                                                left_on='NIP',
                                                right_on='CompanyID')

    try:
        # GET OUTPUT DATAFRAMES AND NAME THEM
        names_output_tables = {'FullOutput': parsed_register_data[0],
                               'ValidOutput': parsed_register_data[1],
                               'InvalidOutput': parsed_register_data[2],
                               'Tests': tests_fait,
                               'All': merged_df}
        # EXPORT EACH DATAFRAME TO SEPARATED SHEET WITH ACCORDING NAME
        with pd.ExcelWriter(XLSX_OUTPUT_PATH +
                            'PWG_REGISTER_' +
                            str(d.date.today()) +
                            '.xlsx') as writer:
            for name, table in names_output_tables.items():
                # EXPORT ONLY TABLE WITH DATA
                if not table.empty:
                    table.to_excel(writer, name, index=False)
    except PermissionError:
        print("Close previous output file.")
    except Exception as e:
        error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
        print("Could not export output." + error)

#################### GET OUTPUT ##################
### CREATE LIST OF COMPANY IDS FROM INPUT FILE ###
company_ids_list = get_nip_list(INPUT_FILE)
### DOWNLOAD AND COLLECT JSONS BY COMPANY IDS ####
company_ids_jsons, company_ids_errors = get_data(METHOD,
                                                 company_ids_list,
                                                 JSONS_OUTPUT_PATH)
### PARSE AND EXPORT COLLECTED JSONS ###
fait_tests = calculate_krs_tests(company_ids_jsons)
parsed_output = parse_get_full(company_ids_jsons, company_ids_errors)
export_output(parsed_output, fait_tests)
