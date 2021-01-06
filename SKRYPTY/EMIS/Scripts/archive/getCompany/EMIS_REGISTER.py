import datetime as d
import pandas as pd
import time as t

from emis import get_session_id, get_nip_list, get_isic_list, get_company_info, flatten_json, parse_employees, parse_field, parse_naics,\
                 cols_drop, employees_cols_drop, cols_to_drop_list, output_rename, known_cols, len_guids, cols_guids_to_drop

START = t.time()
######## DEFINE USER NAME, PASSWORD AND METHOD #########
USER_NAME = 'wojciech.wyszkowski@pwc.com'
PASSWORD = 'emispwc15' 
METHOD = 'getFullCompany'

##### DEFINE INPUT AND CREATE OUTPUT PATH ######
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\NIP_list.xlsx'
JSON_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\JSONS_REGISTER\\'
XLXS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\\'

############# PARSING JSONS TO DF ##############

def parse_company_info(nips_jsons, nips_errors):
    result_list = []
    for i in nips_jsons:
        try:
            dictionary = nips_jsons[i]
            dictionary['nip'] = i
            dictionary['Data rozpoczęcia współpracy'] = None
            for k in cols_drop:
                dictionary.pop(k, None)
       
            result = flatten_json(dictionary)
            #### EMPLOYEE NUMBER PART ####
            parse_employees(result)
            for k in employees_cols_drop:
                result.pop(k, None)
    
            result_df = pd.DataFrame([result])

            #### PARSE FIELDS PART ####
            executives = parse_field(result_df, '_executiveNameLocal', '_executiveUserDefinedPositionLocal', 'KeyExecutives')
            shareholders = parse_field(result_df, '_ownerNameLocal', '_ownershipPercentage', 'Shareholders')
            external_ids = parse_field(result_df, '_classCode', '_externalId', 'NationalFiscalIDs')
            naics_codes_df = parse_naics(result_df)
            
            ##### CREATE ROW ####
            result_df = pd.concat([result_df, executives, shareholders, external_ids, naics_codes_df], axis=1)
            result_list.append(result_df)
        except:
            nips_errors[i] = 'Could not parse data'
    try:
        output = pd.concat(result_list, ignore_index=True, sort=False)      
        cols_to_drop = []
        for c in output.columns:
            for l in len_guids:
                if c[l:] in cols_guids_to_drop:
                    cols_to_drop.append(c)
                    
        cols_to_drop.extend(cols_to_drop_list)
        output.drop(columns = cols_to_drop, inplace=True)
        output = output.rename(output_rename, axis = 'columns').sort_values(by=['NIP'])
        
        all_cols = list(output)
        unknown_cols = [c for c in all_cols if c not in known_cols]
        cols = known_cols + unknown_cols    
        output = output[cols].sort_values(by = ['NIP'], na_position='last')    
    except ValueError:
        cols = known_cols
        output = pd.DataFrame(columns = cols)
        
    output = output.fillna('')
    output = output.astype(str)
    
    if bool(nips_errors):
        invalid_output = pd.DataFrame.from_dict(nips_errors, orient = 'index').reset_index()
        invalid_output.columns = ['NIP', 'Error']
        invalid_output.sort_values(by = ['NIP'], inplace=True, na_position='last')
    else:
        invalid_output = pd.DataFrame(columns = ['NIP', 'Error'])
    
    full_output = pd.concat([output, invalid_output.drop(['Error'], axis=1)], sort = True).drop_duplicates(keep = 'first', subset = 'NIP').reset_index(drop=True)
    full_output = full_output[cols].sort_values(by=['NIP'], na_position='last')
    return full_output, output, invalid_output

############### GET OUTPUT ##################  

def get_output(parsed_company_info):
    try:
        output_list = [i for i in parsed_company_info]
        sheet_names = ['FullOutput', 'ValidOutput', 'InvalidOutput']
        
        with pd.ExcelWriter(XLXS_OUTPUT_PATH + 'EMIS_REGISTER_' + str(d.date.today()) + '.xlsx') as writer:
            for sheet_name, df in zip(sheet_names, output_list):
                df.to_excel(writer, sheet_name, index = False)
            output_list[0].to_excel(writer, sheet_name = 'EMIS_input', columns = ['NIP', 'EMISID', 'Data rozpoczęcia współpracy'], index = False)
    except PermissionError:
        print("Close previous output file.")
    except:
        print("Could not export output.")
    return output_list

###########################################
session_id = get_session_id(USER_NAME, PASSWORD)
nip_list = get_nip_list(INPUT_FILE)
nips_isics, nips_errors = get_isic_list(nip_list, session_id)
nips_jsons, nips_errors = get_company_info(METHOD, nips_isics, nips_errors, session_id, JSON_OUTPUT_PATH)
output = get_output(parse_company_info(nips_jsons, nips_errors))

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))
