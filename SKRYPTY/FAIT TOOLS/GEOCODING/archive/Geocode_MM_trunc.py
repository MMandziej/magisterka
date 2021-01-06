import datetime as d
import json
import pyodbc
import urllib

# Key for Google API - to be filled!
key = ''
#key = ''
# Address for geocoding API
api_url = 'https://maps.googleapis.com/maps/api/streetview/metadata?size=600x300&pitch=4&source=outdoor&'
rescue_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

###
project = 'Geocoding_TEST'


def connect_with_db():
    conn = pyodbc.connect(#INSERT SQL CREDS
            )
    cursor = conn.cursor()
    print("Connection with SQL Server database successfully established.")
    return cursor


def retrieve_addresses(cursor: str,
                       project_name: str) -> list:
    address_list = []
    for row in cursor.execute('SELECT nip, address, lat, lng FROM [PL_FTS].[dbo].[{}] \
                               ORDER BY nip ASC'.format(project_name)):
        single_address_dict = {}
        nip = row.nip
        address = row.address
        lat = row.lat
        lng = row.lng
        single_address_dict[nip] = {'address': address,
                                    'lat': lat,
                                    'lng': lng}
        address_list.append(single_address_dict)
    print("%s addresses succesfully retrieved from table." % len(address_list))
    return address_list


def get_coordinates(address_list: list) -> list:
    nips_jsons = {}
    correct_cnt = 0
    rescue_cnt = 0
    for entity in address_list:
        for nip, table in entity.items():
            try:
                website = api_url + urllib.parse.urlencode([("location", table["address"]), ("key",key)])
                out = urllib.request.urlopen(website).read()
                out_json = json.loads(out)
                status = out_json['status']
                if status == 'OK':
                    lat = out_json['location']['lat']
                    lng = out_json['location']['lng']
                    correct_cnt += 1
                    nips_jsons[nip] = out_json
                elif status == 'ZERO_RESULTS':
                    resc_website = rescue_url + urllib.parse.urlencode([("address", table["address"]), ("key",key)])
                    resc_out = urllib.request.urlopen(resc_website).read()
                    resc_out_json = json.loads(resc_out)
                    resc_status = resc_out_json['status']
                    if resc_status == 'OK':
                        lat = resc_out_json['results'][0]['geometry']['location']['lat']
                        lng = resc_out_json['results'][0]['geometry']['location']['lng']
                        rescue_cnt += 1
                        nips_jsons[nip] = resc_out_json
                    else:
                        lat = 0
                        lng = 0
                else:
                    lat = 0
                    lng = 0

            except Exception as e:
                s = str(e)
                print('Error: {0}'.format(s))
                nips_jsons[nip] = s
                status = 'FAILED'
                lat = 0
                lng = 0

            table['status'] = status
            table['lat'] = lat
            table['lng'] = lng
    print("For {} entities adresses correctly checked with outdoor method.".format(correct_cnt))
    print("For {} entities adresses correctly checked with basic method.".format(rescue_cnt))
    return address_list, nips_jsons


def write_addresses_to_db(cursor: str,
                          address_list_geocoded: list,
                          project_name: str):   
    count = 0
    for entity in address_list_geocoded:
        for nip, table in entity.items():
            args = {'arg1': project_name,
                    'arg2': table['lat'],
                    'arg3': table['lng'],
                    'arg4': nip,
                    'arg5': table['address']}

            cursor.execute(
                "UPDATE [PL_FTS].[dbo].[{arg1}] SET lat = {arg2}, lng = {arg3} " \
                "WHERE nip = '{arg4}' AND address = '{arg5}'".format(**args))
            cursor.commit()

            count += 1
            print('Address {0}/{1} written into DB, processing time so far {2}.'.format(
                    count, len(address_list_geocoded), d.datetime.now().replace(microsecond=0)-starttime))

############### GET OUTPUT ##################
starttime = d.datetime.now().replace(microsecond=0)
connection_to_db = connect_with_db()
addresses = retrieve_addresses(connection_to_db, project) 
addresses_geocoded, nips_jsons = get_coordinates(addresses)
write_addresses_to_db(connection_to_db, addresses_geocoded, project)
