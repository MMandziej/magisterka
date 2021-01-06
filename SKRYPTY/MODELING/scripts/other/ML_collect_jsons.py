import datetime as d
import os
import json
import pandas as pd

XLXS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\\'

path_to_json = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\EMIS\FULL'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

jsons_valid = []
for j in json_files:
    if "INVALID" not in j:
        jsons_valid.append(j)

jsons_loaded = []
nips = []
jsons_wrong = []
for i in jsons_valid:
    with open(os.path.join(path_to_json, i), encoding="utf8") as json_file:
        try:
            json_text = json.load(json_file)
            nip = i[:10]
            jsons_loaded.append(json_text)
            nips.append(nip)
        except:
            jsons_wrong.append(i)

for nip, j in zip(nips, jsons_loaded):
    # DELETE UNCECESSARY DATA FROM DICTS
    for code in ["_type", "auditedStatus", "consolidatedStatus", "countryCode",
                 "displayCurrency", "multiple", "originalCurrency", "period",
                 "stmtCode", "stmtId", "source"]:
        try:
            j.pop(code)
        except KeyError:
            print("For NIP " + nip + "the following key not found: " + code)
    # MAP ISIC WITH NIP
    j['NIP'] = nip   
    # PARSE FINANCIAL FIELDS
    for i in j['accountList']:
        j[i['accountCode']] = i['accountValue']
    # DELETE INITIAL ACCOUNTS LIST
    j.pop('accountList')

output_parsed = pd.DataFrame(jsons_loaded)
output_parsed.rename(columns={
    'acctErrFlag' : 'AccountErrorFlag',
    'beginDate' : 'BeginDate',
    'endDate' : 'EndDate',
    'fsYear' : 'FiscalYear',
    'isic' : 'ISIC',
    'lastUpdate' : 'LastUpdate',
    'originalStandardCode' : 'OriginalStandardCode',
    'outputStandardCode' : 'OutputStandardCode'}, inplace=True)

known_cols = ['NIP', 'ISIC', 'FiscalYear', 'BeginDate', 'EndDate', 'LastUpdate',
              'OriginalStandardCode', 'OutputStandardCode', 'AccountErrorFlag']
all_cols = list(output_parsed)
unknown_cols = [c for c in all_cols if c not in known_cols]
cols = known_cols + unknown_cols

output_parsed.fillna('', inplace=True)
output_parsed = output_parsed.astype({
    'NIP':'str',
    'ISIC':'str',
    'BeginDate':'str',
    'EndDate':'str',
    'LastUpdate':'str',
    'OriginalStandardCode':'str',
    'OutputStandardCode':'str',
    'AccountErrorFlag':'str'}) 

output_parsed = output_parsed[cols].sort_values(by=['NIP', 'FiscalYear'], na_position='last')    
with pd.ExcelWriter(XLXS_OUTPUT_PATH +
                    'PredictionModule_FINANCE' +
                    str(d.date.today()) +
                    '.xlsx') as writer:
                    output_parsed.to_excel(writer, 'Total', index=False)
    
    
"""
types = []
flags = []
audited = []
country_codes = []
original_currency = []
currency_displayed = []
multiple = [] 
period = []
source = []
originalStandardCode = []

flags.append(j['acctErrFlag'])
audited.append(j['auditedStatus'])
country_codes.append(j['countryCode'])
original_currency.append(j['originalCurrency'])
currency_displayed.append(j['displayCurrency'])
multiple.append(j['multiple'])
period.append(j['period'])
source.append(j['source'])
originalStandardCode.append(j['originalStandardCode'])


dist_types = list(set(types))
dist_flags = list(set(flags))
dist_audited = list(set(audited))
dist_country_codes = list(set(country_codes))
dist_original_currency = list(set(original_currency))
dist_currency_displayed = list(set(currency_displayed))
dist_multiple = list(set(multiple))
dist_period = list(set(period))
dist_source = list(set(source))
dist_originalStandardCode = list(set(originalStandardCode))
"""
