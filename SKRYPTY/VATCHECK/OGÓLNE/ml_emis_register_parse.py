"""
Script used to parse register data collected from EMIS API based on
getFullCompany method. Data is processed and used to predict probability of
companies' bankruptcy.
"""

import datetime as d
import json
import os
import pandas as pd
import re

from ml_help import \
    flatten_json, parse_affiliates, parse_employees, parse_dividends, \
    parse_executives, parse_external_ids, parse_naics, parse_outstanting_shares, \
    parse_owners, parse_previous_names, parse_segment, \
    COLS_DROP, FLATTEN_COLS_DROP, OUTPUT_RENAME, OUTPUT_REGISTER_COLS, PUBLIC_DOMAINS

################## USER PART ##################
######## DEFINE INPUT NAD OUTPUT PATHS ########
JSONS_OP = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Operational\ALL'
JSONS_INV = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Investigated'
JSONS_LIQ = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Liquidated\ALL'
JSONS_CSD = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Closed\ALL'

XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\\'
############# END OF USER PART ################

def collect_json_files(jsons_paths: list) -> tuple:
    merged_json_path_dict = {}
    nips_jsons = {}
    nips_errors = {}
    count_col = 0
    for single_path in jsons_paths:
        for file in os.listdir(single_path):
            if file.endswith('.json') and "INVALID" not in file:    
                merged_json_path_dict[file[:10]] = single_path + '\\' + file
                count_col += 1
                print("Data collected for %d entities." % count_col)
    count_load = 0
    for company_id, file in merged_json_path_dict.items():
        with open(file, encoding='utf-8') as json_file:
            try:
                json_text = json.load(json_file)
                nips_jsons[company_id] = json_text
                count_load += 1
                print("Data loaded for %d out of %d entities." % (count_load, len(merged_json_path_dict)))
            except:
                nips_errors[company_id] = file
    return nips_jsons, nips_errors


def parse_company_info(nips_jsons: dict, nips_errors: dict) -> list:
    """ Parse collected JSONs with register data and errors to DataFrames.

    Parameters
    ----------
    nips_jsons : dictionary
        a dictionary storing company ids (key) and collected JSONs (value)
    nips_errors : dictionary
        a dictionary storing company ids (key) and errors (value) collected while
        acquiring EMIS IDs and JSONS with financial data

    Returns
    -------
    full_output : pd.DataFrame
        a DataFrame storing aggregated both valid nad ivalid collected register data
    output : pd.DataFrame
        a DataFrame storing only valid collected register data
    invalid_output : pd.DataFrame
        a DataFrame storing errors collected while collecting EMIS IDs / JSONS and
        parsing register data
    """

    result_list = []
    count = 0
    # Iterate over dictionary {NIP : JSON}
    for nip, table in nips_jsons.items():
        try:
            # Drop unnecessary columns
            for k in COLS_DROP:
                table.pop(k, None)

            result = flatten_json(table)
            drop_list = []
            for key in result.keys():
                for col in FLATTEN_COLS_DROP:
                    if key.endswith(col):
                        drop_list.append(key)

            for key in drop_list:
                result.pop(key, None)
            for key, value in OUTPUT_RENAME.items():
                result[value] = result.pop(key, None)

            # PARSING SINGLE FIELDS AND CREATION OF NEW VARIABLES
            result['AddresFlat'] = 1 if re.search(r"\/[0-9]*", result['Address']) is not None else 0
            result['EmailAdressNotPresent'] = 0 if result['EmailAddress'] is not None else 1
            result['EmailAdressPublic'] = 0
            if result['EmailAddress'] is not None:
                for i in PUBLIC_DOMAINS:
                    if i in result['EmailAddress']:
                        result['EmailAdressPublic'] = 1
                        break

            result['FaxNotPresent'] = 0 if result['Fax'] is not None else 1
            result['PhoneNotPresent'] = 0 if result['Phone'] is not None else 1
            result['WebsiteNotPresent'] = 0 if result['Website'] is not None else 1
            # PARSE AUDIT DATE
            if result['AuditDate'] is not None:
                result['AuditDateNull'] = 0
                result['AuditDateYearsAgo'] = int(d.datetime.now().year) - d.datetime.strptime(result['AuditDate'], '%Y-%m-%d').year
            else:
                result['AuditDateNull'] = 1
                result['AuditDateYearsAgo'] = 'n/a'
            # PARSE COMPANY SIZE AND SIZE YEAR
            if result['CompanyRevenueYear'] is not None:
                result['CompanyRevenue2YearsAgo'] = 1 if int(result['CompanyRevenueYear']) < d.datetime.now().year - 2 else 0
            else:
                result['CompanyRevenue2YearsAgo'] = 'n/a'
            # PARSE COUNTRY CODE
            result['CountryForeign'] = 1 if result['Country'] != 'PL' else 0
            result['DescriptionNull'] = 0 if result['Description'] is not None else 1
            # PARSE INCORPORATION YEAR
            result['IncLessThan1YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 1 else 0
            result['IncLessThan3YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 3 else 0
            result['IncLessThan5YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 5 else 0
            result['IncLessThan10YearsAgo'] = 1 if int(result['IncorporationYear']) > int(d.datetime.now().year) - 10 else 0
            result['IncYearsAgo'] = int(d.datetime.now().year) - int(result['IncorporationYear'])
            # PARSE PRODUCTS
            if result['MainProducts'] is None:
                result['MainProductsNull'] = 1
                result['MainProducts'] = 'n/a'
            elif isinstance(result['MainProducts'], str) and not result['MainProducts'].strip():
                result['MainProductsNull'] = 1
                result['MainProducts'] = 'n/a'
            elif isinstance(result['MainProducts'], str) and result['MainProducts'].strip():
                result['MainProductsNull'] = 0
            # PARSE MARKET CAPITALIZATION
            result['MarketCapNull'] = 1 if result['LatestMarketCapitalization'] is None else 0

            # PARSE NESTED FIELDS
            parse_affiliates(result)
            parse_employees(result)
            parse_dividends(result)
            parse_executives(result)
            parse_external_ids(result)
            parse_naics(result)
            parse_outstanting_shares(result)
            parse_owners(result)
            parse_previous_names(result)
            parse_segment(result)
            # APPEND PARSED DICTIONARY TO LIST FROM WHICH TABLE IS CREATED
            result_list.append(result)
            count += 1
            print("Data parsed for %d out of %d entities." % (count, len(nips_jsons)))
        except Exception as exc:
            error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
            print("For " + nip + " doesn't work.")
            nips_errors[nip] = error
    # CREATE OUTPUT TABLE
    output = pd.DataFrame(result_list)
    output = output[OUTPUT_REGISTER_COLS]
    output = output.sort_values(by=['NIP'], na_position='last')

    if nips_errors:
        # CREATE DATAFRAME FROM LIST OF ERRORS
        invalid_output = pd.DataFrame.from_dict(nips_errors, orient='index').reset_index()
        invalid_output.columns = ['NIP', 'Error']
        invalid_output.sort_values(by=['NIP'], inplace=True, na_position='last')
    else:
        # Create empty DataFrame if there is no valid output
        invalid_output = pd.DataFrame(columns=['NIP', 'Error'])

    # MERGE VALID AND INVALID OUTPUT
    full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort=True)
    #full_output.drop_duplicates(keep='first', subset='NIP', inplace=True)
    full_output.reset_index(drop=True)
    full_output = full_output.sort_values(by=['NIP'], na_position='last')
    return full_output, output, invalid_output


############# GET OUTPUT ################
jsons_loaded, jsons_invalid = collect_json_files([JSONS_OP, JSONS_INV, JSONS_LIQ, JSONS_CSD])

full_output, output, invalid_output = parse_company_info(jsons_loaded, jsons_invalid)
with pd.ExcelWriter(XLSX_OUTPUT_PATH +
                    'EMIS_REGISTER_' +
                    str(d.date.today()) +
                    '.xlsx') as writer:
            full_output.to_excel(writer, sheet_name='FULL_OUTPUT', index=False)
            #output.to_excel(writer, sheet_name='VALID', index=False)
            invalid_output.to_excel(writer, sheet_name='INVALID', index=False)
            