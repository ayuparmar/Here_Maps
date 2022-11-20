import io

import requests
import json


def get_maps_data(lat, long):
    api_key = 'LjeF0DTVqT-gETXeNryneCeuxaWpjL-1S05fGdCgowQ'
    url = 'https://traffic.ls.hereapi.com/traffic/6.3/flow.json?prox=' + lat + '%2C' + long + '%2C104&apiKey=' + api_key
    content_raw = requests.get(url).content
    content = json.loads(content_raw)
    return content


def parse_maps_data(data):
    RWS = data["RWS"][0]["RW"]
    JF_list = []
    for RW in RWS:
        JF = 0.0
        FI = RW["FIS"][0]["FI"]
        for F in FI:
            JF += F['CF'][0]['JF']
        JF = JF/len(FI)
        JF_list.append(JF)
    final_jf = max(JF_list)
    return final_jf


if __name__ == '__main__':
    lat = "17.4555"
    long = "78.364"
    map_data = get_maps_data(lat, long)
    parse_maps_data(map_data)
    # out_file = open("Data/map_data.json", 'w')
    # json.dump(map_data, out_file, indent=6)
    # out_file.close()
    # print(map_data['RWS'])
