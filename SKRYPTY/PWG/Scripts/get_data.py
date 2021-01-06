"""
Script used to retrieve different type of data from PWG API based on
available methods and list of companies IDs. The following ID types are
allowed: NIP, REGON, KRS, PWG_ID.
"""

from pwg_ordinary import get_nip_list, get_data

########### DEFINE METHOD ############
METHOD = 'getFinanceStatus'
FISCAL_YEAR = ''

### DEFINE INPUT AND OUTPUT FILES ####
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\PWG\INPUT_API\NIP_list.xlsx'
JSONS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\GET_FULL\\'

############ GET OUTPUT #############
nip_list = get_nip_list(INPUT_FILE)
output = get_data(METHOD, nip_list, JSONS_OUTPUT_PATH)


"""
from pwg_ordinary import request_data

results = []
for zam_id in [44928, 44925, 44926, 44927]:
    results.append(request_data(METHOD, str(zam_id), ''))
"""