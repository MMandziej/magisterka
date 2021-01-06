import base64
import copy
import datetime as d
import errno
import pandas as pd
import time as t
import os

from pwg_ordinary import get_regon_caseid, get_data, parse_set_update, parse_last_update

############## DEFINE API KEYS ##############
public_key = 'krs4po'
private_key = '12ef683460534adc6352e8d633cb17ad'

####### DEFINE INPUT AND OUTPUT KEYS ########
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\PWG\INPUT_API\NIP_list.xlsx'
SETUPDATE_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\Global_Regulations\SET_UPDATE\\'
GETLASTUPDATE_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\Global_Regulations\GET_LASTUPDATE\\'
GETLASTDOC_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\Global_Regulations\GET_LASTDOC\\'
LOG_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\Global_Regulations\\'
PDF_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\Global_Regulations\pdf\\'
LOG_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\Global_Regulations\LOG\\'

######## DEFINE SLEEP TIME IN SECONDS #######
sleep_time = 960

################## GET PDF ##################
def parse_pdf(getLastDoc_output):
    valid_output = getLastDoc_output[0] 
    pdf_valid_guid = '' 
    regon_status_date = {}
    output_dict = {}
    
    for regon, table in valid_output.items():
        try:
            if 'bin' in table['data']:
                bin_coded = table['data']['bin']
                if len(bin_coded) == 0:
                    status_bin = 'Bin empty'
                    update_date = 'Date empty'
                else:
                    bin_decoded = base64.b64decode(bin_coded)
                    output_dict[regon] = bin_decoded
                    status_bin = 'Bin valid'
                    update_date = table['data']['last_doc_date']    
            else:
                status_bin = table['data']['message']
                update_date = 'Date empty'
            regon_status_date[regon] = [status_bin, update_date]
        except Exception as e :
            error = 'Code: {c}, Message: {m}'.format(c = type(e).__name__, m = str(e))
            status_bin = error
            update_date = 'Date invalid'
            regon_status_date[regon] = [status_bin, update_date]

    regon_case = copy.deepcopy(regon_case_dict)
    regon_case_list = list(regon_case.keys())
    output_list = list(output_dict.keys())
    missing_values = list(set(regon_case_list) - set(output_list))
    
    for i in missing_values:
        regon_case.pop(i)
        
    for regon_valid, regon in zip(output_dict, regon_case):
        try:
            filepath = os.path.join(PDF_OUTPUT_PATH, str(regon_case[regon]))
            os.makedirs(filepath)
            with open(os.path.join(filepath, regon_valid + '{}.pdf'.format(pdf_valid_guid)), 'wb') as fp:
                fp.write(output_dict[regon_valid])
        except OSError as e:
            if e.errno == errno.EEXIST:
                regon_status_date[regon_valid][0] = 'Could not create directory file'
        except TypeError:
                regon_status_date[regon_valid][0] = 'Wrong NIP/KRS/REGON format'
        except:
            regon_status_date[regon_valid][0] = 'Bin invalid'
        
    regon_status_date_df = pd.DataFrame.from_dict(regon_status_date, orient = 'index', columns = ['REGON', 'BinStatus', 'GLD_LastDocDate']).reset_index()  
    regon_case_df = pd.DataFrame.from_dict(regon_case_dict, orient = 'index', columns = ['REGON', 'CaseID']).reset_index()

    output = regon_status_date_df.merge(regon_case_df, how = 'outer', on = 'REGON', sort = True)
    output.reset_index(drop=True, inplace=True)
    output.sort_values(by = ['CaseID'], inplace=True)
    output = output[['CaseID', 'REGON', 'BinStatus', 'GLD_LastDocDate']] #add 'Bin'
    output.to_excel(LOG_OUTPUT_PATH + str(d.date.today()) + '.xlsx', index=False)
    return output

################## CREATE LOG #################
def create_log():
    log_df = parse_SetUpdateFirma[0].merge(parse_LastUpdate[0], how = 'outer', on = 'REGON', sort = True)
    log_df = log_df.merge(parsePDF_output, how = 'outer', on = 'REGON', sort = True)
    log_df = log_df[['CaseID', 'REGON', 'Code', 'Message', 'UpdateDate', 'LL_LastDocDate', 'BinStatus', 'GLD_LastDocDate']]
    log_df.sort_values(by = ['CaseID'], inplace=True)
    log_df.to_excel(LOG_OUTPUT_PATH + str(d.date.today()) + '.xlsx', index=False)
    return log_df 

################# GET OUPTUT ##################
############ GET NIP NAD CASE LIST ############
regon_list = get_regon_caseid(INPUT_FILE)[0]
regon_case_dict = get_regon_caseid(INPUT_FILE)[1]

################# SET UPDATE ##################
setUpdateFirma_output = get_data(private_key, public_key, 'setUpdateFirma', regon_list, SETUPDATE_OUTPUT_PATH)
parse_SetUpdateFirma = parse_set_update(setUpdateFirma_output, LOG_OUTPUT_PATH)
################### SLEEP #####################
t.sleep(sleep_time)

################# LAST UPDATE  ################
getLastUpdate_output = get_data(private_key, public_key, 'getLastUpdate', regon_list, GETLASTUPDATE_OUTPUT_PATH)
parse_LastUpdate = parse_last_update(getLastUpdate_output, LOG_OUTPUT_PATH)

############## GET LAST DOC ###################
getLastDoc_output = get_data(private_key, public_key, 'getLastDoc', regon_case_dict, GETLASTDOC_OUTPUT_PATH)
parsePDF_output = parse_pdf(getLastDoc_output)

###############################################
log = create_log()

