# -*- coding: utf-8 -*-
import requests
import json
import datetime

country = 'China'

poiname_field_name = 'Lake_name'
country_field_name = 'Country/Region'
longitude_field_name = 'Lon'
latitude_field_name = 'Lat'

target_cnname_field_header = 'cnname'

amap_key = input("Amap key: ")

f = open("lake_info.csv", "r")

print('Loading records...')
count = 0

fields = []
lines = []
filtered_index = []

name_field_index = None
country_field_index = None
longitude_field_index = None
latitude_field_index = None

while True:
    line = f.readline().removesuffix('\n')
    if not line:
        break
    
    lines.append(line)

    if count == 0:
        lines[count] += ',' + target_cnname_field_header
        fields = line.split(',')
        name_field_index = fields.index(poiname_field_name)
        country_field_index = fields.index(country_field_name)
        longitude_field_index = fields.index(longitude_field_name)
        latitude_field_index = fields.index(latitude_field_name)

    else:
        lines[count] += ','
        _fields = line.split(',')
        if _fields[country_field_index] == country:
            filtered_index.append(count)
    
    count += 1

f.close()

print('{} record(s) loaded, {} records(s) pending for translation.'.format(count, len(filtered_index)))

chn_dict = {}

for index in filtered_index:
    _fields = lines[index].split(',')
    
    if poiname_field_name != '' and _fields[name_field_index] == '':
        continue

    coord_str = _fields[longitude_field_index] + ',' + _fields[latitude_field_index]
    # poitype=190205 : lakes
    request = requests.get('https://restapi.amap.com/v3/geocode/regeo?key={}&location={}&poitype=190205&extensions=all'.format(amap_key, coord_str))
    request.encoding = 'UTF-8'
    contents = request.text
    obj = json.loads(contents)
    if obj['status'] != '1':
        print('Failed: index {} ================='.format(index))
        print(contents)
    else:
        regeo = obj['regeocode']
        sub = None
        if 'pois' in regeo and len(regeo['pois']) > 0:
            sub = regeo['pois']
        elif 'aois' in regeo and len(regeo['aois']) > 0:
            sub = regeo['aois']
        else:
            print('Failed: index {}. No poi nor aoi was found ------------------'.format(index))
            # print(regeo)
            continue
        
        for poi in sub:
            chn_dict[index] = poi['name']
            print('{} => {}'.format(_fields[name_field_index], poi['name']))
            break   # we just need the first poi

for index in filtered_index:
    if index in chn_dict:
        lines[index] += chn_dict[index]

f = open("lake_info_"+datetime.datetime.now().strftime("%b%d,%Y")+".csv", "a")
f.write('\n'.join(lines) + '\n')
f.close()