"""
Script used to collect and parse financial data from JSONs downloaded using
EMIS API based on getStatementByCode method.

Data are processed and exported to xlsx file for later usage for FAIT ML purposes.
"""

import datetime as d
import os
import json
import numpy as np
import pandas as pd

from copy import deepcopy
from math import isnan

from ml_help import fin_keys_drop, cols_rename, fin_known_cols, fin_fait_columns#, \
    #retrieve_latest_data


################## USER PART ##################
######## DEFINE INPUT NAD OUTPUT PATHS ########
PATH_TO_JSONS = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\FORENSIC_DATA\EMIS\FINANCE\501-1000'
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


def parse_financial_data(nips_jsons: list,
                         nips_errors: dict) -> pd.DataFrame:
    """ Parse collected JSONs with financial data and errors to DataFrame

    Parameters
    ----------
    nips_jsons : list (of dicts)
        a list of dicts storing coompany id (key) and collected JSON (value)
    nips_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected while 
        acquiring EMIS IDs and JSONS with financial data 

    Returns
    -------
    full_output : pd.DataFrame
        a DataFrame storing aggregated parsed financial data for all fiscal years
    """
    accounts = {'NS': 'NetSalesRevenue',
                'OP': 'OperatingProfitEBIT',
                'PERSON': 'EmployeeBenefitExpense',
                'TS': 'TotalAssets',
                'NP': 'NetProfitLossForThePeriod',
                'TANG': 'PropertyPlantAndEquipment',
                'CE': 'CashandCashEquivalents',
                'SE': 'TotalEquity',
                'ISSUED': 'IssuedCapital',
                'CA': 'CurrentAssets',
                'CL': 'CurrentLiabilities'}

    financial_cols = ['NIP', 'FiscalYear', 'NetSalesRevenue', 'OperatingProfitEBIT',
        'EmployeeBenefitExpense', 'TotalAssets', 'NetProfitLossForThePeriod', 
        'PropertyPlantAndEquipment', 'CashandCashEquivalents', 'TotalEquity',
        'IssuedCapital', 'CurrentAssets', 'CurrentLiabilities', 'consolidated']

    result_list = []
    # Iterate over single {NIP : JSON} dict
    for nip, table in nips_jsons.items():
        try:
            # Try to extract basic information, insert None if not exist
            value_dict = {}
            value_dict['NIP'] = nip
            value_dict['FiscalYear'] = table['fsYear']
            # Extract type of collected financial report
            consolidation_status = table['consolidatedStatus']
            if consolidation_status == 'N':
                value_dict['consolidated'] = 'Individual'
            else:
                value_dict['consolidated'] = 'Consolidated'
            # Extract defined financial data from nested fields if exists
            account_list = table['accountList']
            for pole, name in accounts.items():
                for field in account_list:
                    if field['accountCode'] == pole:
                        value_dict[name] = field['accountValue']
            # Append list of dicts with data for single company and fiscal year
            result_list.append(value_dict)
        except Exception as e:
            # If data could not be parsed raise exception and append error
            # Append existing list of errors
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            nips_errors[nip] = error

    if result_list:
        # Create DataFrame from list of dicts with data for single company and fiscal years
        output = pd.DataFrame(result_list)[financial_cols]
    else:
        # Create empty DataFrame if there is no valid output 
        output = pd.DataFrame(columns=financial_cols)

    if nips_errors:
        # Create DataFrame from list of errors
        invalid_output = pd.DataFrame(list(nips_errors.keys()), columns=['nip'])
    else:
        # Create empty DataFrame if there is no valid output
        invalid_output = pd.DataFrame(columns=['NIP'])

    # Merge both outputs
    full_output = pd.concat([output, invalid_output], sort=True)
    full_output = full_output[pd.notnull(full_output['FiscalYear'])]
    full_output = full_output[financial_cols].sort_values(by=['NIP', 'FiscalYear'],
                                          ascending=[True, False],
                                          na_position='last').reset_index(drop=True)
    #full_output[['EMISID', 'NIP', 'Data rozpoczęcia współpracy']] = full_output[['EMISID', 'NIP', 'Data rozpoczęcia współpracy']].fillna('')
    full_output[['NIP', 'consolidated']] = full_output[['NIP', 'consolidated']].astype(str)
    # Divide financial data by 1000 and store it in thousands
    #full_output.iloc[:, 3:12] /= 1000
    print("Output table successfully created.")
    return full_output


def retrieve_latest_data(data: pd.DataFrame, max_year: int) -> list:
    nsr_latest_df = data['NetSalesRevenue'][data.FiscalYear == max_year].iloc[0]
    tassets_latest_df = data['TotalAssets'][data.FiscalYear == max_year].iloc[0]
    ebit_latest_df = data['OperatingProfitEBIT'][data.FiscalYear == max_year].iloc[0]
    netprofitloss_latest_df = data['NetProfitLossForThePeriod'][data.FiscalYear == max_year].iloc[0]
    ppae_latest_df = data['PropertyPlantAndEquipment'][data.FiscalYear == max_year].iloc[0]
    cash_latest_df = data['CashandCashEquivalents'][data.FiscalYear == max_year].iloc[0]
    tequity_latest_df = data['TotalEquity'][data.FiscalYear == max_year].iloc[0]
    icap_latest_df = data['IssuedCapital'][data.FiscalYear == max_year].iloc[0]
    ebe_latest_df = data['EmployeeBenefitExpense'][data.FiscalYear == max_year].iloc[0]
    ca_latest_df = data['CurrentAssets'][data.FiscalYear == max_year].iloc[0]
    cl_latest_df = data['CurrentLiabilities'][data.FiscalYear == max_year].iloc[0]
    
    nsr_latest = None if isnan(nsr_latest_df) else float(nsr_latest_df)
    tassets_latest = None if isnan(tassets_latest_df) else float(tassets_latest_df)
    ebit_latest = None if isnan(ebit_latest_df) else float(ebit_latest_df)
    netprofitloss_latest = None if isnan(netprofitloss_latest_df) else float(netprofitloss_latest_df)
    ppae_latest = None if isnan(ppae_latest_df) else float(ppae_latest_df)
    cash_latest = None if isnan(cash_latest_df) else float(cash_latest_df)
    tequity_latest = None if isnan(tequity_latest_df) else float(tequity_latest_df)
    icap_latest = None if isnan(icap_latest_df) else float(icap_latest_df)
    ebe_latest = None if isnan(ebe_latest_df) else float(ebe_latest_df)
    ca_latest = None if isnan(ca_latest_df) else float(ca_latest_df)
    cl_latest = None if isnan(cl_latest_df) else float(cl_latest_df)

    return nsr_latest, tassets_latest, ebit_latest, netprofitloss_latest, ppae_latest,\
            cash_latest, tequity_latest, icap_latest, ebe_latest, ca_latest, cl_latest
    

def calculate_fait_tests(fait_output: pd.DataFrame) -> pd.DataFrame:
    unique_nips = list(fait_output['NIP'].unique())
    nip_tests = {}
    for nip in unique_nips:
        tests_dict = {}
        chunk_df = fait_output[fait_output['NIP'] == nip]
        available_years = list(chunk_df.FiscalYear.unique())
        min_year, max_year = min(available_years), max(available_years)

        # Retrieve latest financial data
        nsr_latest, tassets_latest, ebit_latest, netprofitloss_latest, ppae_latest,\
        cash_latest, tequity_latest, icap_latest, ebe_latest, ca_latest, cl_latest = retrieve_latest_data(chunk_df, max_year)

        if nsr_latest is None:
            a = tests_dict['Dane finansowe: Przychody ze sprzedaży poniżej 10 mln zł'] = np.nan
            tests_dict['Dane finansowe: Przychody ze sprzedaży pomiędzy 10 a 50 mln zł'] = np.nan
            tests_dict['Dane finansowe: Przychody ze sprzedaży powyżej 50 mln zł'] = np.nan
        elif nsr_latest < 10000:
            a = tests_dict['Dane finansowe: Przychody ze sprzedaży poniżej 10 mln zł'] = 1
            tests_dict['Dane finansowe: Przychody ze sprzedaży pomiędzy 10 a 50 mln zł'] = 0
            tests_dict['Dane finansowe: Przychody ze sprzedaży powyżej 50 mln zł'] = 0
        elif nsr_latest >= 10000 and nsr_latest <= 50000:
            a = tests_dict['Dane finansowe: Przychody ze sprzedaży poniżej 10 mln zł'] = 0
            tests_dict['Dane finansowe: Przychody ze sprzedaży pomiędzy 10 a 50 mln zł'] = 1
            tests_dict['Dane finansowe: Przychody ze sprzedaży powyżej 50 mln zł'] = 0           
        elif nsr_latest > 50000:
            a = tests_dict['Dane finansowe: Przychody ze sprzedaży poniżej 10 mln zł'] = 0
            tests_dict['Dane finansowe: Przychody ze sprzedaży pomiędzy 10 a 50 mln zł'] = 0
            tests_dict['Dane finansowe: Przychody ze sprzedaży powyżej 50 mln zł'] = 1
            
        if tassets_latest is None:
            tests_dict['Dane finansowe: Aktywa poniżej 10 mln zł'] = np.nan
            tests_dict['Dane finansowe: Aktywa pomiędzy 10 a 50 mln zł'] = np.nan
            tests_dict['Dane finansowe: Aktywa powyżej 50 mln zł'] = np.nan            
        elif tassets_latest < 10000:
            tests_dict['Dane finansowe: Aktywa poniżej 10 mln zł'] = 1
            tests_dict['Dane finansowe: Aktywa pomiędzy 10 a 50 mln zł'] = 0
            tests_dict['Dane finansowe: Aktywa powyżej 50 mln zł'] = 0            
        elif tassets_latest >= 10000 and tassets_latest <= 50000:
            tests_dict['Dane finansowe: Aktywa poniżej 10 mln zł'] = 0
            tests_dict['Dane finansowe: Aktywa pomiędzy 10 a 50 mln zł'] = 1
            tests_dict['Dane finansowe: Aktywa powyżej 50 mln zł'] = 0           
        elif tassets_latest > 50000:
            tests_dict['Dane finansowe: Aktywa poniżej 10 mln zł'] = 0
            tests_dict['Dane finansowe: Aktywa pomiędzy 10 a 50 mln zł'] = 0
            tests_dict['Dane finansowe: Aktywa powyżej 50 mln zł'] = 1
                       
        if ebit_latest is None or nsr_latest is None:    
            tests_dict['Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)'] = np.nan
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%'] = np.nan
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%'] = np.nan            
        elif nsr_latest == 0.0:
            tests_dict['Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%'] = 0
        elif ebit_latest/nsr_latest < 0:
            tests_dict['Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)'] = 1
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%'] = 0            
        elif ebit_latest/nsr_latest >= 0 and ebit_latest/nsr_latest <= 0.05  and not nsr_latest == 0.0:
            tests_dict['Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%'] = 1
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%'] = 0            
        elif ebit_latest/nsr_latest > 0.2 and not nsr_latest == 0.0:
            tests_dict['Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%'] = 1
        else:
            tests_dict['Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%'] = 0
            tests_dict['Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%'] = 0
        
        if cash_latest is None:
            tests_dict['Dane finansowe: Środki pieniężne powyżej 1 mln zł'] = np.nan
            tests_dict['Dane finansowe: Środki pieniężne poniżej 100 tys. zł'] = np.nan            
        elif cash_latest > 1000:
            tests_dict['Dane finansowe: Środki pieniężne powyżej 1 mln zł'] = 1
            tests_dict['Dane finansowe: Środki pieniężne poniżej 100 tys. zł'] = 0            
        elif cash_latest < 100:
            tests_dict['Dane finansowe: Środki pieniężne powyżej 1 mln zł'] = 0
            tests_dict['Dane finansowe: Środki pieniężne poniżej 100 tys. zł'] = 1
        else:    
            tests_dict['Dane finansowe: Środki pieniężne powyżej 1 mln zł'] = 0
            tests_dict['Dane finansowe: Środki pieniężne poniżej 100 tys. zł'] = 0
            
        if nsr_latest is None or cash_latest is None:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Środków pieniężnych powyżej 250'] = np.nan
        elif cash_latest == 0.0:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Środków pieniężnych powyżej 250'] = 0
        elif nsr_latest/cash_latest > 250:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Środków pieniężnych powyżej 250'] = 1
        else:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Środków pieniężnych powyżej 250'] = 0
            
        if nsr_latest is None or ebe_latest is None:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Wynagrodzeń powyżej 50'] = np.nan
        elif ebe_latest == 0.0:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Wynagrodzeń powyżej 50'] = 0    
        elif nsr_latest/abs(ebe_latest) > 50:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Wynagrodzeń powyżej 50'] = 1
        else:
            tests_dict['Dane finansowe: Stosunek Przychodów ze sprzedaży do Wynagrodzeń powyżej 50'] = 0

        if netprofitloss_latest is None:
            tests_dict['Dane finansowe: Strata netto w ostatnim roku finansowym'] = np.nan
        elif netprofitloss_latest < 0:
            tests_dict['Dane finansowe: Strata netto w ostatnim roku finansowym'] = 1
        else:
            tests_dict['Dane finansowe: Strata netto w ostatnim roku finansowym'] = 0
            
        latest3yrs = [str(yr) for yr in available_years[-3:]]
        npl_latest_df = chunk_df['NetProfitLossForThePeriod'][chunk_df['FiscalYear'].isin(latest3yrs)]
        if np.sum(np.array(npl_latest_df)) < 0:
            tests_dict['Dane finansowe: Strata netto w 3 ostatnich latach finansowych'] = 1
        else:
            tests_dict['Dane finansowe: Strata netto w 3 ostatnich latach finansowych'] = 0
        
        if netprofitloss_latest is None or icap_latest is None:
            tests_dict['Dane finansowe: Strata w ostatnim roku finansowym większa niż kapitał własny'] = np.nan
        elif netprofitloss_latest + tequity_latest < 0:
            tests_dict['Dane finansowe: Strata w ostatnim roku finansowym większa niż kapitał własny'] = 1
        else:
            tests_dict['Dane finansowe: Strata w ostatnim roku finansowym większa niż kapitał własny'] = 0
        
        if icap_latest is None or tequity_latest is None:
            tests_dict['Dane finansowe: Kapitał własny niższy niż kapitał zakładowy (Ujemny kapitał własny)'] = np.nan
        elif icap_latest > tequity_latest:
            tests_dict['Dane finansowe: Kapitał własny niższy niż kapitał zakładowy (Ujemny kapitał własny)'] = 1
        else:
            tests_dict['Dane finansowe: Kapitał własny niższy niż kapitał zakładowy (Ujemny kapitał własny)'] = 0     

        # Spadek przychodów ze sprzedaży rok po roku 
        npl_array = np.array(chunk_df['NetProfitLossForThePeriod'])
        npl_bools = [npl_array[i] > npl_array[i+1] for i in range(len(npl_array)-1)]
        tests_dict['Dane finansowe: Spadek przychodów w każdym z dostępnych lat finansowych'] = 1 if all(npl_bools) else 0

        # Zmniejszenie kapitału własnego
        capital_max = float(chunk_df['IssuedCapital'][chunk_df.FiscalYear == max_year])
        capital_min = float(chunk_df['IssuedCapital'][chunk_df.FiscalYear == min_year])
        tests_dict['Dane finansowe: Spadek kapitału własnego w badanym okresie'] = 1 if capital_max < capital_min * 0.8 else 0

        # NEW FAIT AND ML TESTS AND INDICATORS
        # aktywa bieżące / pasywa bieżące;
        if ca_latest is None or cl_latest is None or cl_latest == 0:
            tests_dict['Dane finansowe: Stosunek aktywów do pasywów bieżących'] = np.nan
        else:
            tests_dict['Dane finansowe: Stosunek aktywów do pasywów bieżących'] = ca_latest / cl_latest

        # aktywa obrotowe - zapasy - należności / zobowiązania krótkoterminowe
        # TRWC - (BSITA * TS)
        # zysk brutto / przychody ze sprzedaży
        if ebit_latest is None or nsr_latest is None or nsr_latest == 0:
            tests_dict['Dane finansowe: Stosunek zysku brutto do przychodów ze sprzedaży'] = np.nan
        else:
            tests_dict['Dane finansowe: Stosunek zysku brutto do przychodów ze sprzedaży'] = ebit_latest / nsr_latest

        # średnia wartość zapasów / przychody ze sprzedaży * 360 dni
        # inventories = BSITA * TS / NSR

        # zysk netto / średnia wartość aktywów
        # NP / TS

        # zobowiązania ogółem + rezerwy/ wynik na działalności operacyjnej + amortyzacja

        
        # Append main dict with tests dict
        nip_tests[nip] = tests_dict

    cols_sql = [
        'NIP', 'NetSalesRevenue', 'OperatingProfitEBIT', 'EmployeeBenefitExpense',
        'TotalAssets', 'NetProfitLossForThePeriod', 'PropertyPlantAndEquipment',
        'CashandCashEquivalents', 'TotalEquity', 'IssuedCapital', 'FiscalYear', 'consolidated', 
        'Dane finansowe: Przychody ze sprzedaży poniżej 10 mln zł',
        'Dane finansowe: Przychody ze sprzedaży pomiędzy 10 a 50 mln zł',
        'Dane finansowe: Przychody ze sprzedaży powyżej 50 mln zł',
        'Dane finansowe: Aktywa poniżej 10 mln zł',
        'Dane finansowe: Aktywa pomiędzy 10 a 50 mln zł',
        'Dane finansowe: Aktywa powyżej 50 mln zł',
        'Dane finansowe: Ujemna marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży)',
        'Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) od 0% do 5%',
        'Dane finansowe: Marża brutto (Zysk z działalności operacyjnej / Przychody ze sprzedaży) powyżej 20%',
        'Dane finansowe: Środki pieniężne powyżej 1 mln zł',
        'Dane finansowe: Środki pieniężne poniżej 100 tys. zł',
        'Dane finansowe: Stosunek Przychodów ze sprzedaży do Środków pieniężnych powyżej 250',
        'Dane finansowe: Stosunek Przychodów ze sprzedaży do Wynagrodzeń powyżej 50',
        'Dane finansowe: Strata netto w ostatnim roku finansowym',
        'Dane finansowe: Strata netto w 3 ostatnich latach finansowych',
        'Dane finansowe: Strata w ostatnim roku finansowym większa niż kapitał własny',
        'Dane finansowe: Kapitał własny niższy niż kapitał zakładowy (Ujemny kapitał własny)']
    tests_df = pd.DataFrame(nip_tests)
    tests_df_t = tests_df.T   
    tests_merged = fait_output.join(tests_df_t, on='NIP')
    tests_merged.drop_duplicates(subset='NIP', keep='first', inplace=True)
    fait_data_tests = tests_merged[cols_sql]
    return fait_data_tests, tests_merged


def create_output(loaded_jsons: list) -> pd.DataFrame:
    parsed_jsons = []
    for nip, table in loaded_jsons.items():
        json_table = deepcopy(table)
        # DELETE UNCECESSARY DATA FROM DICTS
        for code in fin_keys_drop:
            try:
                json_table.pop(code)
            except KeyError:
                print("For NIP " + nip + " the following key not found: " + code)
            # MAP ISIC WITH NIP
            json_table['NIP'] = nip
            # PARSE FINANCIAL FIELDS
            for i in table['accountList']:
                json_table[i['accountCode']] = i['accountValue']
            # DELETE INITIAL ACCOUNTS LIST
            #table.pop('accountList')
            parsed_jsons.append(json_table)

    # CREATE OUTPUT
    output_parsed = pd.DataFrame(parsed_jsons)
    # RENAME AND DROP EMPTY COLUMNS
    output_parsed.dropna(axis=1, how='all', inplace=True)
    output_parsed.rename(columns=cols_rename, inplace=True)
    # REARRANGE OUTPUT DATAFRAME
    all_cols = list(output_parsed)
    unknown_cols = [c for c in all_cols if c not in fin_known_cols]
    cols = fin_known_cols + unknown_cols
    output_parsed = output_parsed[cols].sort_values(by=['NIP', 'FiscalYear'], na_position='last')
    # FILL N/A VALUES AND CHANGE COLUMNS TYPE
    output_parsed.fillna('', inplace=True)
    output_parsed = output_parsed.astype({
        'NIP': 'str',
        'ISIC': 'str',
        'BeginDate': 'str',
        'EndDate': 'str',
        'LastUpdate': 'str',
        'OriginalStandardCode': 'str',
        'OutputStandardCode': 'str',
        'AccountErrorFlag': 'str'})
    output_fait = output_parsed[fin_fait_columns]
    output_fait = output_fait[output_fait.FiscalYear.isin([2014, 2015, 2016, 2017, 2018, 2019])]
    cols_numeric = ['Net sales revenue', 'Employee benefit expense',
        'Operating profit/loss (EBIT)', 'NET PROFIT/LOSS FOR THE PERIOD', 'Property, plant and equipment',
        'Cash and cash equivalents', 'Assets', 'Total equity', 'Issued capital']
    output_fait[cols_numeric] = output_fait[cols_numeric].apply(pd.to_numeric, errors='coerce')
    return output_parsed, output_fait


def export_output(parsed_output):
    with pd.ExcelWriter(XLSX_OUTPUT_PATH +
                        'ML_FINANCE_' +
                        str(d.date.today()) +
                        '.xlsx') as writer:
        parsed_output.to_excel(writer, 'Total', index=False)

############ GET OUTPUT ############
jsons_loaded, jsons_invalid = collect_json_files([PATH_TO_JSONS])
output_full = parse_financial_data(jsons_loaded, jsons_invalid)
nips_fait_tests = calculate_fait_tests(output_full)
export_output(output_full)
