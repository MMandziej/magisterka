# coding: utf8

import logging
import pyodbc
import datetime
import time
import unicodedata
import codecs
#import chardet
import argparse
import urllib
import json
import pandas


JSON_OUTPUT_PATH = r'C:\Users\mmandziej001\Desktop\Projects\EMIS\OUTPUT_API\\'
# Key for Google API - to be filled!
key = 'AIzaSyB1v_HidGghc_bdegWp6IpiWp9e52suOKQ'
# Address for geocoding API
api_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
###
db_connect_string = 'driver={ODBC Driver 13 for SQL Server};server=10.82.186.8;database=PL_FTS;uid=pl_fts_user;pwd=Call0fCtulu'

def connectToDB(db_connect_string):
    db_connect = pyodbc.connect(db_connect_string, autocommit=False)
    return db_connect
  
def writeInDB(db_connect,sql_statement):
    db_connect = pyodbc.connect(db_connect_string, autocommit=False)
    cur = db_connect.cursor()
    try:
        cur.execute(sql_statement)
        cur.commit()
        ret = 1
    except Exception as e:
        s = str(e)
        print('Error: {0}'.format(s))
        ret = 0
    cur.close()  
    return ret 

def add_quot(text):
    text2 = '\'' + text + '\''
    return text2;
  
def geocode_address(address):
    json_valid_guid = 'geocode'
    #######################
    #### GEOCODING PART ###
    #######################
    try:
        website = api_url + urllib.parse.urlencode([("address", address),("key",key)])
        print(website)
        out = urllib.request.urlopen(website).read()
        out_json = json.loads(out)
        status = out_json['status']
        with open(JSON_OUTPUT_PATH + '_{}.json'.format(json_valid_guid), 'w') as f:
            json.dump(out_json, f)
        
    except Exception as e:
        s = str(e)
        print('Error: {0}'.format(s))
        status = 'FAILED'
        lat = 0
        lng = 0
    if (status=='OK'):
        lng = out_json['results'][0]['geometry']['location']['lng']
        lat = out_json['results'][0]['geometry']['location']['lat']
    else:
        lat = 0
        lng = 0
    return (lat,lng)
    ###############################
    #### END OF GEOCODING PART ####
    ###############################

parser = argparse.ArgumentParser()
parser.add_argument('--InSelectFile', nargs='?', default='./00_SQL/in_sl_bl.txt')
parser.add_argument('--OutUpdateFile', nargs='?', default='./00_SQL/out_sl_bl.txt')
parser.add_argument('--WriteToDB', nargs='?', default='Yes')

strings = parser.parse_args()

input_file = strings.InSelectFile
output_file = strings.OutUpdateFile
write2db = 0 if strings.WriteToDB == 'No' else 1

with open(input_file, "r") as selectFile:
    selectQuery = selectFile.read().replace('\n','')
with open(output_file, "r") as updateFile:
    updateQuery = updateFile.read() 

db_connection = connectToDB(db_connect_string)

today = datetime.datetime.now()
today_print = '{0}-{1}-{2}'.format(today.year,today.month,today.day)  
  
starttime = datetime.datetime.now().replace(microsecond=0)

### Get select
addressList = pandas.read_sql_query(selectQuery, db_connection)['address'].tolist()
cc_list = pandas.read_sql_query(selectQuery, db_connection)['Company code'].tolist()

### Count addresses
print('Found {0} addresses'.format(len(addressList)))
cnt = 0

for code, address in zip(cc_list, addressList):
    cnt = cnt + 1
    lat,lng = geocode_address(address)
    updateCommand = updateQuery.format(lat, lng, code)
    if write2db == 1:
        writeInDB(db_connection,updateCommand)
        currenttime = datetime.datetime.now().replace(microsecond=0)
        print('Address {0}/{1} written into DB, processing time so far {2}'.format(cnt,len(addressList),currenttime-starttime))
    else:
        print(updateCommand)

    
