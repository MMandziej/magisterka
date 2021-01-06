import json
import datetime as d
import pandas as pd

from pwg_ordinary import get_nip_list, request_data, cols_finance_keep, cols_finance_rename, cols_finance

#################### USER PART ####################
##### DEFINE INPUT, OUTPUT FILES AND METHOD  ######
INPUT_FILE = r"C:\Users\mmandziej001\Desktop\Projects\PWG\INPUT_API\NIP_list.xlsx"
JSONS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\GET_FINANCE\\'
XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_PARSE\\'
METHOD = 'getFinance'
######### INSERT FISCAL YEARS  ########
fiscal_years = ['2018']

############### END OF USER PART ##################

def get_jsons(company_id_list: list, fiscal_years: list):    
    """ Send requests to API and collect JSONS with financial data

    Parameters
    ----------
    company_id_list : list (of str values)
        list of companies id's for which to collect JSONS
    fiscal_years : list (of str values)
        list of financial years (stored as str) for which to collect JSONS

    Returns
    -------
    company_ids_jsons : list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    company_ids_errors : list (of dicts)
        a list of dicts storing company id (key) and collected error (value)
    """
    
    # Define empty output JSONS and errors lists
    company_ids_jsons = []
    company_ids_errors = []
    # Send requests in a loop for company id and fiscal year 
    for company_id in company_id_list:
        for fiscal_year in fiscal_years:
            # Define guid for saved JSON files, include fiscal year if defined
            json_guid = 'PWG_' + METHOD if fiscal_year == '' else 'PWG_' + METHOD + '_' + fiscal_year
            try:
                # Collect and decode JSON file if response is successfull 
                result_decoded = request_data(METHOD, company_id, fiscal_year)
                json_table = json.loads(result_decoded)['result']               
                # Export collected JSON as file with valid guid 
                with open(JSONS_OUTPUT_PATH + company_id + '_{}.json'.format(json_guid), 'w') as f:
                    json.dump(json_table, f)
                # Append collected JSON to output list as a {company_id : json_table} dict
                company_ids_jsons.append({company_id : json_table})
            except Exception as e:
                # Raise exception and collect error
                error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
                error_dict = {"nip": company_id, "error": error}
                # Export collected error as JSON file 
                with open(JSONS_OUTPUT_PATH + company_id + '_{}.json'.format(json_guid + '_INVALID'), 'w') as f:
                    json.dump(error_dict, f)
                # Append collected error to output list as a {company_id : error} dict
                company_ids_errors.append({company_id : error})
    return company_ids_jsons, company_ids_errors

def parse_get_finance(company_ids_jsons: list, company_ids_errors: list) -> pd.DataFrame: 
    """ Parse collected JSONs and errors to DataFrame

    Parameters
    ----------
    company_ids_jsons : list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    company_ids_errors : list (of dicts)
        a list of dicts storing company id (key) and collected error (value)

    Returns
    -------
    full_output : pd.DataFrame
        a DataFrame storing aggregated parsed financial data merged with invalid output
    """
    result_list = []
    # Iterate over list of {company id : JSON} dict
    for i in company_ids_jsons:
        for company_id, table in i.items():
            try:
                # Try to extract basic information, insert None if not exist
                value_dict = {}
                value_dict['NIP'] = table['firma']['nip']
                for name, field in {'FiscalYear': 'year', 'LastUpdate': 'day'}.items():
                    try:
                        value_dict[name] = table['finance'][0].get(field, None)
                    except IndexError:
                        value_dict[name] = None 
                # Extract necessary financial fields if exist in collected JSON
                # Do not touch 
                for finance_field in cols_finance_keep:
                    for j in table['finance']:
                        if j['ident'] == finance_field:
                            try:
                                value_dict[finance_field] = float(j['amount'])     
                                if finance_field == '03.02.05':
                                    value_dict[finance_field] = -1*float(j['amount'])  
                            except TypeError:
                                pass
                    value_dict[finance_field] = value_dict.get(finance_field, None)
                """try:
                    if not value_dict['03.01']:
                        value_dict['03.01'] = value_dict['02.01']
                    if not value_dict['01.04.01']:
                        value_dict['01.04.01'] = value_dict['01.04.51']
                    if not value_dict['03.06']:
                        value_dict['03.06'] = value_dict['02.09']
                    value_dict.pop('01.04.51', None)
                    value_dict.pop('02.01', None)
                    value_dict.pop('02.09', None)
                except KeyError as ke:
                    error = 'Code: {c}, Message: {m}'.format(c = type(ke).__name__, m = str(ke))
                    print(value_dict['NIP'])"""
                # Append dict with data for single company and fiscal year to list of dicts
                result_list.append(value_dict)
            except Exception as e:
                print('inde')
                # If data could not be parsed raise exception and append error
                # Append existing list of errors 
                error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
                print(error)
                company_ids_errors.append({company_id: error})
    if result_list:
        # Create DataFrame from list of dicts with data for single company and fiscal years
        output = pd.DataFrame(result_list)
        output = output.rename(cols_finance_rename, axis='columns')
        output = output[cols_finance]
    else:
        # Create empty DataFrame if there is no valid output
        output = pd.DataFrame(columns=cols_finance)
    
    #if company_ids_errors:
        # Create DataFrame from list of errors 
        # invalid_output = pd.DataFrame(company_ids_errors, columns=['NIP', 'Error'])
  #  else:
        # Create empty DataFrame if there is no invalid output

    numeric_cols = ['NetSalesRevenue', 'OperatingProfitEBIT',
    'EmployeeBenefitExpense', 'TotalAssets', 'NetProfitLossForThePeriod',
    'PropertyPlantAndEquipment', 'CashandCashEquivalent',  'TotalEquity',
    'IssuedCapital', 'FiscalYear']
    output[numeric_cols] = output[numeric_cols].apply(pd.to_numeric, errors='coerce')
    invalid_output = pd.DataFrame(columns=['NIP', 'Error'])  
    # Merge both outputs
    full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort=True).reset_index(drop=True)
    full_output = full_output[cols_finance].sort_values(by=['NIP', 'FiscalYear'], ascending=[True, False], na_position='last')
    # Divide financial data by 1000 and store it in thousands
    full_output.iloc[:, 3:13] /= 1000
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
    
    output_list = []
    try:
        # Extract distinct fiscal years values from input DataFrame
        # if input is not empty
        if not full_output.empty:
            output_dict = {}
            fiscal_years = full_output['FiscalYear'].unique().tolist()
            fiscal_years.sort()
            # Extract chunk DataFrames by unique fiscal years values
            # and store it in {fiscal year : single_year_output} dict
            for fiscal_year in fiscal_years:
                single_year_output = full_output[full_output.FiscalYear == fiscal_year]
                output_dict[fiscal_year] = single_year_output
                # Export total output and each single DataFrame in separated sheets in Excel file
                with pd.ExcelWriter(XLSX_OUTPUT_PATH + 'PWG_FINANCE_' + str(d.date.today()) + '.xlsx') as writer:
                    full_output.to_excel(writer, 'Total', index = False)
                    for fiscal_year, df in output_dict.items():
                        df.to_excel(writer, str(int(fiscal_year)), index = False)
            # Create list of single DataFrames
            output_list = list(output_dict.values())
    except Exception as e:
        # Raise exception and print Error
        error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
        print(error)
    return output_list

############### GET OUTPUT ##################
company_id_list = get_nip_list(INPUT_FILE)
company_ids_jsons, company_ids_errors = get_jsons(company_id_list, fiscal_years)
output_parsed = parse_get_finance(company_ids_jsons, company_ids_errors)
output_exported = export_output(output_parsed)
