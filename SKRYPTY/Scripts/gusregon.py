from datetime import date
import pandas as pd
import pyodbc

from bs4 import BeautifulSoup, Tag
from requests import Session
from sqlalchemy import create_engine
from zeep import Client, Transport

from keys_coded import PRG_CREDS, GHC_CREDS, PRG_CREDS_SQL_ALCHEMY

#from .version import __version__
__version__ = '1.1.3'
WSDL = 'https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/wsdl/UslugaBIRzewnPubl.xsd'
ENDPOINT = 'https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc'
ENDPOINT_SANDBOX = 'https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc'

class GUS(object):
    endpoint = ENDPOINT
    headers = {'User-Agent': 'gusregon/%s' % __version__}
    pkd_report_type = {
        'F': 'PublDaneRaportDzialalnosciFizycznej',
        'P': 'PublDaneRaportDzialalnosciPrawnej'}
    report_type = {
        'F': {
            '1': 'PublDaneRaportDzialalnoscFizycznejCeidg',
            '2': 'PublDaneRaportDzialalnoscFizycznejRolnicza',
            '3': 'PublDaneRaportDzialalnoscFizycznejPozostala',
            '4': 'PublDaneRaportDzialalnoscFizycznejWKrupgn'},
        'LF': 'PublDaneRaportLokalnaFizycznej',
        'P': 'PublDaneRaportPrawna',
        'LP': 'PublDaneRaportLokalnaPrawnej'}

    def __init__(self, api_key=None, sandbox=False):
        if not any([api_key, sandbox]):
            raise AttributeError('Api key is required.')
        self.api_key = api_key
        self.sandbox = sandbox
        if sandbox:
            self.api_key = api_key or 'abcde12345abcde12345' # d98f6764bb7849dc84f3 # abcde12345abcde12345
            self.endpoint = ENDPOINT_SANDBOX
        transport = Transport(session=Session())
        transport.session.headers = self.headers
        client = Client(WSDL, transport=transport)
        self.service = client.create_service('{http://tempuri.org/}e3', self.endpoint)
        self.headers.update({'sid': self._service('Zaloguj', self.api_key)})

    def _service(self, action, *args, **kwargs):
        service = getattr(self.service, action)
        return service(*args, **kwargs)

    def _remove_prefix(self, data):
        data = {item.name: item.get_text()
                for item in BeautifulSoup(data, 'lxml').dane if isinstance(item, Tag)}
        parsed_data = {}
        for name, value in data.items():
            parsed_data[name.split('_', 1)[1]] = value.strip()
        return parsed_data

    def _get_details(self, nip=None, regon=None, krs=None):
        if not any([nip, regon, krs]):
            raise AttributeError(
                'At least one parameter (nip, regon, krs) is required.')
        if nip:
            search_params = {'Nip': nip}
        elif regon:
            search_params = {'Regon': regon}
        else:
            search_params = {'Krs': krs}
        return self._service('DaneSzukaj', search_params)

    def search(self, *args, **kwargs):
        details = self._get_details(*args, **kwargs)
        if details is not None:
            data = BeautifulSoup(details, 'lxml')
            report_type = self.report_type.get(data.typ.get_text())
            if isinstance(report_type, dict):
                report_type = report_type.get(data.silosid.get_text())
            return self._remove_prefix(self._service(
                'DanePobierzPelnyRaport', data.regon.get_text(), report_type))

    def get_pkd(self, *args, **kwargs):
        pkd = []
        details = self._get_details(*args, **kwargs)
        if details is not None:
            data = BeautifulSoup(details, 'lxml')
            report_type = self.pkd_report_type.get('F')
            if 'P' in data.typ.get_text():
                report_type = self.pkd_report_type.get('P')
            report = self._service(
                'DanePobierzPelnyRaport', data.regon.get_text(), report_type)
            if report is not None:
                for item in BeautifulSoup(report, 'lxml').find_all('dane'):
                    data = {i.name.split('_', 1)[1].replace('_', '').lower(): i.get_text()
                            for i in item.children if isinstance(i, Tag)}
                    pkd.append({
                        'code': data['pkdkod'],
                        'name': data['pkdnazwa'],
                        'main': data['pkdprzewazajace'] == '1'})
                pkd = [dict(t) for t in set([tuple(d.items()) for d in pkd])]
        return pkd

    def get_address(self, *args, **kwargs):
        details = self.search(*args, **kwargs)
        if details:
            postal_code = details['adsiedzkodpocztowy']
            address = '%s %s' % (details['adsiedzulica_nazwa'],
                                 details['adsiedznumernieruchomosci'])
            if details['adsiedznumerlokalu']:
                address += '/%s' % details['adsiedznumerlokalu']
                lokal = details['adsiedznumerlokalu']
            else:
                lokal = False
            return {
                'CompanyName': details['nazwa'],
                'StreetAddress': address,
                'PostalCode': '%s-%s' % (postal_code[:2], postal_code[2:]),
                'City': details['adsiedzmiejscowosc_nazwa'],
                'FlatNumber': lokal}


def get_data_gus(company_id_list: list, info_type: str) -> list:
    gus = GUS(api_key='d98f6764bb7849dc84f3')
    results = []
    count = 0
    for company_id in company_id_list:
        data = {}
        if info_type in [1, 'search']:
            data[company_id] = gus.search(nip=company_id)
        elif info_type in [2, 'address']:
            data[company_id] = gus.get_address(nip=company_id)
        elif info_type in [3, 'pkd']:
            data[company_id] = gus.get_pkd(nip=company_id)
        results.append(data)
        count += 1
        print("Data downloaded for %d out of %d entities. Report type: %s." % (count, len(company_id_list), info_type))
    return results


def parse_reports(report_list: list) -> dict:
    parsed_reports = {}
    incorrect_data = {}

    def trunc_regon(regon):
        truncated_regon = regon
        if len(regon) == 14 and regon[-5:] == '00000':
            truncated_regon = regon[:-5]
        return truncated_regon

    for report_dict in report_list:
        parsed_info = {}
        for company_id, report_dict in report_dict.items():
            if report_dict:
                try:
                    # parsed_info['CompanyID'] = company_id.strip()
                    parsed_info['CompanyName'] = report_dict['nazwa'].strip()
                    parsed_info['NIP'] = report_dict.get('nip', None)
                    parsed_info['REGON'] = trunc_regon(report_dict.get('regon14', report_dict.get('regon9', None)))
                    parsed_info['KRS'] = report_dict.get('numerwrejestrzeewidencji', None)
                    try:
                        parsed_info['DataPowstania'] = date.fromisoformat(report_dict['datapowstania'].strip())
                    except ValueError:
                        parsed_info['DataPowstania'] = report_dict['datapowstania'].strip()
                    try:
                        parsed_info['DataRozpoczeciaDzialalnosci'] = date.fromisoformat(report_dict['datarozpoczeciadzialalnosci'].strip())
                    except ValueError:
                        parsed_info['DataRozpoczeciaDzialalnosci'] = report_dict['datarozpoczeciadzialalnosci'].strip()
                    try:
                        parsed_info['DateRozpoczeciaMin'] = min([parsed_info['DataPowstania'], parsed_info['DataRozpoczeciaDzialalnosci']])
                    except:
                        parsed_info['DateRozpoczeciaMin'] = parsed_info['DataPowstania']
                    parsed_info['Country'] = report_dict.get('adsiedzkraj_nazwa', '')
                    parsed_info['Voivodeship'] = report_dict.get('adsiedzwojewodztwo_nazwa', '')
                    parsed_info['City'] = report_dict.get('adsiedzmiejscowosc_nazwa', '')
                    parsed_info['PostalCode'] = report_dict.get('adsiedzkodpocztowy', '')
                    parsed_info['Street'] = report_dict.get('adsiedzulica_nazwa', '')
                    parsed_info['Building'] = report_dict.get('adsiedznumernieruchomosci', '')
                    parsed_info['FlatNumber'] = report_dict.get('adsiedznumerlokalu', '')
                    parsed_info['AddressSummary'] = parsed_info['City'] + ' ' + parsed_info['PostalCode'] + ' ' + \
                        parsed_info['Street'] + ' ' + parsed_info['Building'] + ' ' + parsed_info['FlatNumber']
                    parsed_info['AdresWWW'] = report_dict['adresstronyinternetowej'].strip() if report_dict['adresstronyinternetowej'] != "" else None
                    parsed_info['AdresEmail'] = report_dict.get('adresemail', None)
                    parsed_info['AdresEmail2'] = report_dict.get('adresemail2', None)
                    parsed_info['FAX'] = report_dict.get('numerfaksu', None)
                    parsed_info['PhoneNumber'] = report_dict.get('numertelefonu', None)
                    parsed_info['DataWznowieniaDzialalnosci'] = report_dict.get('datawznowieniadzialalnosci', None)
                    parsed_info['DataZawieszeniaDzialalnosci'] = report_dict.get('datazawieszeniadzialalnosci', None)
                    parsed_info['DataZakonczeniaDzialalnosci'] = report_dict.get('datazakonczeniadzialalnosci', None)
                    parsed_info['DataWpisuDoRejestru'] = report_dict.get('datawpisudorejestruewidencji', None)
                    parsed_info['DataWpisuREGON'] = report_dict.get('datawpisudoregon', report_dict.get('datawpisudoregondzialalnosci', None))
                    parsed_info['DataSkresleniaREGON'] = report_dict.get('dataskresleniazregon', report_dict.get('dataskresleniazregondzialalnosci', None))
                    parsed_info['DataZaistnieniaZmiany'] = report_dict.get('datazaistnieniazmiany', None)
                    parsed_info['LegalForm'] = report_dict.get('podstawowaformaprawna_nazwa', ' OSOBA FIZYCZNA PROWADZĄCA DZIAŁALNOŚĆ GOSPODARCZĄ')
                    parsed_info['RodzajRejestru'] = report_dict.get('rodzajrejestruewidencji_nazwa', report_dict.get('rodzajrejestru_nazwa', None))
                    parsed_info['FormaFinansowania'] = report_dict.get('formafinansowania_nazwa', None)
                    parsed_info['FormaWlasnosci'] = report_dict.get('formawlasnosci_nazwa', None)
                    parsed_info['JednostkiLokalne'] = report_dict.get('jednosteklokalnych', None)
                    parsed_info['NazwaSkrocona'] = report_dict.get('nazwaskrocona', None).strip()
                    parsed_info['OrganRejestrowy'] = report_dict.get('organrejestrowy_nazwa', None)
                    parsed_info['OrganZalozycielski'] = report_dict.get('organzalozycielski_nazwa', None)
                    parsed_info['SpecialLegalForm'] = report_dict.get('szczegolnaformaprawna_nazwa', None)
                except Exception as e:
                    error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
                    incorrect_data[company_id] = error
                    print( "Couldn't parse: ", company_id)
            else:
                incorrect_data[company_id] = 'No data'
        parsed_reports[company_id] = parsed_info
    return parsed_reports, incorrect_data


def parse_pkd(pkd_list: list) -> dict:
    parsed_pkds = {}
    incorrect_data = {}
    for i in pkd_list:
        parsed_info = {}
        main_pkd_count = 0
        for company_id, company_all_pkd_list in i.items():
            if company_all_pkd_list:
                main_pkds = []
                secondary_pkds = []
                for single_pkd in company_all_pkd_list:
                    if single_pkd['main']:
                        main_pkd_count += 1
                        main_pkds.append(single_pkd['code'])
                    else:
                        secondary_pkds.append(single_pkd['code'])
                for v in main_pkds:
                    if len(main_pkds) > 1 and v in AGRARIAN_PKDS:
                        main_pkds.remove(v)
                parsed_info['MainPKD'] = ', '.join(main_pkds)
                parsed_info['MainPKDOpis'] = pkds_opis.get(parsed_info['MainPKD'], 'n/a')
                parsed_info['SecondaryPKDs'] = ', '.join(sorted(list(secondary_pkds)))
            else:
                incorrect_data[company_id] = 'No data'
            parsed_pkds[company_id] = parsed_info
    return parsed_pkds, incorrect_data


def parse_address(address_list: list) -> dict:
    parsed_addresses = {}
    for i in address_list:
        for company_id, address_dict in i.items():
            parsed_addresses[company_id] = address_dict
    return parsed_addresses


def establish_connection(creds):
   conn = pyodbc.connect(creds)
   cursor=conn.cursor()
   return cursor


def export_coordinates_to_sql(project_name: str,
                              creds: str,
                              addresses_output: pd.DataFrame):
    from sqlalchemy.types import NVARCHAR
    engine = create_engine(creds)
    create_schema_statement = ("IF NOT EXISTS (SELECT schema_name FROM information_schema.schemata"
                               " WHERE schema_name = '{0}') BEGIN EXEC"
                               " sp_executesql N'CREATE SCHEMA {0}' END").format(project_name)
    engine.execute(create_schema_statement)
    addresses_output.to_sql('addresses_coordinates', con=engine, schema=project_name, if_exists='append',
                            index=False, method='multi', dtype={col: NVARCHAR(length=255) for col in addresses_output})
    print("Export to table %s successfull" % (project_name + '.addresses_coordinates'))


def export_gus_to_sql(project_name: str,
                      creds: str,
                      gus_output: pd.DataFrame):
    from sqlalchemy.types import NVARCHAR, Date, Integer

    gus_sql_cols = [
        'CompanyID','CompanyName', 'NIP', 'REGON', 'KRS', 'Country', 'City', 'PostalCode', 'Street', 'Building',
        'FlatNumber', 'AddressSummary', 'AdresWWW', 'LegalForm', 'MainPKD', 'MainPKDOpis', 'SecondaryPKDs',
        'DataPowstania', 'DataRozpoczeciaDzialalnosci', 'DateRozpoczeciaMin', 'DataWznowieniaDzialalnosci',
        'DataZawieszeniaDzialalnosci', 'DataZakonczeniaDzialalnosci', 'Brak danych w GUS',
        'Dzialalnosc zawieszona (i niewznowiona)', 'Dzialalnosc zakonczona', 'Ryzykowna działalnosc główna',
        'Ryzykowna działalnosc główna (bez działalności klienta)', 'Ryzykowne działalnosci dodatkowe',
        'Ryzykowne działalnosci dodatkowe (bez działalności klienta)', 'Brak strony WWW',
        'Adres email na domenie publicznej', 'Podmiot zarejestrowany pod adresem wirtualnego biura',
        'Firma zalożona po 1 stycznia 2015 roku', 'Adres z numerem lokalu', 'CAAC import', 'CAAC eksport']

    cols_dtypes = {**{col: NVARCHAR() for col in gus_sql_cols[:17]},
                   **{col: Date() for col in gus_sql_cols[17:23]},
                   **{col: Integer() for col in gus_sql_cols[23:]}}

    engine = create_engine(creds)
    create_schema_statement = ("IF NOT EXISTS (SELECT schema_name FROM information_schema.schemata"
                               " WHERE schema_name = '{0}') BEGIN EXEC"
                               " sp_executesql N'CREATE SCHEMA {0}' END").format(project_name)
    engine.execute(create_schema_statement)
    gus_output[gus_sql_cols].to_sql('gus_caac', con=engine, schema=project_name, if_exists='replace',
                                    index=False, method=None, dtype=cols_dtypes)
    print("Export to table %s successfull" % (project_name + '.gus_caac'))


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def check_none(x):
    if x is None:
        return ''
    else:
        return x.strip().replace('  ', ' ')


street_replacements = {'ul.': '',
                       'al.': '',
                       'pl.': ''}


PUBLIC_DOMAINS = [
    '@GMAIL', '@WP', '@POCZTA.ONET', '@ONET.', '@OP.PL', '@GAZETA.PL', '@GO2',
    '@YAHOO', '@O2', '@AUTOGRAF.PL', '@BUZIACZEK.PL', '@TLEN.', '@HOTMAIL',
    '@INTERIA.', '@VP', '@GERY.PL', '@AKCJA.PL', '@CZATERIA.PL', '@1GB.PL', '@2GB.PL',
    '@OS.PL', '@SKEJT.PL', '@FUKS.PL', '@ZIOMEK.PL', '@OFERUJEMY.INFO', '@TWOJ.INFO',
    '@TWOJA.INFO', '@BOY.PL', '@NAJX.COM', '@ADRESIK.COM', '@E-MAIL.NET.PL', '@IV.PL',
    '@BAJERY.PL', '@GOG.PL', '@OS.PL', '@SERWUS.PL', '@AOL.PL', '@POCZTA.FM',
    '@LYCOS.CO%', '@WINDOWSLIVE.COM', '@OUTLOOK.COM', '@OVCLOUD', '@AZ.PL', '@FIRMA.PL',
    '@HOME.PL', '@HUB.PL', '@AMORKI.PL', '@POCZTA.GG.PL', '@PINO.PL', '@TENBIT',
    '@NEOSTRADA.PL', '@PW', '@SPOKO.PL', '@PROKONTO.PL', '@ORANGE.PL', '@GG.PL',
    '@PLUSNET.PL', '@VIP.ONET.PL', '@INMAIL.PL', '@KOSZMAIL.PL', '@ASTER.PL',
    '@REPUBLIKA.PL', '@OPOCZTA.PL', '@POCZTA.WP.PLV', '@KONTO.PL', '@PROTONMAIL.COM',
    '@TUTANOTA.COM', '@INT.PL', '@ZOHOMAIL']

"""
RISKY_PKDS_ALL = [
    '6621Z', '6622Z', '6629Z', '6630Z', '6810Z', '6820Z', '6831Z', '6832Z', '6910Z',
    '6920Z', '7010Z', '7021Z', '7022Z', '7311Z', '7312A', '7312B', '7312C', '7320Z',
    '7711Z', '7712Z', '7731Z', '7732Z', '7733Z', '7734Z', '7735Z', '7739Z', '7810Z',
    '8610Z', '8621Z', '8622Z', '8623Z', '8690A', '8690B', '8690C', '8690D', '8690E',
    '8710Z', '8720Z', '8730Z', '8790Z', '0510Z', '0520Z', '0610Z', '0620Z', '0710Z',
    '0729Z', '0910Z', '0990Z', '1610Z', '1621Z', '1622Z', '1623Z', '1724Z', '1920Z',
    '2211Z', '2223Z', '2331Z', '2332Z', '2341Z', '2342Z', '2343Z', '2351Z', '2352Z',
    '2361Z', '2362Z', '2363Z', '2364Z', '2365Z', '2369Z', '2410Z', '2420Z', '2431Z',
    '2432Z', '2433Z', '2434Z', '2441Z', '2442A', '2442B', '2443Z', '2444Z', '2445Z',
    '2446Z', '2451Z', '2452Z', '2453Z', '2454A', '2454B', '2511Z', '2512Z', '2529Z',
    '2540Z', '2550Z', '2561Z', '2562Z', '2571Z', '2572Z', '2573Z', '2591Z', '2592Z',
    '2593Z', '2594Z', '2599Z', '2611Z', '2612Z', '2620Z', '2630Z', '2640Z', '2651Z',
    '2660Z', '2670Z', '2680Z', '2711Z', '2712Z', '2720Z', '2731Z', '2732Z', '2733Z',
    '2740Z', '2751Z', '2752Z', '2790Z', '2811Z', '2812Z', '2813Z', '2814Z', '2815Z',
    '2821Z', '2822Z', '2823Z', '2824Z', '2825Z', '2829Z', '2830Z', '2841Z', '2849Z',
    '2891Z', '2892Z', '2893Z', '2894Z', '2895Z', '2896Z', '2899Z', '2910A', '2910B',
    '2910C', '2910D', '2910E', '2920Z', '2931Z', '2932Z', '3011Z', '3012Z', '3020Z',
    '3030Z', '3040Z', '3091Z', '3315Z', '3316Z', '3317Z', '3521Z', '3522Z', '3523Z',
    '3700Z', '3811Z', '3812Z', '3821Z', '3822Z', '3831Z', '3832Z', '4110Z', '4120Z',
    '4211Z', '4212Z', '4213Z', '4221Z', '4222Z', '4291Z', '4299Z', '4311Z', '4312Z',
    '4313Z', '4321Z', '4322Z', '4329Z', '4331Z', '4332Z', '4333Z', '4334Z', '4339Z',
    '4391Z', '4399Z', '4511Z', '4519Z', '4520Z', '4531Z', '4532Z', '4540Z', '4611Z',
    '4612Z', '4613Z', '4614Z', '4615Z', '4616Z', '4617Z', '4618Z', '4619Z', '4621Z',
    '4631Z', '4632Z', '4633Z', '4634A', '4634B', '4635Z', '4636Z', '4637Z', '4638Z',
    '4639Z', '4643Z', '4649Z', '4651Z', '4652Z', '4661Z', '4662Z', '4663Z', '4664Z',
    '4666Z', '4669Z', '4671Z', '4672Z', '4673Z', '4674Z', '4676Z', '4677Z', '4690Z',
    '4711Z', '4721Z', '4722Z', '4723Z', '4724Z', '4726Z', '4729Z', '4730Z', '4741Z',
    '4742Z', '4743Z', '4752Z', '4754Z', '4781Z', '4791Z', '4910Z', '4920Z', '4931Z',
    '4932Z', '4939Z', '4941Z', '4942Z', '4950A', '4950B', '5010Z', '5020Z', '5030Z',
    '5040Z', '5110Z', '5121Z', '5122Z', '5210A', '5210B', '5221Z', '5222A', '5222B',
    '5223Z', '5224A', '5224B', '5224C', '5229A', '5229B', '5229C', '5320Z', '6201Z',
    '6202Z', '6203Z', '6209Z', '6311Z', '6312Z', '6411Z', '6419Z', '6420Z', '6430Z',
    '6491Z', '6492Z', '6499Z', '6511Z', '6512Z', '6520Z', '6530Z', '6611Z', '6612Z', '6619Z'] """

RISKY_PKDS = [
    '4615Z', '4616Z', '4617Z', '4618Z', '4619Z', '4621Z', '4631Z', '4632Z', '4633Z',
    '4634A', '4634B', '4635Z', '4636Z', '4637Z', '4638Z', '4639Z', '4643Z', '4649Z',
    '4651Z', '4652Z', '4666Z', '4669Z', '4676Z', '4690Z', '4711Z', '4721Z', '4722Z',
    '4723Z', '4724Z', '4726Z', '4729Z', '4741Z', '4742Z', '4743Z', '4754Z', '4791Z']

AGRARIAN_PKDS = [
    '0111Z', '0112Z', '0113Z', '0114Z', '0115Z', '0116Z', '0119Z', '0121Z', '0122Z',
    '0123Z', '0124Z', '0125Z', '0126Z', '0127Z', '0128Z', '0129Z', '0141Z', '0142Z',
    '0143Z', '0144Z', '0145Z', '0146Z', '0147Z', '0149Z', '0150Z', '0170Z', '0210Z',
    '0220Z', '0230Z', '0311Z', '0312Z', '0321Z', '0322Z']


engine = create_engine(PRG_CREDS_SQL_ALCHEMY)
connection = engine.connect()
offices = pd.read_sql_table('Virtual_Offices', connection, columns=['miasto', 'kod_pocztowy', 'Numer_domu'])
pkds_list = pd.read_sql_table('PKD_opis', connection, columns=['SymbolPKD', 'Opis'])
pkds_opis_raw = pd.Series(pkds_list.Opis.values, index=pkds_list.SymbolPKD).to_dict()
pkds_opis = {}
for k, v in pkds_opis_raw.items():
    #k.replace('PKD', '')#.replace('Z', '').replace(' ', '').replace('.', '')
    pkds_opis[k.replace('PKD', '').replace(' ', '').replace('.', '')] = v
    
CAAC_IMPORT = pd.read_sql_table('caac_import_2013_2017', connection, columns=['NIP'])['NIP'].to_list()
CAAC_EXPORT = pd.read_sql_table('caac_eksport_2013_2017', connection, columns=['NIP'])['NIP'].to_list()
