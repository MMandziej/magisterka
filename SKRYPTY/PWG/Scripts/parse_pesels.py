import pandas as pd
import re

from datetime import date
from pwg_ordinary import get_nip_list, get_data


#################### USER PART ####################
##### DEFINE INPUT, OUTPUT FILES AND METHOD  ######
INPUT_FILE = r'C:\Users\mmandziej001\Desktop\Projects\PWG\INPUT_API\NIP_list.xlsx'
JSONS_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_API\GET_FULL\\'
XLSX_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\PWG\OUTPUT_PARSE\\'
DOWNLOAD_TYPE = 'person'


def parse_linked_entities(getFull_jsons: dict, download_type: 'company') -> pd.DataFrame:
    results = []
    guid = 'COMPANY'
    
    def validate_pesel(pesel_str):
        matches = re.findall(r'\d{11}', pesel_str)
        if matches:
            return "".join(matches)
        else:
            return None
    
    if download_type == 'company' or len(list(getFull_jsons.keys())[0]) != 11:
        for company_id, value in getFull_jsons.items():
            table = value['data']
            for person in table['roles']:
                results.append({'CompanyID': company_id,
                                'Imie' : person['name'].upper(),
                                'Nazwisko': person['surname'].upper(),
                                'PESEL': validate_pesel(person['pesel']),
                                'Stanowisko': person['rola'],
                                'Rola': person['rola2'],
                                'Start': person['start'],
                                'Koniec': person['koniec'],
                                'Aktualnosc': 'Current'})
            for person_hist in table['roleshistory']:
                results.append({'CompanyID': company_id,
                                'Imie' : person_hist['name'].upper(),
                                'Nazwisko': person_hist['surname'].upper(),
                                'PESEL': validate_pesel(person_hist['pesel']),
                                'Stanowisko': person_hist['rola'],
                                'Rola': person_hist['rola2'],
                                'Start': person_hist['start'],
                                'Koniec': person_hist['koniec'],
                                'Aktualnosc': 'Former'})
            print('Data parsed for %s.' % company_id)

    elif download_type == 'person' or len(list(getFull_jsons.keys())[0]) == 11:
        guid = 'PERSON'
        for pesel, value in getFull_jsons.items():
            table = value['data']
            name, surname = table['name'], table['surname']
            firmy = table['firmy']
            for company_id, value in firmy.items():
                roles = value['rola']
                for funkcja in roles:
                    for i in roles[funkcja]['daty']:
                        results.append({'PESEL': pesel,
                                        'Imie' : name.upper(),
                                        'Nazwisko': surname.upper(),
                                        'NIP': value['nip'],
                                        'REGON': value['regon'],
                                        'KRS': value['krs'],
                                        'Nazwa': value['nazwa'],
                                        'Rola': i['rola'],
                                        'Start': i['start'],
                                        'Koniec': i['koniec'],
                                        'Aktualnosc': 'Current' if (
                                            i['koniec'] == '9999-12-31') else 'Former'})
            print('Data parsed for %s.' % pesel)

    result_df = pd.DataFrame.from_dict(results)
    result_df.to_excel(XLSX_OUTPUT_PATH + 'PWG_BTT_SPYDER_' + guid + '_' +
                       str(date.today()) + '.xlsx', sheet_name='BTT', index=False)
    return result_df


################### GET OUTPUT ###################
company_ids_list = get_nip_list(INPUT_FILE)
company_ids_jsons, company_ids_errors = get_data('getFull', company_ids_list, JSONS_OUTPUT_PATH)
parsed_data = parse_linked_entities(company_ids_jsons, DOWNLOAD_TYPE)

