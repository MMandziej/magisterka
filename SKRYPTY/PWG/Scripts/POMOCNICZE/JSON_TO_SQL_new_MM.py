import datetime
import json
import os
import pandas as pd
import numpy as np
import time as t
from pandas.io.json import json_normalize
import sqlalchemy
from sqlalchemy.sql import text
t = t.time()

JSON_DIR = r"C:\Users\mmandziej001\Desktop\Projects\PWG\API_PWG\JSONs_output\getFull_19_02_2019"
database_name = 'MMandziej'
#####################################  FUNCTIONS  #############################
def collect_json_names():
    files = os.listdir(JSON_DIR)
    json_names=[]
    [json_names.append(i) for i in files if i[-4:]=='json']
    return(json_names)


def load_json(json_names):
    json_files = []
    faulty = []
    for file in json_names:
        try:
            with open(JSON_DIR + '\\' + file, encoding="utf8") as f:
                data = json.load(f)
                data = data['result']['data']
                if type(data) is not list:
                    json_files.append(data)
                else:
                    faulty.append(file + ' - empty')
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            faulty.append(file + ' - faulty')
    files = [json_files, faulty]        
    return(files)            


def create_df(valid_json):
    dfs = []
    for i in valid_json:
        (keys,values) = zip(*i.items())
        keys = pd.Series(keys)
        values = pd.Series(values,index=keys)
        dfs.append(values)
    df = pd.DataFrame(dfs, columns=keys)
    return df

def create_outer_table(df, table):
    temp = []
    nip = []
    for row in range(0, len(df[table])):
        try:
            temp.append(json_normalize(df.loc[row, table]))
            nip.append(df.loc[row, 'nip'])
        except:
            pass
        
    for i in range(0, len(temp)):
        temp[i]['nip'] = nip[i]
        
    temp = pd.concat(temp)
    temp.reset_index(drop=True ,inplace=True)
    df.drop([table], axis=1, inplace=True)
    return temp


def egzekucje(df):
    for row_no in range(0, len(df['egzekucje'])):
        try:
            temp = json_normalize(df['egzekucje'][row_no]).loc[0,]
            df.loc[row_no, 'egzekucje'] = temp[0]
        except:
            df.loc[row_no, 'egzekucje'] = None
    return df 


def uprawnienia(df):
    for row_no in range(0, len(df['uprawnienia'])):
        try:
            temp = json_normalize(df['uprawnienia'][row_no]).loc[0,]
            df.loc[row_no, 'uprawnienia'] = temp[0][0]
        except:
            df.loc[row_no, 'uprawnienia'] = None
    return df


def negatywne(df):
    for row_no in range(0, len(df['negatywne'])):
        try:
            temp = json_normalize(df['negatywne'][row_no]).loc[0,]
            df.loc[row_no, 'negatywne'] = temp[0]
        except:
            df.loc[row_no, 'negatywne'] = None
    return df

def format_date(df, columns):
    for column in columns:
        df[column].replace('9999-12-31', np.nan, regex=True, inplace=True)
        df[column].replace('0000-00-00', np.nan, regex=True, inplace=True)
        
        
def change_column_type(df, columns):
    for column in columns:
        df[column] = pd.to_numeric(df[column])
        
        
def pass_df(tables_name_df):
    failure_log = []
    for name in tables_name_df:
        try:
            tables_name_df[name].to_sql(name, engine, if_exists='append', index=True, schema="dbo")
        except:
            failure_log.append(name)
    return failure_log


def rescue(failure_log):
    failed_rows = []
    failed_tables = []
    if failure_log:
        for i in failure_log:
            for idx, row in tables_name_df[i].iterrows():
                new_row = pd.DataFrame(row).transpose()
                try:
                    new_row.to_sql(i, engine, if_exists='append', index=True, schema="dbo")
                except:
                    new_row['tabela'] = i
                    failed_rows.append(new_row)
                    pass
        failed_tables.append(pd.concat(failed_rows))
    return failed_tables 


def create_output_log(faulty_json, duplikaty_nip, failure_log, failed_tables):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H_%M")
    f = open(JSON_DIR + '\json_to_sql_log_' + now + '.txt', 'w')
    f.write('All JSON files: %d \n' % (len(collect_json_names())))
    f.write('Faulty JSON files: \n')
    for i in faulty_json:
        f.write(i)
        f.write('\n')
    f.write('Duplicated files: \n')
    for i in duplikaty_nip: 
       f.write(i)
       f.write('\n')
    f.write('Tables failed entirely to pass to SQL SERVER: \n') 
    for i in failure_log:
        f.write(i)
        f.write('\n')
    f.write('Rows failed to pass to SQL SERVER: \n') 
    for i in failed_tables:
        f.write(str(i))
        f.write('\n')
    f.close()
################################### FUNCTIONS END  ############################

################################### DATA PREPARATION  #########################
files_json = load_json(collect_json_names())
faulty_json = files_json[1]
valid_json = files_json[0]

spolki = create_df(valid_json)

def create_zaleglosci(valid_json):
    nip = valid_json[0]['nip']
    czas = str(datetime.date.today())
    zaleglosci = valid_json[0]['zaleglosci']
    dfs = []
    df_nip = pd.DataFrame(columns=['nip'])
    df_czas = pd.DataFrame(columns=['czas'])
    df_index = pd.DataFrame({'asd' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]})

    for i in zaleglosci:
        df = pd.DataFrame.from_dict(zaleglosci[i], orient = 'index')
        df_transposed = df.T
        dfs.append(df_transposed)
    
    df = pd.concat(dfs)
    for i in range(0, len(df)):
        df_nip = df_nip.append({'nip': nip}, ignore_index=True)
    
    for i in range(0, len(df)):
        df_czas = df_czas.append({'czas': czas}, ignore_index=True)
    
    df_final = pd.concat([df, df_nip, df_czas, df_index], axis=1, join='inner')
    df_final.set_index('asd')
    return df_final
    
zale = create_zaleglosci(valid_json)

engine = sqlalchemy.create_engine("mssql+pyodbc://PL-WAWFTS002/" +
                                  database_name + "?driver=SQL+Server")

zale.to_sql("ZALEGLOSCI", engine)

udzialowcy = create_outer_table(spolki, 'udzialowcy')
zalezne = create_outer_table(spolki, 'zalezne')
rola = create_outer_table(spolki, 'roles')
rola_h = create_outer_table(spolki, 'roleshistory')
aktywnosc = create_outer_table(spolki, 'aktywnosc')
uokik = create_outer_table(spolki, 'uokik')
zaleglosci = create_outer_table(spolki, 'zaleglosci')

#spolki.drop(['last_doc'], axis=1, inplace=True)
rola.drop(['pstan'], axis=1, inplace=True) #######
rola_h.drop(['pstan'], axis=1, inplace=True) #######
spolki.drop(['dotacje'], axis=1, inplace=True) #######
spolki.drop(['finance_year'], axis=1, inplace=True) #######
spolki.drop(['negatywne_txt'], axis=1, inplace=True) #######
aktywnosc['nip_aktywnosc'] = np.nan ####

columns = ['email', 'phone', 'www']
for col in columns:
    spolki[col] = spolki[col].apply(', '.join)

spolki = spolki.mask(spolki.applymap(str).eq('[]'))
spolki = uprawnienia(spolki)
spolki = egzekucje(spolki)
spolki = negatywne(spolki)

spolki.rename(columns = {'lokal':'numer_lokalu'}, inplace = True)
spolki.rename(columns = {'numer':'numer_nieruchomosci'}, inplace = True)
rola.rename(columns = {'surname':'nazwisko'}, inplace = True)
rola.rename(columns = {'name':'imie'}, inplace = True)
rola_h.rename(columns = {'surname':'nazwisko'}, inplace = True)
rola_h.rename(columns = {'name':'imie'}, inplace = True)

rola['pesel'] = rola.pesel.apply(lambda x: np.where(x.isdigit(), x, None))
rola_h['pesel'] = rola_h.pesel.apply(lambda x: np.where(x.isdigit(), x, None))
#aktywnosc['nip_aktywnosc'] = aktywnosc.nip_aktywnosc.apply(lambda x: np.where(x.isdigit(), x, None))


format_date(spolki, ['data_zakonczenia', 'data_rejestracji'])
format_date(aktywnosc, ['start', 'koniec'])
format_date(rola, ['start', 'koniec'])
format_date(rola_h, ['start', 'koniec'])
format_date(uokik, ['data'])

change_column_type(spolki, ['kapital', 'regon'])
change_column_type(rola, ['pesel'])
try:
    change_column_type(udzialowcy, ['pesel'])
except:
    pass
change_column_type(aktywnosc, ['wartosc', 'ilosc', 'kapital'])
change_column_type(zalezne, ['wartosc', 'ilosc', 'kapital'])

tables_list = [aktywnosc, rola, rola_h, udzialowcy, uokik, zaleglosci, zalezne, spolki]

for table in tables_list:
    table['czas'] = pd.Series([str(datetime.date.today())] * len(table))
    table.fillna(value=np.nan, inplace=True)
    table.replace('',np.nan, regex=True,inplace=True)
################################ DATA PREPARATION END  ########################

################################ SQL SERVER CONNECTION  #######################
tables_names = ['[AKTYWNOSC]', '[ROLA]', '[ROLA_H]', '[UDZIALOWCY]', '[UOKIK]', 
          '[ZALEGLOSCI]', '[ZALEZNE]', '[SPOLKI]']

engine = sqlalchemy.create_engine("mssql+pyodbc://PL-WAWFTS002/" +
                                  database_name + "?driver=SQL+Server")

#Select list of NIP number in database to check if any duplicates occur
nip_baza = engine.execute(text("SELECT nip FROM "+ database_name + ".[dbo].[SPOLKI]"))
lista_nip_baza = []
for row in nip_baza:
    lista_nip_baza.append(int(row[0]))

duplikaty_nip = list(map(str,set(lista_nip_baza).intersection(pd.to_numeric(spolki['nip']))))

#instering into hist tables duplicates
try:
    for i in tables_names:
        sql = text("INSERT INTO " + database_name + ".[hist]." + i + 
                   " SELECT * FROM " + database_name + ".[dbo]." + i + 
                   " WHERE nip in ("  + (','.join(duplikaty_nip)) + ")")
        engine.execute(sql)
except:
    print ("Unable to pass")
    pass
#dropping from database duplicates
try:
    for i in tables_names:
        sql = text("DELETE FROM " + database_name + ".[dbo]." + i + 
                   "WHERE nip in ("  + (','.join(duplikaty_nip)) + ")")
        engine.execute(sql)
except:
    print ("Unable to delete")
    pass
#Select index numbers from database
queries = []
results = []
for i in tables_names:
    sql = text("SELECT MAX([Index]) FROM " + database_name + ".[dbo]." + i)
    result = engine.execute(sql)
    results.append(result)

records_no = []
for i in results:
    for row in i:
        records_no.append(row[0])

records_no = [0 if x is None else x for x in records_no]
################################### SETTING NEW INDEXES########################
tables_df = pd.DataFrame({ 'Tablice' : tables_list ,'len' : records_no})
   
for i in range(0, len(tables_df)):
    indeksy = np.arange(1 + tables_df.loc[i, "len"],
                       (1 + tables_df.loc[i, "len"] + len(tables_df.loc[i, 'Tablice'])),
                       1, dtype=None)
    tables_df['Tablice'][i] = tables_df['Tablice'][i].set_index([indeksy])

aktywnosc, rola, rola_h, udzialowcy, uokik, zaleglosci, zalezne, spolki =\
tables_df['Tablice']

tables_df = tables_df.reindex([7, 6, 5, 4, 3, 2, 1, 0])
############################# SETTING NEW INDEXES END #########################

############################# PASSING TO DATABASE##############################
tables_names_pass = ['SPOLKI', 'ZALEZNE', 'ZALEGLOSCI', 'UOKIK', 
                     'UDZIALOWCY', 'ROLA_H', 'ROLA', 'AKTYWNOSC']

tables_name_df = dict(zip(tables_names_pass, tables_df['Tablice']))

failure_log = pass_df(tables_name_df)
failed_tables = rescue(failure_log)

create_output_log(faulty_json, duplikaty_nip, failure_log, failed_tables)
###############################################################################

