from base64 import b64decode
emis_file = r'C:\Users\mmandziej001\Desktop\Projects\Scripts\emis_all.txt'
pwg_file = r'C:\Users\mmandziej001\Desktop\Projects\Scripts\pwg_all.txt'
sql_file = r'C:\Users\mmandziej001\Desktop\Projects\Scripts\sql.txt'


def decode_key(key_file):
    """ Read encoded keys stored in external files """
    encoded_key = open(key_file).read()
    if key_file == sql_file:
        decoded_keys = b64decode(encoded_key).decode('utf-8')
    else:
        key1, key2 = encoded_key.split('\n')
        decoded_key1 = b64decode(key1).decode('utf-8')
        decoded_key2 = b64decode(key2).decode('utf-8')
        decoded_keys = decoded_key1, decoded_key2
    return decoded_keys

PROJECT_NAME = 'Mall7'
USER_NAME, PASSWORD = decode_key(emis_file)
PUBLIC_KEY, PRIVATE_KEY = decode_key(pwg_file)
PRG_CREDS = SQL_CREDS = decode_key(sql_file)
GHC_CREDS = "Trusted_Connection=yes;DRIVER={ODBC Driver 17 for SQL Server};server=DEGCSQLDBSPWV01;Database=PL_FTS;"
GHC_CREDS_SQL_ALCHEMY = "mssql+pyodbc://DEGCSQLDBSPWV01/PL_FTS?driver=ODBC+Driver+17+for+SQL+Server"
PRG_CREDS_SQL_ALCHEMY = "mssql+pyodbc://pl_fts_user:Call0fCtulu@cz-prgfts008/PL_FTS?driver=SQL+Server"
############ ENCODE KEYS/PASSWORDS ###########

from base64 import b64encode

key_1 = b'pierwszyklucz' # wpisz pierwszy klucz - b przed stringiem jest konieczne, żeby zrobić z niego obiekt bitowy
key_2 = b'drugiklucz' # wpisz drugi klucz klucz - jak wyżej

coded_key_1 = b64encode(key_1).decode('utf-8')
coded_key_2 = b64encode(key_2).decode('utf-8')

""" Te klucze potem zapisujemy w zewnętrznym pliku tekstowym oddzielone spacją - 
###     można zastosować inny delimiter, ale wtedy też trzeba zmienić argument 
###     metody split w funkcji decode_key.
###     Dla bezpieczeństwa sciezki do plików trzymamy w osobnym skrypcie 
###     (nie jednym z tych, które często przesyłamy) i dopiero z niego importujemy
###     np.  from keys_coded import USER_NAME, PASSWORD, PRG_CREDS """
