import datetime as d
import json
import pandas as pd
import time as t
from copy import deepcopy

from keys_coded import USER_NAME, PASSWORD
from emis import get_session_id, get_nip_name, get_isic_list, request_data,\
                 financial_data_cols_unprocessed, cols_rename, financial_data_cols, accounts

START = t.time()
######## DEFINE USER NAME AND PASSWORD AND METHOD #########
#USER_NAME = 'wojciech.wyszkowski@pwc.com'
#PASSWORD = 'emispwc15' 
METHOD = 'getStatementByCode'

######## DEFINE INPUT NAD OUTPUT PATHS #########
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\Kamil\NIP_LIST.xlsx'
JSON_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\Kamil\JSONS\REGISTER\2019s\\'
XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\Kamil\\'
ID_CLASS = 'KRS'

######### INSERT FISCAL YEARS  ########
fiscal_years = ['2018']

############### END OF USER PART ##################

def get_financial_data(nips_isics: dict, 
                       nips_errors: dict, 
                       session_id: str,
                       fiscal_years: list) -> list:            
    
    """ Send requests to API and collect JSONS with financial data

    Parameters
    ----------
    nips_isics : dictionary
        list of companies' NIPs (key) and EMIS IDs - ISICs for which
        to collect JSONS (value)
    nips_errors : dictionary
        a list of dicts storing NIPs (key) and errors (value) collected
        while acquiring EMIS IDs of companies
    session_id : string
        unique ID of current session required for authentication
    fiscal_years : list (of str values)
        list of financial years (should be stored as str) for which to collect JSONS        

    Returns
    -------
    nips_jsons : list (of dicts)
        a list of dicts storing NIP (key) and collected JSON (value)
    nips_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected
        while acquiring EMIS IDs and JSONS with financial data 
    """
    # Define empty output JSONS list
    nips_jsons = []
    # Send requests in a loop for NIP and fiscal year 
    for nip, isic in nips_isics.items():
        for fiscal_year in fiscal_years:
            # Define guid for saved JSON files, include fiscal year if defined
            json_valid_guid = 'EMIS_FINANCE_' + fiscal_year   
            try:
                # Collect and decode JSON file if response is successfull 
                result_decoded = request_data(METHOD, isic, session_id, '', '', '', str(fiscal_year))
                json_table = json.loads(result_decoded)['data']
                # Export collected JSON as file with valid guid 
                with open(JSON_OUTPUT_PATH + nip + '_{}.json'.format(json_valid_guid), 'w') as f:
                    json.dump(json_table, f)
                # Append collected JSON to output list as a {NIP : json_table} dict
                nips_jsons.append({nip : json_table})           
            except Exception as e:
                # Raise exception and collect error
                error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
                error_dict = {"isic": isic, "nip": nip, "error": error}
                # Export collected error as JSON file 
                with open(JSON_OUTPUT_PATH + nip + '_{}.json'.format(json_valid_guid + '_INVALID'), 'w') as f:
                    json.dump(error_dict, f)  
                # Append/update collected error to output dict as a {NIP : error}
                nips_errors[nip] = error
    return nips_jsons, nips_errors

def parse_financial_data(nips_jsons: list, nips_errors: dict) -> pd.DataFrame:
    """ Parse collected JSONs with financial data and errors to DataFrame

    Parameters
    ----------
    nips_jsons : list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    nips_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected while 
        acquiring EMIS IDs and JSONS with financial data 

    Returns
    -------
    full_output : pd.DataFrame
        a DataFrame storing aggregated parsed financial data for all fiscal years
    """
    
    result_list = []
    # Iterate over list of {NIP : JSON} dicts
    for json_table in nips_jsons:
        # Iterate over single {NIP : JSON} dict
        for nip, table in json_table.items():
            try:
                # Try to extract basic information, insert None if not exist
                value_dict = {}
                value_dict['nip'] = nip
                value_dict['Data rozpoczęcia współpracy'] = None
                value_dict['FiscalYear'] = table['fsYear']
                # Extract type of collected financial report 
                consolidation_status = table['consolidatedStatus']
                if consolidation_status == 'N':
                    value_dict['consolidated'] = 'Individual'
                else:
                    value_dict['consolidated'] = 'Consolidated'
                # Extract defined financial data from nested fields if exists
                account_list = table['accountList']
                for pole in accounts:
                    for field in account_list:
                        if field['accountCode'] == pole:
                            value_dict[pole] = field['accountValue']
                    value_dict[pole] = value_dict.get(pole, None)     
                # Append list of dicts with data for single company and fiscal year
                result_list.append(value_dict)
            except Exception as e:
                # If data could not be parsed raise exception and append error
                # Append existing list of errors 
                error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
                nips_errors[nip] = error
    
    if nips_isics:
        # Create DataFrame from input of NIPs and EMIS IDs
        nips_isics_df = pd.DataFrame.from_dict(nips_isics, orient = 'index').reset_index()
        nips_isics_df.columns = ['nip', 'emisid']
    else:
        # Create empty DataFrame if there is no valid output
        nips_isics_df = pd.DataFrame(columns = ['nip', 'emisid'])
    
    if result_list:
        # Create DataFrame from list of dicts with data for single company and fiscal years
        output = pd.DataFrame(result_list)[financial_data_cols_unprocessed]
        output.rename(columns = cols_rename, inplace=True)
    else:
        # Create empty DataFrame if there is no valid output 
        # Create local copy of variable
        copy_financial_data_cols = deepcopy(financial_data_cols)
        copy_financial_data_cols.remove('emisid')
        output = pd.DataFrame(columns = copy_financial_data_cols)
        
    if nips_errors:
        # Create DataFrame from list of errors 
        invalid_output = pd.DataFrame(list(nips_errors.keys()), columns = ['nip'])
    else:
        # Create empty DataFrame if there is no valid output
        invalid_output = pd.DataFrame(columns = ['NIP'])

    # Merge both outputs
    full_output = pd.concat([output, invalid_output], sort = True)
    full_output = full_output.merge(nips_isics_df, how = 'outer', on = 'nip')
    full_output = full_output[pd.notnull(full_output['FiscalYear'])]
    full_output = full_output[financial_data_cols].sort_values(by=['emisid', 'FiscalYear'], na_position='last').reset_index(drop=True)
    full_output[['emisid', 'nip', 'Data rozpoczęcia współpracy']] = full_output[['emisid', 'nip', 'Data rozpoczęcia współpracy']].fillna('')
    full_output[['emisid', 'nip', 'Data rozpoczęcia współpracy']] = full_output[['emisid', 'nip', 'Data rozpoczęcia współpracy']].astype(str)
    # Divide financial data by 1000 and store it in thousands
    full_output.iloc[:, 3:12] /= 1000
    return full_output

def export_output(full_output: pd.DataFrame) -> list:
    """ Split parsed financial data for each availavle fiscal year and 
    export each table into separated Excel sheet in defined file 

    Parameters
    ----------
    full_output : pd.DataFrame
        a DataFrame storing aggregated parsed financial data merged with invalid output

    Returns
    -------
    output_list: list (of pd.DataFrame)
        a list of separated DataFrames storing financial data for each available fiscal year
    """
    
    try:
        # Extract distinct fiscal years values from input DataFrame
        # if input is not empty
        if not full_output.empty:
            output_dict = {}
            fiscal_years_df = full_output['FiscalYear'].unique().tolist()
            fiscal_years_df.sort()
            # Extract chunk DataFrames by unique fiscal years values
            # and store it in {fiscal year : single_year_output} dict
            for fiscal_year in fiscal_years_df:
                single_year_output = full_output[full_output.FiscalYear == fiscal_year]
                output_dict[fiscal_year] = single_year_output
                # Export total output and each single DataFrame in separated sheets in Excel file
                with pd.ExcelWriter(XLSX_OUTPUT_PATH + 'EMIS_FINANCE1_' + str(d.date.today()) + '.xlsx') as writer:
                    full_output.to_excel(writer, 'Total', index = False)
                    for fiscal_year, df in output_dict.items():
                        df.to_excel(writer, str(int(fiscal_year)), index = False)
                # Create list of single DataFrames
            output_list = list(output_dict.values())
    except Exception as e:
        # Raise exception and print Error
        error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
        print(error)
        output_list=None
    return output_list

############### GET OUTPUT ##################
session_id = get_session_id(USER_NAME, PASSWORD)
nip_list, nips_invalid, log_df = get_nip_name(INPUT_FILE, ID_CLASS)
nips_isics, nips_errors = get_isic_list(nip_list, session_id, ID_CLASS)
nips_jsons, nips_errors = get_financial_data(nips_isics, nips_errors, session_id, fiscal_years)
output_parsed = parse_financial_data(nips_jsons, nips_errors)
output_exported = export_output(output_parsed)

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))

