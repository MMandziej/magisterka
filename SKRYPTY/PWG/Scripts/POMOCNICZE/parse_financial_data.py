import json
import os
import pandas as pd
import sqlalchemy

INPUT = r"C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\GET_FINANCE"
database_name = 'MMandziej'
table_name = 'PWG_Finance'

###################  COLLECT JSONS   ####################

def collect_json_names():
    files = os.listdir(INPUT)
    json_names= []
    [json_names.append(i) for i in files if i[-4:] == 'json']
    return(json_names)

def load_json(json_names):
    valid_files = []
    invalid_files = []
    names_list = []
    valid_nips = []
    invalid_nips = []
    for file in json_names:
        try:
            with open(INPUT + '\\' + file, encoding="utf8") as f:
                data = json.load(f)
                finance = data['result']['finance']
                nip = data['result']['firma']['nip']
                name = data['result']['firma']['nazwa']
                if len(finance) != 0:
                    valid_files.append(finance)
                    valid_nips.append(nip)
                    names_list.append(name)
                else:
                    invalid_files.append(file + ' - empty')
                    invalid_nips.append(nip)            
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            invalid_files.append(file + ' - faulty')
                 
    valid_jsons = [valid_files, valid_nips, names_list]
    invalid_jsons = [invalid_files, invalid_nips]
    return valid_jsons, invalid_jsons

############## PARSING JSONS TO DF ###################

def parse_data(json_files):
    jsons_files = load_json(collect_json_names())[0][0]
    valid_nips = load_json(collect_json_names())[0][1]
    company_names = load_json(collect_json_names())[0][2]
    invalid_files = load_json(collect_json_names())[1][0]
    
    valid_nips_df = pd.DataFrame(valid_nips, columns = ['NIP'])
    company_names_df = pd.DataFrame(company_names, columns = ['Name'])
    financial_year_list = []
    days_list = []
    all_rows = []
    
    try:
        for file in jsons_files:
            ident_list = []
            amount_list = []
            financial_year = file[0]['year']
            financial_year_list.append(financial_year)
            day = file[0]['day']
            days_list.append(day)
            for dictionary in file:
                ident = dictionary['ident']
                ident_list.append(ident)
                amount = dictionary['amount']
                amount_list.append(amount)
                row = dict(zip(ident_list, amount_list))
                
            row_df = pd.DataFrame([row])
            all_rows.append(row_df)
    except:
        pass 
        invalid_files.append(file + ' - wrongly parsed')
    
    fs_year_df = pd.DataFrame(financial_year_list, columns = ['FinanceYear'])
    days_df = pd.DataFrame(days_list, columns = ['Date'])
    all_rows_df = pd.concat(all_rows, ignore_index = True, sort = False)
    output_df = pd.concat([valid_nips_df, company_names_df, fs_year_df, days_df, all_rows_df], axis = 1)
    
    output_fait_df = output_df.rename(columns = {'03.01' : 'NetSalesRevenue',
                                                 '03.02.05' : 'EmployeeBenefitExpense',
                                                 '03.06' : 'OperatingProfitLoss(EBIT)',
                                                 '03.14' : 'NetProfitLossForThePeriod',
                                                 '01.01.02' : 'PropertyPlantAndEquipment',
                                                 '01.02.03.01.03' : 'CashAndCashEquivalent',
                                                 '01.03' : 'Assets',
                                                 '01.04.01' : 'TotalEquity',
                                                 '01.04' : 'IssuedCapital'})
    
    output_fait_df = output_fait_df[['NIP', 'Name', 'FinanceYear', 'Date', 'NetSalesRevenue', 'EmployeeBenefitExpense', 'OperatingProfitLoss(EBIT)',\
                           'NetProfitLossForThePeriod', 'PropertyPlantAndEquipment', 'CashAndCashEquivalent', 'Assets', 'TotalEquity', 'IssuedCapital']]
    
    invalid_files_df = pd.DataFrame(invalid_files, columns = ['InvalidFile'])          
    return output_df, output_fait_df, invalid_files_df

################### GET OUTPUT #######################

output = parse_data(load_json(collect_json_names()))
output[0].to_excel(r"C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_PARSE\PWG_full_financial_data.xlsx")
output[1].to_excel(r"C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_PARSE\PWG_FAIT_financial_data.xlsx")
output[2].to_excel(r"C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_PARSE\PWG_invalid_files.xlsx")

################ EXPORT TO SQL #######################

"""engine = sqlalchemy.create_engine("mssql+pyodbc://PL-WAWFTS002/" +
                                  database_name + "?driver=SQL+Server")
output[0].to_sql(table_name, engine)
output[1].to_sql(table_name + '_FAIT', engine)"""


