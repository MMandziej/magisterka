import datetime as d
import json
import pandas as pd
import pyodbc
import urllib

# Key for Google API - to be filled!
key = 'AIzaSyDMkKf7KJVgB8L1QAhXPj1R0bVGfnZdnNE'
#key = 'AIzaSyB1v_HidGghc_bdegWp6IpiWp9e52suOKQ'
# Address for geocoding API
api_url = 'https://maps.googleapis.com/maps/api/streetview/metadata?size=600x300&pitch=4&source=outdoor&'
rescue_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

###
project_table = 'Kaufland9_adresy'


def connect_with_db():
    conn = pyodbc.connect('driver={ODBC Driver 13 for SQL Server};'
                          'server=10.82.186.8;'
                          'database=PL_FTS;'
                          'uid=pl_fts_user;'
                          'pwd=Call0fCtulu')
    cursor = conn.cursor()
    print("Connection with SQL Server database successfully established.")
    return cursor

def retrieve_addresses(cursor: str, project_name: str) -> list:
    def cleanse_address(text):
        ref_dict = {'ul. ': '',
                    'Ul. ': '',
                    '  ': ''}

        for phrase, replacement in ref_dict.items():
            text = text.replace(phrase, replacement)
        return text.strip()
    
    address_list = []
    for row in cursor.execute('SELECT nip, address, lat, lng FROM [PL_FTS].[dbo].[{}] \
                               ORDER BY nip ASC'.format(project_name)):
        single_address_dict = {}
        single_address_dict[row.nip] = {'address': cleanse_address(row.address),
										'lat': row.lat,
										'lng': row.lng}
        address_list.append(single_address_dict)
    print("%s addresses succesfully retrieved from table." % len(address_list))
    return address_list


def get_coordinates(address_list: list) -> list:
    nips_jsons = {}
    correct_cnt = []
    rescue_cnt = []
    cnt = 0
    for entity in address_list:
        for nip, table in entity.items():
            try:
                website = api_url + urllib.parse.urlencode([("location", table["address"]), ("key",key)])
                out = urllib.request.urlopen(website).read()
                out_json = json.loads(out)
                status = out_json['status']
                if status == 'OK':
                    method = 'outdoor'
                    lat = out_json['location']['lat']
                    lng = out_json['location']['lng']
                    correct_cnt.append(nip)
                    nips_jsons[nip] = out_json
                elif status == 'ZERO_RESULTS':
                    method = 'basic'
                    resc_website = rescue_url + urllib.parse.urlencode([("address", table["address"]), ("key",key)])
                    resc_out = urllib.request.urlopen(resc_website).read()
                    resc_out_json = json.loads(resc_out)
                    resc_status = resc_out_json['status']
                    if resc_status == 'OK':
                        lat = resc_out_json['results'][0]['geometry']['location']['lat']
                        lng = resc_out_json['results'][0]['geometry']['location']['lng']
                        nips_jsons[nip] = resc_out_json
                        status = 'OK'
                        rescue_cnt.append(nip)
                    else:
                        lat = 0
                        lng = 0
                else:
                    lat = 0
                    lng = 0
                cnt += 1
                print("Address checked for {} out of {} entities.".format(cnt, len(address_list)))

            except Exception as e:
                s = str(e)
                print('Error: {0}'.format(s))
                nips_jsons[nip] = s
                status = 'FAILED'
                lat = 0
                lng = 0
            table['NIP'] = nip
            table['status'] = status
            table['lat'] = lat
            table['lng'] = lng
            table['method'] = method
    print("For {} entities adresses correctly checked with outdoor method.".format(len(correct_cnt)))
    print("For {} entities adresses correctly checked with basic method.".format(len(rescue_cnt)))
    return address_list, nips_jsons


def write_addresses_to_db(cursor: str, address_list_geocoded: list, project_name: str):   
    cursor.execute(
        "IF COL_LENGTH('[PL_FTS].[dbo].[{0}]', 'status') IS NULL \
         BEGIN \
         ALTER TABLE [PL_FTS].[dbo].[{0}] \
         ADD status VARCHAR(50), \
             method VARCHAR(50) \
         END".format(project_name))
    cursor.commit()

    count = 0
    for entity in address_list_geocoded:
        for nip, table in entity.items():
            args = {'arg1': project_name,
                    'arg2': table['lat'],
                    'arg3': table['lng'],
                    'arg4': table['status'],
                    'arg5': table['method'],
                    'arg6': nip}

            cursor.execute(
                "UPDATE [PL_FTS].[dbo].[{arg1}] \
                 SET lat = {arg2}, \
                     lng = {arg3}, \
                     status = '{arg4}', \
                     method = '{arg5}'  \
                WHERE nip = '{arg6}'".format(**args))
            cursor.commit()

            count += 1
            print('Address {0}/{1} written into DB, processing time so far {2}.'.format(
                    count, len(address_list_geocoded), d.datetime.now().replace(microsecond=0)-starttime))
    list_df = []
    for i in address_list_geocoded:
        for j in i.values():
            list_df.append(j)

    log_df = pd.DataFrame(list_df)
    log_df = log_df[['NIP','address', 'lat', 'lng', 'status', 'method']]
    return log_df

############### GET OUTPUT ##################
starttime = d.datetime.now().replace(microsecond=0)
connection_to_db = connect_with_db()
addresses = retrieve_addresses(connection_to_db, project) 
addresses_geocoded, nips_jsons = get_coordinates(addresses)
geocoding_log = write_addresses_to_db(connection_to_db, addresses_geocoded, project_table)
