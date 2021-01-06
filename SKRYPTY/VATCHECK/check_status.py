"""
Script used to retrieve and parse data from MF API based on
search and check methods and list of companies IDs.

Data are processed and exported to xlsx file and/or SQL table and
used for investigating analysis purposes and FAIT project.
"""

import json
import numpy as np
import pandas as pd
import pyodbc
import time as t

from copy import deepcopy
from datetime import date

from keys_coded import GHC_CREDS

from vatcheck import get_nip_name, get_vat_status, slice_export_jsons, check_shared_accs, \
    parse_vat_status, create_output, export_output, export_vatcheck_to_sql, \
    calculate_removal_datediff, score_removal_reason, initial_cols, cols_rename, known_cols

START = t.time()

############################ USER PART ###########################
######## DEFINE METHOD, ID CLASS, INPUT NAD OUTPUT PATHS #########
ID_CLASS = 'NIP'
INPUT_FILE = r"C:\Users\mmandziej001\Desktop\Projects\VATCHECK\ID_LIST.xlsx"
BATCH_OUTPUT_PATH = r"C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\JSONS\BATCH_JSONS\\"
JSON_OUTPUT_PATH = r"C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\JSONS\SINGLE_JSONS\\"
XLSX_OUTPUT_PATH = r"C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\\"
PROJECT_NAME = "Mall7_20200225"


#################### GET OUTPUT ##################
### CREATE LIST OF COMPANY IDS FROM INPUT FILE ###

nip_list, nips_invalid, log_df, client_nips_accounts = get_nip_name(INPUT_FILE, ID_CLASS)
nips_jsons, nips_errors = get_vat_status(ID_CLASS, nip_list, BATCH_OUTPUT_PATH)
merged_jsons = slice_export_jsons(nips_jsons, JSON_OUTPUT_PATH)
parsed_jsons, nips_errors, parsed_nips_accounts = parse_vat_status(merged_jsons,
                                                                   nips_errors,
                                                                   list(log_df.ValidNIP),
                                                                   client_nips_accounts)
all_accounts, shared_accs = check_shared_accs(parsed_nips_accounts)
vat_output = create_output(parsed_jsons, nips_errors)
export_output(vat_output, log_df, XLSX_OUTPUT_PATH)
# table = export_vatcheck_to_sql(PROJECT_NAME, GHC_CREDS, vat_output[0])

END = t.time()
execution_time = END - START
print("Execution time: ", str(execution_time))
