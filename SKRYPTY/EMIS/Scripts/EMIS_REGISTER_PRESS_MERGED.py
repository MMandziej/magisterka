"""
Script consists of two parts - register and press

Register one is used to retrieve and parse register data from EMIS API based on
getFullCompany method and list of companies IDs. Companies IDs have to be
fist converted into EMIS IDs which is included in script.

Companies' previous names parsed in this process are added to the base list of
company names.

Search for press articles is performed on this list using the
'getDocuments_Name' method. In the case of one company having multiple names, 
search is executed on all of them, but the results are assinged to the name
from the input file.

Data are processed and exported to xlsx file and used for investigating
analysis purposes and FAIT project.
"""

import datetime as d
import json
import pandas as pd
import re
import time as t

from urllib.parse import quote
from urllib.request import Request, urlopen

from directories import INPUT_FILE, REG_JSON_OUTPUT_PATH, REG_XLSX_OUTPUT_PATH, PROJECT_NAME
from emis_full import \
    get_session_id, get_isic_list, get_company_info, get_date_ago,\
    get_nip_name, get_sql_data,\
    get_press_whitelist, flatten_json, parse_employees, parse_affiliates, parse_executives,\
    parse_owners, parse_dividends, parse_outstanting_shares, parse_segment,\
    parse_previous_names, parse_naics, parse_external_ids, format_press_input,\
    cols_drop,\
    PUBLIC_DOMAINS, FLATTEN_COLS_DROP, OUTPUT_RENAME, FULL_REGISTER_COLS
    
from keys_coded import USER_NAME, PASSWORD, PRG_CREDS, GHC_CREDS

############################ USER PART ###########################
######################### DEFINE METHOD ##########################
ID_CLASS = 'NIP'
YEARS = 10
START_DATE, END_DATE = get_date_ago(YEARS), d.date.today().isoformat()
SEARCH25 = 'NEAR25 ("przestęp* VAT*" OR "przestęp* podat*" OR "przestęp* karuzel*" OR "naduży* podat*" OR "naduży* VAT*" OR "karuzel* podat*" OR "karuzel* VAT*" OR "wyłudz* VAT*" OR "wyłudz* podat*" OR "oszu* VAT*" OR "oszu* podat*")'
SEARCH50 = 'NEAR50 ("przestęp* VAT*" OR "przestęp* podat*" OR "przestęp* karuzel*" OR "naduży* podat*" OR "naduży* VAT*" OR "karuzel* podat*" OR "karuzel* VAT*" OR "wyłudz* VAT*" OR "wyłudz* podat*" OR "oszu* VAT*" OR "oszu* podat*")'
TOKEN = 'c95ba1694eafb8da346497423c52f2f60e70f3abeb0b8409c5d7ccd0e5193e0bb7f0294d24d8aa37b203be74957c5151c6c582cb793a3be63523d77177974278'
START = t.time()


def parse_company_info(collected_jsons: dict,
                       collected_errors: dict,
                       nip_names_dict: dict,
                       nips_isics : dict) -> tuple:
    """ Parse collected JSONs with register data and errors to list od dicts

    Parameters
    ----------
    collected_jsons : list (of dicts)
        a list of dicts storing company id (key) and collected JSON (value)
    collected_errors : dictionary
        a dictionary stoprzedring NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data

    Returns
    -------
    result_list: list
        a list storing dictionaries with register data for companies
    collected_errors : dictionary
        a dictionary storing NIP (key) and error (value) collected while
        acquiring EMIS IDs and JSONS with financial data
    """
    result_list = []
    for i in collected_jsons:
        try:
            print(i)
            dictionary = collected_jsons[i]
            dictionary['Data rozpoczęcia współpracy'] = None
            # Drop unnecessary columns
            for k in cols_drop:
                dictionary.pop(k, None)

            # Parse collected JSON file
            result = flatten_json(dictionary)

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

            # Parse nested fields to single field
            parse_employees(result)
            parse_executives(result)
            parse_affiliates(result)
            parse_owners(result)
            parse_dividends(result)
            parse_outstanting_shares(result)
            parse_segment(result)
            result, nip_names_dict = parse_previous_names(result, nip_names_dict, nips_isics, ID_CLASS)
            parse_naics(result)
            parse_external_ids(result)
            # Create DataFrame as row
            result_df = pd.DataFrame([result])
            # Append DataFrame (table row) to list
            result_list.append(result_df)
        except Exception as exc:
            # If data could not be parsed raise exception and append error
            # Append existing list of errors
            error = 'Code: {c}, Message: {m}'.format(c=type(exc).__name__, m=str(exc))
            collected_errors[i] = error
    print("Data successfully parsed for %s companies." % len(result_list))
    return result_list, collected_errors, nip_names_dict


def create_register_output(result_list: list, parsed_errors: dict) -> tuple:
    """ Create output tables in pandas DataFrames from parsedJSONs

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
    full_output : pd.DataFrame
        a DataFrame storing aggregated both valid nad ivalid collected register data
    output : pd.DataFrame
        a DataFrame storing only valid collected register data
    invalid_output : pd.DataFrame
    a DataFrame storing errors collected while collecting EMIS IDs / JSONS and
    parsing register data
    """

    if result_list:
        # Concat all rows into output table
        output = pd.concat(result_list, ignore_index=True, sort=False)
        output = output[FULL_REGISTER_COLS].sort_values(by=['NIP'], na_position='last')
    else:
        # Create empty DataFrame if there is no valid output
        output = pd.DataFrame(columns=FULL_REGISTER_COLS)

    # Fill null values and change type of columns
    output = output.fillna('')
    output = output.astype(str)
    output['NumberOfEmployees'] = pd.to_numeric(output['NumberOfEmployees'])
    output['FewEmployees'] = pd.to_numeric(output['FewEmployees'])
    
    #if parsed_errors:
    #    # Create DataFrame from list of errors
    #    invalid_output = pd.DataFrame.from_dict(parsed_errors, orient='index').reset_index()
    #    invalid_output.columns = ['NIP', 'Error']
    #    invalid_output.sort_values(by=['NIP'], inplace=True, na_position='last')
    #else:
    #    # Create empty DataFrame if there is no valid output
    #    invalid_output = pd.DataFrame(columns=['NIP', 'Error'])

    # Merge both outputs
    #full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort=True)
    #full_output.drop_duplicates(keep='first', subset='NIP', inplace=True)
    #full_output.reset_index(drop=True)
    #full_output = full_output[FULL_REGISTER_COLS].sort_values(by=['NIP'], na_position='last')
    print("Output successfully created.")
    return output #full_output, output#, invalid_output
 
####################### PRESS PART #########################


def request_press_data(method : str, start_date :str , end_date: str, name : str, search: str, token: str) -> str: 
    """ Send a request to API to retrieve json file containing search results
    
    Parameters
    ----------
    method: str
        String specifying method used to send a request to API: getDocuments_Name.
    start_date: str
        Date of oldest possible articles.
    end_date: str
        Today's date.
    name: str
        Name of the company we are seeking articles about.
        In the case of multiple names assigned to one company, this parameter
        contains all their names separated by OR wildcard
    
    Returns
    -------
    data_decoded: str
        String containing results of the search in JSON-style formatting.          
    """
    
    if method == 'getDocuments_Name':
        url = 'https://api.emis.com/news//Search/query/?countries=PL&'\
              'languages=pl&skipDuplicates=1&formats[]=1&formats[]=2&formats[]=3'\
              '&publicationTypes[]=TN&'\
              '&includeBody=1'\
              '&limit=100'\
              '&startDate=' + start_date +\
              '&endDate=' + end_date +\
              '&term=' + name +\
              '%20' + search +\
              '&token=' + token
    
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data_decoded = urlopen(request).read().decode('utf-8')
    return data_decoded


def get_documents_links(nip_names_dict : dict, method : str, creds: str) -> list: 
    
    """ Send requests to API using request_press_data function
    and gather their results in dictionaries.
    Requests are sent for both general and badpress (incriminating) searches. 
    
    Parameters
    ----------
    nip_names_dict: dict
        dict of company ids (keys) and lists of names (values).
    method: str
        String specifying method used to send a request to API: getDocuments_Name.
        
    Returns
    -------
    press_values: list
        List of dictionaries containing company ids, names and results of the press search
    all_articles: list
        List of dictionaries containing company ids, names and the articles
        possibly incriminating them
    nips_errors: dict
        Dict containing errors (values) and ids of companies for which they occured"""    
    press_values = []
    all_articles = []
    nips_errors = {}
    valid_articles_dic = {}
    press_whitelist_dic = get_press_whitelist(creds)

    for nip, name_list in nip_names_dict.items():
        # Iterate over dict of company ids and name lists
        name=name_list[0]       
        search_term = format_press_input(name_list) # format name lists to a valid search input
        try:
            # Send request for general search for a single company
            company_articles_ids_25 = []            
            company_articles_ids_50 = []
            single_press_value = {'NIP' : nip, 'Name' : name}
            result_decoded = request_press_data(method, START_DATE, END_DATE, quote(search_term).replace('%C2%A0','%20'), '', TOKEN)
            # search_term (company names) needs to be formatted to be comply with HTML
            json_table = json.loads(result_decoded)['data']         
            if json_table['total'] != 0:    # If general request returns any articles                 
                # send request for incriminating phrases in the scope of 50 words from one of company names
                single_press_value['Press'] = json_table['total'] if json_table['duplicates'] is None else json_table['total'] - json_table['duplicates']             
                result_decoded50 = request_press_data(method, START_DATE, END_DATE, quote(search_term).replace('%C2%A0','%20'), quote(SEARCH50), TOKEN)
                json_table50 = json.loads(result_decoded50)['data']          
                    
                if json_table50['total'] != 0:    # If BadPress50 request returns any articles
                    # send request for incriminating phrases in the scope of 50 words from one of company names
                    result_decoded25 = request_press_data(method, START_DATE, END_DATE, quote(search_term).replace('%C2%A0','%20'), quote(SEARCH25), TOKEN)
                    json_table25 = json.loads(result_decoded25)['data']    
                        
                    for idx, i in enumerate([json_table25['documents'], json_table50['documents']]):
                        for idj,j in enumerate(i):
                            valid_articles_dic[idj]=j
                            for a in press_whitelist_dic.values():
                                if str(j['id']) == a['ID'] and nip == a[ID_CLASS]:
                                    valid_articles_dic.pop(idj,None)
                    for k in valid_articles_dic.values():        
                        hits = re.findall(r'<span style="color: red">.*?<\/span>', j['body'])    # Highlight company name and incriminating phrases
                        if len(hits) != 0:
                            hits_cleansed = []
                            for i in hits:
                                hit_cleansed = i[i.index(">")+1 : i.index("<", i.index(">"))]
                                hits_cleansed.append(hit_cleansed)
                        single_article_information = {'NIP' : nip,    # Create dic with information for a single company
                                                      'Name' : name, 
                                                      'ID' : j['id'], 
                                                      'Publisher': j['publication']['name'],
                                                      'Title' : re.sub(('<.*?>'),'',j['title']),
                                                      'Body':  re.sub(('<.*?>'),'',j['body']),
                                                      'KeywordsFound' : ", ".join(hits_cleansed)}
                        if str(idx)=='0' and 'Przegląd prasy' not in j['title']:    # Exclude articles with press reviews
                            single_article_information.update({'Type':'25', 'Search':SEARCH25})
                            company_articles_ids_25.append(j['id'])
                            all_articles.append(single_article_information)                               
                            
                        elif str(idx)=='1' and j['id'] not in company_articles_ids_25 and 'Przegląd prasy' not in j['title']:
                            single_article_information.update({'Type': '50', 'Search': SEARCH50})
                            company_articles_ids_50.append(j['id'])
                            all_articles.append(single_article_information)                               
                            single_press_value.update({'BadPress25': len(company_articles_ids_25),
                                                       'BadPress50': len(company_articles_ids_50),
                                                       'TotalBadPress': len(company_articles_ids_25) + len(company_articles_ids_50)})

                else: 
                    single_press_value.update({'BadPress25' : 0, 'BadPress50' : 0, 'TotalBadPress' : 0})
                 # If requests returns no general articles about company, set badpress values as 0      
            else:
                single_press_value.update({'Press' : 0, 'BadPress25' : 0, 'BadPress50' : 0, 'TotalBadPress' : 0})
                
            press_values.append(single_press_value)
                    
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
            nips_errors[nip] = error
    
    for invalid_nip, name in nips_invalid.items(): 
        press_values.append({'NIP': invalid_nip, 'Name': 'n/a' if name=='nan' else name, 'Press': 0, 'BadPress25': 0, 'BadPress50': 0, 'TotalBadPress': 0})
    return press_values, all_articles, nips_errors


########### MERGE PRESS AND FAIT OUTPUT ###########

def merge_outputs(press_values, all_articles, register_output, log_df):
    # Create and sort a dataframe of search results
    press_df = pd.DataFrame(press_values)
    press_df = press_df[['NIP', 'Name', 'Press', 'BadPress25', 'BadPress50', 'TotalBadPress']]
    press_df.sort_values(by=['NIP'], inplace=True, na_position='last')
    press_df[['NIP', 'Press', 'BadPress25', 'BadPress50', 'TotalBadPress']] = press_df[['NIP', 'Press', 'BadPress25', 'BadPress50', 'TotalBadPress']].apply(pd.to_numeric)
    press_df = press_df.fillna('n/a')
    press_df['NIP'] = press_df['NIP'].astype(str)

    # create and sort dataframe of incriminating articles
    if all_articles:
        articles_df = pd.DataFrame(all_articles)
        articles_df = articles_df[['NIP', 'Name', 'ID', 'Publisher', 'Title', 'Type', 'Search', 'KeywordsFound', 'Body']]
        articles_df = articles_df.sort_values(by=['NIP', 'Type'], na_position='last').reset_index(drop=True)
    # Create empty DataFrame if there no articles were found
    else:
        articles_df = pd.DataFrame(columns=['NIP', 'Name', 'ID', 'Publisher',
                            'Title', 'Type', 'Search', 'KeywordsFound', 'Body'])

    output_list = [i for i in register_output]
    sheet_names = ['FullOutput', 'ValidOutput', 'InvalidOutput']

    emis_tests = press_df[['NIP']]
    emis_tests['NoPress'], emis_tests['BadPress'] = 1, 1
    emis_tests.loc[press_df['Press'] == 0, 'NoPress'] = 0
    emis_tests.loc[press_df['TotalBadPress'] == 0, 'BadPress'] = 0
    emis_tests = emis_tests.merge(output_list[0][['NIP', 'WebsiteNotPresent', 'EmailAdressPublic', 'FewEmployees']], how='left', on='NIP')
    emis_tests.iloc[:, 1:] = emis_tests.iloc[:, 1:].apply(pd.to_numeric)

    with pd.ExcelWriter(REG_XLSX_OUTPUT_PATH + 'EMIS_REGISTER_PRESS_' + str(d.date.today()) + '.xlsx') as writer:
        # save results in separate sheets of one Excel file
        for sheet_name, table in zip(sheet_names, output_list):
            table.to_excel(writer, sheet_name, index=False)
        emis_tests.to_excel(writer, sheet_name='EMIS_TESTS', index=False)
        output_list[0][['NIP', 'EMISID', 'Data rozpoczęcia współpracy']].to_excel(
            writer, sheet_name='EMIS_input', index=False)
        log_df.to_excel(writer, sheet_name="LOG", index=False)
        press_df.to_excel(writer, sheet_name='PressResults', index=False)
        articles_df.to_excel(writer, sheet_name='ArticlesResults', index=False)
    return press_df, articles_df, emis_tests


############### GET OUTPUT ##################
print("Downloading and parsing of register and press data pending. Start time: %s." % d.datetime.now())
#nip_names_dict, nips_invalid, press_whitelist, log_df = get_sql_data(PROJECT_NAME, SQL_CREDS) # ONLY USE THIS LINE WHILE GETTING DATA FROM SQL
nip_names_dict, nips_invalid, log_df = get_nip_name(INPUT_FILE, ID_CLASS)
session_id = get_session_id(USER_NAME, PASSWORD)
nips_isics, nips_errors = get_isic_list(nip_names_dict, session_id, ID_CLASS)
nips_jsons, nips_errors = get_company_info(nips_isics,
                                           nips_errors,
                                           session_id,
                                           REG_JSON_OUTPUT_PATH,
                                           'getFullCompany')
#parsed_jsons, nips_errors, nip_names_dict = parse_company_info(nips_jsons, nips_errors, nip_names_dict, nips_isics)
parsed_jsons, nips_errors, nip_names_dict = parse_company_info(nips_jsons_loaded,
                                                               nips_errors,
                                                               nip_names_dict,
                                                               nips_isics)

register_output = create_register_output(parsed_jsons, nips_errors)

#nip_names_dict, nips_invalid = get_nip_name(INPUT_FILE)
press_values, all_articles, nips_errors = get_documents_links(nip_names_dict, 'getDocuments_Name', PRG_CREDS)
press_df, articles_df, tests_df = merge_outputs(press_values, all_articles, register_output, log_df)

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))

nips_jsons_loaded = {}
path_to_json = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Liquidated\15K'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json') and
              'INVALID' not in pos_json]
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        print(index, ' out of ', len(json_files))
        try:
            nips_jsons_loaded[index] = json.load(json_file)
        except:
            print(js + ' invalid file')
            
parsed_jsons, nips_errors, nip_names_dict = parse_company_info(nips_jsons_loaded,
                                                               nips_errors,
                                                               nip_names_dict,
                                                               nips_isics)
register_output = create_register_output(parsed_jsons, nips_errors)
with pd.ExcelWriter(REG_XLSX_OUTPUT_PATH + 'EMIS_REGISTER_LIQUIDATED_' + str(d.date.today()) + '.xlsx') as writer:
    # save results in separate sheets of one Excel file
    register_output.to_excel(writer, 'OUTPUT', index=False)
    for sheet_name, table in zip(sheet_names, output_list):
        table.to_excel(writer, sheet_name, index=False)
    #emis_tests.to_excel(writer, sheet_name='EMIS_TESTS', index=False)
    #output_list[0][['NIP', 'EMISID', 'Data rozpoczęcia współpracy']].to_excel(
    #    writer, sheet_name='EMIS_input', index=False)
    #log_df.to_excel(writer, sheet_name="LOG", index=False)
    #press_df.to_excel(writer, sheet_name='PressResults', index=False)
    #articles_df.to_excel(writer, sheet_name='ArticlesResults', index=False)