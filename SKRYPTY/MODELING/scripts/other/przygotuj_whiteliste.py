import numpy as np
import pandas as pd

from datetime import date, datetime, timedelta

gus_c_file = r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\GUS\CLOSED_GUS.xlsx"
gus_l_file = r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\GUS\LIQUIDATED_GUS.xlsx"
data_vat = pd.read_excel(r"C:\Users\mmandziej001\Desktop\Projects\VATCHECK\OUTPUT_API\OUT\CLOSED_INVESTIGATED_2020-07-31.xlsx",
                         converters={'NIP': str})[['NIP']]

keep_cols = [
    'CompanyName', 'NIP', 'REGON', 'KRS', 'DateRozpoczeciaMin',
    'DataZawieszeniaDzialalnosci', 'DataZakonczeniaDzialalnosci',
    'DataSkresleniaREGON', 'DataZaistnieniaZmiany']
data_c = pd.read_excel(gus_c_file, converters={'NIP': str, 'REGON': str, 'KRS': str})[keep_cols]
data_l = pd.read_excel(gus_l_file, converters={'NIP': str, 'REGON': str, 'KRS': str})[keep_cols]

data_c['Status'] = 'Closed'
data_l['Status'] = 'Liquidated'

data = pd.concat([data_c, data_l])
#data = data[~pd.isnull(data['NIP'])]
#nips_all = list(data['NIP'])
#nips_vat = list(data_vat['NIP'])

#nips_missing = list(set(nips_all) - set(nips_vat))

#data = data[np.isin(data['NIP'], nips_missing, invert=True)]

# change col format
data['DateRozpoczeciaMin'] = pd.to_datetime(data.DateRozpoczeciaMin.fillna(pd.NaT))
data['DataZawieszeniaDzialalnosci'] = pd.to_datetime(data.DataZawieszeniaDzialalnosci.fillna(pd.NaT))
data['DataZakonczeniaDzialalnosci'] = pd.to_datetime(data.DataZakonczeniaDzialalnosci.fillna(pd.NaT))
data['DataSkresleniaREGON'] = pd.to_datetime(data.DataSkresleniaREGON.fillna(pd.NaT))
data['DataZaistnieniaZmiany'] = pd.to_datetime(data.DataZaistnieniaZmiany.fillna(pd.NaT))

##
data['CheckDate1'] = np.where(~pd.isnull(data['DataZawieszeniaDzialalnosci']),
                              pd.to_datetime(data['DataZawieszeniaDzialalnosci']),
                              pd.NaT)
data['CheckDate1'] = pd.to_datetime(data.CheckDate1.fillna(pd.NaT), errors='coerce')

data['CheckDate2'] = np.where(~pd.isnull(data['DataSkresleniaREGON']),
                              pd.to_datetime(data['DataSkresleniaREGON']),
                              data['CheckDate1'])
data['CheckDate2'] = pd.to_datetime(data.CheckDate2.fillna(pd.NaT), errors='coerce')

data['CheckDate3'] = np.where(~pd.isnull(data['DataZakonczeniaDzialalnosci']),
                              pd.to_datetime(data['DataZakonczeniaDzialalnosci']),
                              data['CheckDate2'])
data['CheckDate3'] = pd.to_datetime(data.CheckDate3.fillna(pd.NaT), errors='coerce')

data['CheckDate4'] = np.where(pd.isnull(data['CheckDate3']),
                              pd.to_datetime(data['DataZaistnieniaZmiany']),
                              data['CheckDate3'])
data['CheckDate4'] = pd.to_datetime(data.CheckDate4.fillna(date.today()), errors='coerce')

data['CheckDate5'] = np.where(data['CheckDate4'] > datetime.today(),
                              datetime.today().date(),
                              data['CheckDate4'])
data['CheckDate5'] = pd.to_datetime(data.CheckDate5.fillna(date.today()), errors='coerce')


data['FinalCheckDate'] = data['CheckDate4']# - timedelta(days=365)
data['FinalCheckDate'] = pd.to_datetime(data.FinalCheckDate.fillna(pd.NaT), errors='coerce')
data['FinalCheckDateMonth'] = pd.to_datetime(data.FinalCheckDate).dt.to_period('M').dt.to_timestamp()
data = data.sort_values(by='FinalCheckDate',
                        ascending=True)
data[['NIP', 'REGON', 'KRS', 'FinalCheckDate']].to_excel(r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\daty_upadlosci.xlsx", index=False)


####
data = pd.read_excel(r"C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\POLAND_DANE\WHITELISTA\dociag.xlsx",
                     converters={'REGON': str, 'KRS': str})

nip_list = [str(i) for i in data['REGON']]
dates_list = [str(i)[:10] for i in data['CheckDate']]


sliced_dict = {}
sliced_valid_ids_list = []
start_param = 0
if len(nip_list) >= 30:
    end_param = 30
    if len(nip_list) < 300:
        print("Input shall be divided into %s batches." % ceil(len(nip_list)/30))
    else:
        print("""Input shall be divided into {} batches.
              Warning: According to doccumentation input to big to collect all data.
              Please downsize to 300 entites at most.""".format(ceil(len(nip_list)/30)))
else:
    end_param = len(nip_list)
    sliced_valid_ids_list.append(','.join(nip_list[start_param:end_param]))

while len(nip_list) > end_param:
    sliced_ids = ','.join(nip_list[start_param:end_param])
    sliced_valid_ids_list.append(sliced_ids)
    sliced_dict[sliced_ids] = dates_list[start_param]
    start_param += 30
    print('Prawie koniec' + str(start_param))
    if len(nip_list) - end_param <= 30:
        end_param = len(nip_list)
        sliced_ids = ','.join(nip_list[start_param:end_param])
        sliced_valid_ids_list.append(sliced_ids)
        print("Input successfully divided into {} batches.".format(len(sliced_valid_ids_list)))
        break
    else:
        end_param += 30
