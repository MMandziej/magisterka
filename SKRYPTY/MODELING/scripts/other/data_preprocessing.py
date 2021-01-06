import numpy as np
import os
import pandas as pd
import pyodbc

from datetime import date, datetime, timedelta

os.chdir(r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE')

### CONNECT TO DATABASE ###
server = 'localhost\SQLEXPRESS01'
database = 'modeling'

def export_data_to_db(server: str,
                      database: str,
                      data_to_append: pd.DataFrame,
                      table_name: str):

    # establish connection with database
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                           SERVER=' + server + '; \
                           DATABASE=' + database + ';\
                           Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    cols = list(data_to_append)

    # append list with value to insert into table
    insert_values_list = []
    for num, a in data_to_append.iterrows():
        single_insert_list = [x for x in data_to_append.loc[num]]
        list_to_str = "', '".join(str(elem) for elem in single_insert_list)
        single_values = "('{}')".format(list_to_str)
        single_values = single_values.replace(", 'nan'", ", NULL")
        insert_values_list.append(single_values)

    insert_values = ", \n".join(str(val) for val in insert_values_list)
    all_cols = ", ".join('[' + str(header) + ']' for header in cols)
    insert_statement = f"INSERT INTO {table_name} ({all_cols}) VALUES {insert_values}"

    try:
        cursor.execute(insert_statement)
        print(f"Data sucessfully exported into {table_name}.")

    except pyodbc.ProgrammingError:
        print(f"Could not insert values into {table_name} table.")

    cursor.commit()
    cursor.close()
    cnxn.close()

### PREPARE VATCHECK ###
print('Reading VAT')
vat_inv = pd.read_excel(r'WHITELISTA\CLOSED_INVESTIGATED_2020-07-31.xlsx', converters={'REGON': str, 'NIP': str, 'DKN': str})
vat_inv['DeclaredAccountsCount'] = vat_inv['AccountNumbers'].str.count(',') + 1
vat_inv['RepresentativesCount'] = vat_inv['Representatives'].str.count('PESEL')
vat_inv['AuthorizedClerksCount'] = vat_inv['AuthorizedClerks'].str.count('PESEL')
vat_inv['ProxyPersons'] = vat_inv['Proxy'].str.count('PESEL')
vat_inv['ProxyCompanies'] = vat_inv['Proxy'].str.count('NIP')
vat_inv['RepresentationCount'] = vat_inv[['RepresentativesCount', 'AuthorizedClerksCount',
                                          'ProxyPersons', 'ProxyCompanies']].sum(axis=1)
vat_inv['RepresentationCount'] = np.where(pd.isnull(vat_inv['CompanyName']), np.nan, vat_inv['RepresentationCount'])
vat_inv = vat_inv[[
    'CompanyName', 'NIP', 'REGON', 'KRS', 'EntityListedInVATRegistry',
    'StatusVAT', 'IncorrectAccountsDetected', 'VirtualAccountsPresence',
    'RegistrationLegalDate', 'RegistrationDenialDate', 'RegistrationDenialBasis',
    'RemovalDate', 'RemovalBasis', 'RiskyRemovalBasis', 'RestorationDate',
    'RestorationBasis', 'CheckDate', 'DeclaredAccountsCount', 'RepresentationCount']]
vat_inv.to_excel(r'MODELING\VATCHECK\CLOSED_LIQUIDATED_VATCHECK.xlsx', index=False)
#export_data_to_db(server=server, database=database,
#                  data_to_append=vat_inv,
#                  table_name='[vat].[operational]')

print('Reading GUS')
### PREPARE GUS ###
gus_inv = pd.read_excel(r'GUS\LIQUIDATED_GUS.xlsx', converters={'REGON': str, 'NIP': str, 'KRS': str})
gus_inv = gus_inv[~pd.isnull(gus_inv['DataUpadlosci'])]
gus_inv['TD'] = pd.to_datetime("now").normalize()
gus_inv['Wiek'] = (gus_inv['DataUpadlosci'] - gus_inv['DateRozpoczeciaMin']).dt.days
gus_inv['SecondaryPKDCount'] = gus_inv['SecondaryPKDs'].str.count(',') + 1
gus_inv['NoMailAdress'] = np.where(pd.isnull(gus_inv['AdresEmail']), 1, 0)
gus_inv['NoFax'] = np.where(pd.isnull(gus_inv['FAX']), 1, 0)
gus_inv['SecondaryPKDCount'] = np.where(pd.isnull(gus_inv['CompanyName']), np.nan, gus_inv['SecondaryPKDCount'])
gus_inv['NoMailAdress'] = np.where(pd.isnull(gus_inv['CompanyName']), np.nan, gus_inv['NoMailAdress'])
gus_inv['NoFax'] = np.where(pd.isnull(gus_inv['CompanyName']), np.nan, gus_inv['NoFax'])
del gus_inv['TD']
### PREPARE LICENCES ###
ure = pd.read_excel(r'KONCESJE\ure.xlsx', converters={'REGON': str, 'NIP': str, 'KRS': str, 'DKN': str})
gus_inv['ActiveLicenses'] = gus_inv['NIP'].map(ure[ure['Status koncesji'] == 'aktywna']['NIP'].value_counts())
gus_inv['RevertedLicenses'] = gus_inv['NIP'].map(ure[ure['Status koncesji'] == 'cofnięta']['NIP'].value_counts())
gus_inv['ExpiredLicenses'] = gus_inv['NIP'].map(ure[ure['Status koncesji'] == 'wygaszona']['NIP'].value_counts())
gus_inv = gus_inv[[
    'CompanyID', 'CompanyName', 'NIP', 'REGON', 'KRS', 'Wiek', 'DateRozpoczeciaMin',
    'Country', 'Voivodeship', 'City', 'PostalCode', 'DataWznowieniaDzialalnosci',
    'DataZawieszeniaDzialalnosci', 'DataZakonczeniaDzialalnosci', 'DataWpisuDoRejestru',
    'DataWpisuREGON', 'DataSkresleniaREGON', 'DataZaistnieniaZmiany',
    'LegalForm', 'RodzajRejestru', 'FormaFinansowania', 'FormaWlasnosci',
    'JednostkiLokalne', 'SpecialLegalForm', 'MainPKD', 'Brak danych w GUS',
    'Dzialalnosc zawieszona (i niewznowiona)', 'Ryzykowna działalnosc główna',
    'Ryzykowne działalnosci dodatkowe', 'Brak strony WWW', 'Adres email na domenie publicznej',
    'Podmiot zarejestrowany pod adresem wirtualnego biura', 'Adres z numerem lokalu',
    'CAAC import', 'CAAC eksport', 'SecondaryPKDCount', 'NoMailAdress', 'NoFax',
    'ActiveLicenses', 'RevertedLicenses', 'ExpiredLicenses']]
gus_inv.to_excel(r'MODELING\GUS\LIQUIDATED_GUS.xlsx', index=False)
#export_data_to_db(server=server, database=database,
#                  data_to_append=gus_inv,
#                  table_name='[gus].[operational]')

print('Reading REGISTER')
### PREPARE REGISTER ###
register_inv = pd.read_excel(r'REGISTER\EMIS_REGISTER_OPERATIONAL_2020-08-01.xlsx', converters={'REGON': str,
                                                                                           'NIP': str,
                                                                                           'KRS': str,
                                                                                           'EMISID': str})
register_inv['MainNAICSCodes'] = register_inv['MainNAICSCodes'].str[:3]
register_inv['SecondaryNAICSCount'] = register_inv['SecondaryNAICSCodes'].str.count(',') + 1
register_inv['LatestMarketCapitalization'] = pd.to_numeric(register_inv['LatestMarketCapitalization'],
                                                           downcast='float')
register_inv['LatestMarketCapitalization'] = np.where(pd.isnull(register_inv['LatestMarketCapitalization']),
                                                      0,
                                                      register_inv['LatestMarketCapitalization'])
register_inv = register_inv[[
    'EMISID', 'NIP', 'KRS', 'REGON', 'DataUpadlosci', 'Region', 'AddresFlat', 'City', 'PostalCode',
    'WebsiteNotPresent', 'EmailAdressNotPresent', 'EmailAdressPublic', 'FaxNotPresent',
    'PhoneNotPresent', 'ProfileUpdateDate', 'IncorporationYear', 'LegalForm', 'CompanyType',
    'NumberOfEmployees', 'EmployeeNumberDate', 'LatestMarketCapitalization',
    'ExecutivesCount', 'OwnersCount', 'ExternalIdsOthers', 'MainNAICSCodes',
    'MainNAICSCount', 'MainPKD', 'SecondaryNAICSCount', 'MainProductsNull',
    'DescriptionNull', 'Status', 'RegisteredCapitalValue', 'RegisteredCapitalDate',
    'AuditDate', 'PreviousNamesCount', 'PreviousNameChangeYearsAgo', 'DividendCount',
    'DividendSum', 'SegmentName', 'SegmentStockName', 'AffilatteshipAvg', 'AffiliatesCount']]
register_inv.to_excel(r'MODELING\REGISTER\OPERATIONAL_REGISTER.xlsx', index=False)
#export_data_to_db(server=server, database=database,
#                  data_to_append=register_inv,
#                  table_name='[register].[operational]')
