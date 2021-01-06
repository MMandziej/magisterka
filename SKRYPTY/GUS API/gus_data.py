import os
import numpy as np
import pandas as pd

from copy import deepcopy
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from gusregon import PUBLIC_DOMAINS, RISKY_PKDS, AGRARIAN_PKDS, CAAC_IMPORT, CAAC_EXPORT, offices, \
    pkds_opis, get_data_gus, parse_reports, parse_pkd, export_gus_to_sql, export_coordinates_to_sql, check_none

#from keys_coded import GHC_CREDS_SQL_ALCHEMY, PROJECT_NAME

os.chdir(r"C:\Users\mmandziej001\Desktop\Projects\GUS API")

INPUT_FILE = r"C:\Users\mmandziej001\Desktop\Projects\GUS API\NIP_list.xlsx"
XLSX_OUTPUT_PATH = r"C:\Users\mmandziej001\Desktop\Projects\GUS API\\"
CLIENT_PKD = '2219Z'
# Kauf - 4711Z Metalimex - 2219Z Mall - 4791Z


def calculate_gus_tests(parsed_gus_reports: dict) -> pd.DataFrame:
    # lista ryzykownych pkd bez pkd klienta
    risky_pkds_no_client = deepcopy(RISKY_PKDS)
    if CLIENT_PKD in risky_pkds_no_client:
        risky_pkds_no_client.remove(CLIENT_PKD)

    nip_tests = {}
    # ref_date = date(2015, 1, 1)
    # ref_date = date.today() - timedelta(days=365 * 5)
    # testy dane rejestrowe
    count = 0
    for company_id, table in parsed_gus_reports.items():
        tests_dict = {}
        if table:
            try:
                tests_dict['Brak danych w GUS'] = 0
                tests_dict['Dzialalnosc zawieszona (i niewznowiona)'] = 1 if (
                    table['DataZawieszeniaDzialalnosci'] and not table['DataWznowieniaDzialalnosci']) else 0
                tests_dict['Dzialalnosc zakonczona'] = 1 if table['DataZakonczeniaDzialalnosci'] else 0

                # Testy PKD
                tests_dict['Ryzykowna działalnosc główna'] = 1 if table['MainPKD'].strip() in RISKY_PKDS else 0
                tests_dict['Ryzykowna działalnosc główna (bez działalności klienta)'] = 1 if \
                    (table['MainPKD'].strip() in risky_pkds_no_client) else 0
                tests_dict['Ryzykowne działalnosci dodatkowe'] = 0
                tests_dict['Ryzykowne działalnosci dodatkowe (bez działalności klienta)'] = 0
                for sec_pkd in list(table['SecondaryPKDs'].split(", ")):
                    if sec_pkd in RISKY_PKDS and sec_pkd in risky_pkds_no_client:
                        tests_dict['Ryzykowne działalnosci dodatkowe'] = 1
                        tests_dict['Ryzykowne działalnosci dodatkowe (bez działalności klienta)'] = 1
                    elif sec_pkd in RISKY_PKDS and sec_pkd not in risky_pkds_no_client:
                        tests_dict['Ryzykowne działalnosci dodatkowe'] = 1
                    elif sec_pkd not in RISKY_PKDS and sec_pkd in risky_pkds_no_client:
                        tests_dict['Ryzykowne działalnosci dodatkowe (bez działalności klienta)'] = 1

                tests_dict['Brak strony WWW'] = 1 if not table['AdresWWW'] else 0
                domain1 = table['AdresEmail'][table['AdresEmail'].find('@'):].strip().upper()
                domain2 = table['AdresEmail2'][table['AdresEmail2'].find('@'):].strip().upper()
                for i in PUBLIC_DOMAINS:
                    if i in domain1 or i in domain2:
                        tests_dict['Adres email na domenie publicznej'] = 1
                        break
                    else:
                        tests_dict['Adres email na domenie publicznej'] = 0

                address_df = pd.DataFrame({'city': check_none(table['City']),
                                           'code': check_none(table['PostalCode']),
                                           'building': check_none(table['Building'])}, index=[0])
                merged_inner = pd.merge(left=address_df,
                                        right=offices,
                                        left_on=['city', 'code', 'building'],
                                        right_on=['miasto', 'kod_pocztowy', 'Numer_domu'])
                tests_dict['Podmiot zarejestrowany pod adresem wirtualnego biura'] = 1 if (
                    len(merged_inner) > 0) else 0

                tests_dict['Firma zalożona po 1 stycznia 2015 roku'] = 1 if \
                    table['DateRozpoczeciaMin'] > date(2015, 1, 1) else 0
                tests_dict['Adres z numerem lokalu'] = 1 if table['FlatNumber'] else 0
                tests_dict['CAAC import'] = 1 if company_id in CAAC_IMPORT or table['NIP'] in CAAC_IMPORT else 0
                tests_dict['CAAC eksport'] = 1 if company_id in CAAC_EXPORT or table['NIP'] in CAAC_EXPORT else 0

                # młody podmiot
                if table['DateRozpoczeciaMin'] > date.today() - relativedelta(months=+3):
                    tests_dict['Wiek poniżej 3 msc'] = 1
                    tests_dict['Wiek 3-6 msc'] = 0
                    tests_dict['Wiek 6-9 msc'] = 0
                elif table['DateRozpoczeciaMin'] > date.today() - relativedelta(months=+6):
                    tests_dict['Wiek poniżej 3 msc'] = 0
                    tests_dict['Wiek 3-6 msc'] = 1
                    tests_dict['Wiek 6-9 msc'] = 0
                elif table['DateRozpoczeciaMin'] > date.today() - relativedelta(months=+12):
                    tests_dict['Wiek poniżej 3 msc'] = 0
                    tests_dict['Wiek 3-6 msc'] = 0
                    tests_dict['Wiek 6-12 msc'] = 1
                else:
                    tests_dict['Wiek poniżej 3 msc'] = 0
                    tests_dict['Wiek 3-6 msc'] = 0
                    tests_dict['Wiek 6-12 msc'] = 0
            except:
                print("Couldn't parse data for: ", company_id)
        else:
            tests_dict['Brak danych w GUS'] = 1
            tests_dict['Dzialalnosc zawieszona (i niewznowiona)'] = np.nan
            tests_dict['Dzialalnosc zakonczona'] = np.nan
            tests_dict['Ryzykowna działalnosc główna'] = np.nan
            tests_dict['Ryzykowna działalnosc główna (bez działalności klienta)'] = np.nan
            tests_dict['Ryzykowne działalnosci dodatkowe'] = np.nan
            tests_dict['Ryzykowne działalnosci dodatkowe (bez działalności klienta)'] = np.nan
            tests_dict['Brak strony WWW'] = np.nan
            tests_dict['Adres email na domenie publicznej'] = np.nan
            tests_dict['Podmiot zarejestrowany pod adresem wirtualnego biura'] = np.nan
            tests_dict['Firma zalożona po 1 stycznia 2015 roku'] = np.nan
            tests_dict['Adres z numerem lokalu'] = np.nan
            tests_dict['CAAC import'] = np.nan
            tests_dict['CAAC eksport'] = np.nan
            tests_dict['Wiek poniżej 3 msc'] = np.nan
            tests_dict['Wiek 3-6 msc'] = np.nan
            tests_dict['Wiek 6-12 msc'] = np.nan
        nip_tests[company_id] = tests_dict
        count += 1

    tests_df = pd.DataFrame(nip_tests).T.reset_index().rename(columns={'index': 'CompanyID'})
    tests_df[tests_df.columns[1:]] = tests_df[tests_df.columns[1:]].apply(pd.to_numeric, errors='coerce')
    tests_df_final = tests_df.sort_values(by=['CompanyID'], na_position='last')
    print("Tests calculated for %d out of %d entities." % (count, len(parsed_gus_reports)))
    return tests_df_final


def create_output(reports: dict, pkds: dict, out_path: str) -> tuple:
    parsed_all = {}
    for (k, v), (k2, v2) in zip(reports.items(), pkds.items()):
        if k == k2:
            parsed_all[k] = v
            parsed_all[k].update(v2)

    date_cols = ['DataPowstania', 'DataRozpoczeciaDzialalnosci', 'DateRozpoczeciaMin',
                 'DataWznowieniaDzialalnosci', 'DataZakonczeniaDzialalnosci', 'DataZaistnieniaZmiany',
                 'DataZawieszeniaDzialalnosci', 'DataWpisuDoRejestru', 'DataWpisuREGON', 'DataSkresleniaREGON']

    gus_tests = calculate_gus_tests(parsed_all)
    reports_df = pd.DataFrame(reports).T.reset_index().rename(columns={'index': 'CompanyID'})
    pkd_df = pd.DataFrame(pkds).T.reset_index().rename(columns={'index': 'CompanyID'})
    full_data = pd.DataFrame(parsed_all).T.reset_index().rename(columns={'index': 'CompanyID'})
    reports_df[date_cols] = reports_df[date_cols].apply(pd.to_datetime,
                                                        errors='ignore',
                                                        format='%d-%m-%Y')
    full_data[date_cols] = full_data[date_cols].apply(pd.to_datetime,
                                                      errors='ignore',
                                                      format='%d-%m-%Y')

    full_output = full_data.merge(gus_tests, how='left', on='CompanyID')
    addresses = full_output[['CompanyID', 'AddressSummary']]
    addresses = addresses.assign(lat=np.nan, lng=np.nan, status=np.nan, method=np.nan)
    addresses.rename(columns={'CompanyID': 'NIP',
                              'AddressSummary': 'address'}, inplace=True)
    with pd.ExcelWriter(out_path + 'GUS_OUTPUT_' + str(date.today()) + '.xlsx') as writer:
        full_output.to_excel(writer, 'Total', index=False)
        full_data.to_excel(writer, 'Data', index=False)
        gus_tests.to_excel(writer, 'FAIT_TESTS', index=False)
        reports_df.to_excel(writer, 'Report', index=False)
        pkd_df.to_excel(writer, 'PKD', index=False)
        addresses.to_excel(writer, 'Geocoding', index=False)
    print("Output successfully created and exported.")
    return full_output, addresses


# get data
data = pd.read_excel(INPUT_FILE, dtype=str, header=None)
nip_list = list(data[0])
# addresses = get_data_gus(nip_list, 2)
reports = get_data_gus(nip_list, 1)
pkds = get_data_gus(nip_list, 3)

# parsed_addresses = parse_address(addresses)
# address_df = pd.DataFrame(parsed_addresses).T.reset_index()
parsed_reports, incorrect_reports = parse_reports(reports)
parsed_pkds, incorrect_pkds = parse_pkd(pkds)
full_output, addresses_geocoding = create_output(parsed_reports, parsed_pkds, XLSX_OUTPUT_PATH)
#export_coordinates_to_sql(PROJECT_NAME, GHC_CREDS_SQL_ALCHEMY, addresses_geocoding)
#export_gus_to_sql(PROJECT_NAME, GHC_CREDS_SQL_ALCHEMY, full_output)
