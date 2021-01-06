import datetime as d
import json
import pandas as pd
import re
import time as t

from urllib.parse import quote
from urllib.request import Request, urlopen

from emis import get_date_ago, get_nip_name

START = t.time()
######## DEFINE METHOD AND SEARCH SCOPE #########
MERGE_OUTPUTS = False
YEARS = 10
ID_CLASS = 'NIP'
METHOD = 'getDocuments_Name'
START_DATE = get_date_ago(YEARS)
END_DATE = d.date.today().isoformat()
SEARCH25 = 'NEAR25 ("przestęp* VAT*" OR "przestęp* podat*" OR "przestęp* karuzel*" OR "naduży* podat*" OR "naduży* VAT*" OR "karuzel* podat*" OR "karuzel* VAT*" OR "wyłudz* VAT*" OR "wyłudz* podat*" OR "oszu* VAT*" OR "oszu* podat*")'
SEARCH50 = 'NEAR50 ("przestęp* VAT*" OR "przestęp* podat*" OR "przestęp* karuzel*" OR "naduży* podat*" OR "naduży* VAT*" OR "karuzel* podat*" OR "karuzel* VAT*" OR "wyłudz* VAT*" OR "wyłudz* podat*" OR "oszu* VAT*" OR "oszu* podat*")'
TOKEN = 'c95ba1694eafb8da346497423c52f2f60e70f3abeb0b8409c5d7ccd0e5193e0bb7f0294d24d8aa37b203be74957c5151c6c582cb793a3be63523d77177974278'


INPUT_FILE = r"C:\Users\mmandziej001\Desktop\Projects\EMIS\NIP_list.xlsx"
XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\\'
################# REQUEST DATA ################

def request_data(method: str,
                 start_date: str,
                 end_date: str,
                 name: str,
                 search: str,
                 token: str):

    """ Send URL request to obtain information about press articles about company.
        Used as a sub-function to get_document_links"

    Parameters
    ----------
    method : string
        method used to obtain data
    start_date : string
        date of oldest acceptable articles. Default is 10 years before current date.
    end_date : string
        date of newest acceptable articles. Default is current date.
    name : string
    cleansed name of company we want to find articles about.
        Obtained from get_documents_links function.
    search : string
        phrases we want to combine with company name. Obtained from SEARCH25 and SEARCH50.
    token: string
        token used to authenticate the request

    Returns
    -------
    data_decoded : json file
        results of search. If the request is satisfied, includes dictionary with article and information about it
    """

    if method == 'getDocuments_Name':
        url = 'https://api.emis.com/news//Search/query/?countries=PL&'\
        'languages=pl'\
        '&skipDuplicates=1'\
        '&formats[]=1'\
        '&formats[]=2'\
        '&formats[]=3'\
        '&publicationTypes[]=TN&'\
        '&includeBody=1'\
        '&limit=100'\
        '&startDate=' + start_date +\
        '&endDate=' + end_date +\
        '&term="' + name +\
        '"%20' + search +\
        '&token=' + token

    request = Request(url, headers={'User-Agent':'Mozilla/5.0'})
    data_decoded = urlopen(request).read().decode('utf-8')
    return data_decoded

########## GET DOCUMENTS LINKS ###########

def get_documents_links(method: str,
                        nip_names_dict: dict,
                        nip_invalid_dic: dict):
    
    """ Get number of documents (and in case of BadPress, also their body) about selected company
    
    Parameters
    ----------
    method: string
        method used to obtain data
    nip_names_dict: dict
        dict containing company's valid NIP (key) and name cleansed of legal forms (value)
    nip_invalid_dic: dict
        dict containing company's invalid identification number (key) and name (value)
    
    Returns
    -------
    press_values: list
        list of dicts containing company's NIP, name and three press values:
        total - total results of press search
        BadPress25 - results of search for incriminating phrases within 25 words from company name
        BadPress50 - results of search for incriminating phrases within 50 words from company name
    all_articles: list
        list of dicts containing information (Company name and NIP, article ID, Publisher, Title,
        found keywords and body) about incriminating articles from BadPress searches
    nips_errors: dict
        dict containing NIPs for which the error occured (key) and error code (value) """
        
    press_values = []
    all_articles = []
    nips_errors = {}
    for dic in nip_names_dict:   # Iterate over list of dictionaries 
        for nip, name in dic.items():    # NIP (key) and company name (value)
            try:
                company_articles_ids_25 = []
                company_articles_ids_50 = []
                single_press_value = {'NIP' : nip, 'Name' : name}
                result_decoded = request_data(method, START_DATE, END_DATE, quote(name), '', TOKEN)    
                # request data for any articles about company 
                json_table = json.loads(result_decoded)['data']
                if json_table['total'] != 0:    #if search returns results
                    single_press_value['Press'] = json_table['total'] if json_table['duplicates'] is None else json_table['total'] - json_table['duplicates']
                    # Articles = All articles - duplicates
                    result_decoded50 = request_data(method, START_DATE, END_DATE, quote(name), quote(SEARCH50), TOKEN)
                    # request data for incriminating phrases about company in scope of 50 words from company name
                    json_table50 = json.loads(result_decoded50)['data']
                    # load returned articles data
                    if json_table50['total'] != 0:
                        result_decoded25 = request_data(method, START_DATE, END_DATE, quote(name), quote(SEARCH25), TOKEN)
                        # if search in scope of 50 words from company name returns any articless, repeat it in scope of 25 words
                        json_table25 = json.loads(result_decoded25)['data']
                        # load returned articles data
                        for idx, i in enumerate([json_table25['documents'], json_table50['documents']]):
                            for j in i:
                                # for every returned incriminating article
                                hits = re.findall(r'<span style="color: red">.*?<\/span>', j['body'])
                                # find keywords, for which the search returned matches
                                if len(hits) != 0:
                                    hits_cleansed = []
                                    for i in hits:
                                        hit_cleansed = i[i.index(">")+1 : i.index("<", i.index(">"))]
                                        hits_cleansed.append(hit_cleansed)
                                        # list all the keywords
                                single_article_information = {'NIP' : nip,
                                                              'Name' : name,
                                                              'ID' : j['id'],
                                                              'Publisher': j['publication']['name'],
                                                              'Title' : re.sub(('<.*?>'), '', j['title']),
                                                              # Cleanse title of HTML formatting
                                                              'Body':  re.sub(('<.*?>'), '', j['body']),
                                                              # Cleanse body of HTML formatting
                                                              'KeywordsFound' : ", ".join(hits_cleansed)}
                                # make a dic of information about article 
                                if str(idx) == '0' and 'Przegląd prasy' not in j['title']:
                                    # append information about BADPRESS25 artcles to dics and lists excluding press reviews
                                    single_article_information.update({'Type':'25', 'Search':SEARCH25})
                                    company_articles_ids_25.append(j['id'])
                                    all_articles.append(single_article_information)

                                elif str(idx) == '1' and j['id'] not in company_articles_ids_25 and 'Przegląd prasy' not in j['title']:
                                    # append information about BADPRESS50 artcles to dics and lists excluding press reviews
                                    single_article_information.update({'Type':'50', 'Search':SEARCH50})
                                    company_articles_ids_50.append(j['id'])
                                    all_articles.append(single_article_information)
                        single_press_value.update({'BadPress25':len(company_articles_ids_25),
                                                   'BadPress50':len(company_articles_ids_50),
                                                   'TotalBadPress':len(company_articles_ids_25)+len(company_articles_ids_50)})
                                    # append dic with all BadPress values
                    else:
                        single_press_value.update({'BadPress25' : 0, 'BadPress50' : 0, 'TotalBadPress' : 0})
                        # if no BadPress50 articles have been found, set  all BadPress values to 0
                else:
                    single_press_value.update({'Press' : 0, 'BadPress25' : 0, 'BadPress50' : 0, 'TotalBadPress' : 0})
                    #if no articles have been found, set all press values to 0 

                press_values.append(single_press_value)
                # append dic of company press results to general press results dic

            except Exception as e:
                # catch errors
                error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
                nips_errors[nip] = error
    for dic in nip_invalid_dic:
        # for every dic containing invalid NIP
        for invalid_nip, name in dic.items():
            press_values.append({'NIP' : invalid_nip, 'Name' : 'n/a' if name == 'nan' else name, 'Press' : 0, 'BadPress25' : 0, 'BadPress50' : 0, 'TotalBadPress' : 0})
            # set all press values to 0 for invalid NIPs
    return press_values, all_articles, nips_errors
########### MERGE PRESS AND FAIT OUTPUT ###########

def merge_outputs(press_values: list,
                  all_articles: list):
    
    """Export the output of the search to excel file and, optionally, merge it with general FAIT file.
    
    Parameters
    ----------
    press_values: list
        list of dics containing information about full results of the search for respective companies
    all_articles: list
        list of dics with information and body of incriminating articles
        
        
    Returns
    -------
    final_output: dataframe/None
        If MERGE_OUTPUTS is set to True, it's a final dataframe containing all faitcloud information (finance, register and press)
        Else it's a None type object, used only to return the same output arguments
    press_df: dataframe
        Dataframe exported to excel, containing all dics from press_values list
    articles_df: dataframe
        Dataframe exported to excel, containing all dics from all_articles list"""
        
    press_df = pd.DataFrame(press_values)    # change press_values list to df
    press_df = press_df[['NIP', 'Name', 'Press', 'BadPress25', 'BadPress50', 'TotalBadPress']]    # name df columns
    press_df.sort_values(by =['NIP'], inplace =True, na_position ='last')    # sort values by NIP ascending
    press_df[['NIP', 'Press', 'BadPress25', 'BadPress50', 'TotalBadPress']] = press_df[['NIP', 'Press', 'BadPress25', 'BadPress50', 'TotalBadPress']].apply(pd.to_numeric)
    # turn data type to numeric
    press_df = press_df.fillna('n/a')

    articles_df = pd.DataFrame(all_articles) #change all_articles list to df
     
    if articles_df.empty:    # if no incriminating articles have been found
        print("No BadPress articles have been found") 
    else:    # if any incriminating articles have been found:
        articles_df = articles_df[['NIP', 'Name', 'ID', 'Publisher', 'Title', 'Type', 'Search', 'KeywordsFound', 'Body']]    # name columns
        articles_df = articles_df.sort_values(by = ['NIP', 'Type'], na_position='last').reset_index(drop=True)    # sort values by NIP and Type ascending

    if MERGE_OUTPUTS is True:
        faitcloud =  pd.read_excel('PWG_FAITCLOUD.xlsx')    # open general faitcloud file
        final_output = faitcloud.merge(press_df, how ='outer', on ='NIP').reset_index(drop=True)    # merge it with final_output df 
        final_output = final_output.sort_values(by=['NIP'], na_position='last').reset_index(drop=True)    # sort values by NIP ascending
        final_output = final_output.fillna('n/a')
        final_output = final_output.astype(str)    # change data type to str
        final_output.to_excel(XLSX_OUTPUT_PATH + 'FAITCLOUD_PRESS.xlsx', sheet_name = 'FullOutput', index = False)    # export merged file to excel
    else:
        final_output = None 
    
    with pd.ExcelWriter(XLSX_OUTPUT_PATH + 'EMIS_PRESS_' + str(d.date.today()) + '.xlsx') as writer:
        # export press_df and articles_df to excel file
        press_df.to_excel(writer, sheet_name ='PressResults', index = False)
        articles_df.to_excel(writer, sheet_name ='ArticlesResults', index =False)
        return final_output, press_df, articles_df

###########################################

nip_names_dict, nip_invalid_dict, log_df = get_nip_name(INPUT_FILE, ID_CLASS)
press_values, all_articles, nips_errors = get_documents_links(METHOD, nip_names_dict, nip_invalid_dict)
final_output, press_df, articles_df = merge_outputs(press_values, all_articles)

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))
