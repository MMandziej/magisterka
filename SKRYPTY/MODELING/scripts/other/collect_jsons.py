import os
import json

################## USER PART ##################
######## DEFINE INPUT NAD OUTPUT PATHS ########
PATH_TO_JSONS = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\REGISTER\Operational\ALL'
XLXS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\IDEA\DANE\Dane_Wnioski_v2\VATCHECK\\'
############# END OF USER PART ################

def collect_json_files(jsons_path: str) -> list:
    nips_jsons = {}
    nips_errors = {}
    nips = [file[:10] for file in os.listdir(jsons_path) if
            file.endswith('.json') and "INVALID" not in file]
    jsons_valid = [file for file in os.listdir(jsons_path) if
                   file.endswith('.json') and "INVALID" not in file]

    for nip, file in zip(nips, jsons_valid):
        with open(os.path.join(PATH_TO_JSONS, file), encoding="utf8") as json_file:
            try:
                json_text = json.load(json_file)
                nips_jsons[nip] = json_text
            except:
                nips_errors[nip] = file
    return nips_jsons, nips_errors

############### GET OUTPUT ##################
jsons_loaded, jsons_invalid = collect_json_files(PATH_TO_JSONS)
