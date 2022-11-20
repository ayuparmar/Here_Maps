import datetime
import json
import os
import copy
import io
import time
import threading
import queue

import pandas as pd
import requests


class Node:
    def __init__(self, node_dict, name):
        """
        :param node_dict: Dictionary for the node
        :param name: alias for the node
        """
        self.name = name
        self.channel_id = node_dict['Channel ID']
        self.api_key = node_dict['API_Key']
        self.lat = node_dict['Latitude']
        self.long = node_dict['Longitude']
        self.node_data_dir = os.path.join('Data', 'nodeData', name)
        self.map_data_dir = os.path.join('Data', 'mapData', name)
        os.makedirs(self.node_data_dir, exist_ok=True)
        os.makedirs(self.map_data_dir, exist_ok=True)
        self.map_data_csv = open(os.path.join(self.map_data_dir, 'data.csv'), 'a')


    def get_node_data(self, start_date, end_date, start_time, end_time):
        """
        Fetches node data from the Thingspeak server
        :rtype: None, Creates data csv file
        :param start_date: str, start date in the format YYYY-MM-DD
        :param end_date: str, end date in the format YYYY-MM-DD
        :param start_time: str, start tim in the format HH:MM:SS
        :param end_time: str, end time in the format HH:MM:SS
        """
        continent = 'Asia'
        city = 'Kolkata'
        filename = os.path.join(self.node_data_dir, start_date + '.csv')
        url = "https://api.thingspeak.com/channels/" + self.channel_id + "/feeds.csv?api_key=" + self.api_key + "&start=" + start_date + "%20" + start_time + "&end=" + end_date + "%20" + end_time + "&timezone=" + continent + "%2F" + city

        content_raw = requests.get(url).content
        content = pd.read_csv(io.StringIO(content_raw.decode('utf-8')))

        content2 = copy.deepcopy(content)
        x = content['created_at'].iloc[0].split(' ')[0]
        y = content['created_at'].iloc[0].split(' ')[1]

        while len(content2) == 8000:
            if x != start_date and y != start_time:
                end_date = x
                end_time = y
                url = "https://api.thingspeak.com/channels/" + self.channel_id + "/feeds.csv?api_key=" + self.api_key + "&start=" + start_date + "%20" + start_time + "&end=" + end_date + "%20" + end_time + "&timezone=" + continent + "%2F" + city
                content_raw = requests.get(url).content

                content2 = pd.read_csv(io.StringIO(content_raw.decode('utf-8')))
                content = content2.merge(content, how='outer')
                x = content['created_at'].iloc[0].split(' ')[0]
                y = content['created_at'].iloc[0].split(' ')[1]
        print("{} Saved".format(filename))
        content.to_csv(filename)


    def get_maps_data(self):
        here_maps_api_key = 'LjeF0DTVqT-gETXeNryneCeuxaWpjL-1S05fGdCgowQ'
        t = datetime.datetime.now()
        t = t.strftime("%Y-%m-%d %H-%M-%S")

        url = 'https://traffic.ls.hereapi.com/traffic/6.3/flow.json?prox=' + self.lat + '%2C' + self.long + '%2C104&apiKey=' + here_maps_api_key
        content_raw = requests.get(url).content
        content = json.loads(content_raw)
        # out_file = open(filename, 'w')
        # json.dump(content, out_file, indent=6)
        # out_file.close()
        # print("{} Saved".format(filename))
        jam_factor = self.parse_maps_data(content)
        self.map_data_csv.writelines('{},{}\n'.format(t, jam_factor))
        print("Data stored for", self.name, "at", t)


    def parse_maps_data(self, data):
        RWS = data["RWS"][0]["RW"]  # list of roadways
        JF_list = []
        for RW in RWS:
            JF = 0.0
            FI = RW["FIS"][0]["FI"]  # list of flow items
            for F in FI:
                JF += F['CF'][0]['JF']  # Jam factor for the flow
            JF = JF / len(FI)
            JF_list.append(JF)
        final_jf = max(JF_list)  # taking max jam factor along all the roads
        return final_jf

def get_maps_data_threaded():
    while True:
        task = que.get()
        task()
        que.task_done()

if __name__ == '__main__':
    nodes = json.load(open('NodeDetails.json', 'r'))

    # Create variable for all nodes

    biodiversity_park_junction = Node(nodes["Biodiversity Park Junction"], 'biodiversity')
    botanical_garden_junction = Node(nodes["Botanical Garden Junction"], 'botanical')
    gachibowli_flyover = Node(nodes["Gachibowli Flyover"], 'gachifloyover')
    iiit_dlf_node = Node(nodes["IIITH DLF Junction"], 'iiitdlf')
    masjid_banda_node = Node(nodes["Masjid Banda Circle"], 'masjidbanda')
    uoh_small_gate = Node(nodes["UoH Small Gate"], 'uohgate')
    prime_splendour = Node(nodes["Prime Splendour Masjid Banda Road"], 'primesplendour')
    vijaya_diag_bot_garden = Node(nodes["Vijaya Diagnostics Botanical Garden"], 'vijayadiag')
    decathlon_gachibowli = Node(nodes["Decathlon Gachibowli"], 'decathlon_gachi')
    indira_nagar = Node(nodes["Indira Nagar"], 'indiranagar')

    # masjid_banda_node.get_node_data(start_date='2021-12-25', end_date='2021-12-25',
    #                                 start_time='09:00:00', end_time='17:00:00')

    data_collection_start_time = datetime.time(8, 0, 0, 0)
    data_collection_stop_time = datetime.time(21, 0, 0, 0)

    node_objects = [biodiversity_park_junction, botanical_garden_junction, masjid_banda_node, iiit_dlf_node,
                    gachibowli_flyover, uoh_small_gate, prime_splendour, vijaya_diag_bot_garden,
                    decathlon_gachibowli, indira_nagar]
    que = queue.Queue(maxsize=len(node_objects))

    try:
        while True:
            now = datetime.datetime.now().time()
            for node_object in node_objects:
                if data_collection_start_time <= now <= data_collection_stop_time:
                    print("Data storage is starting")
                    if node_object.map_data_csv.closed:
                        node_object.map_data_csv = open(os.path.join(node_object.map_data_dir, 'data.csv'), 'a')

                elif not node_object.map_data_csv.closed:
                    node_object.map_data_csv.close()
                    print("Data is stored for", datetime.datetime.now().strftime("%D"))

            while data_collection_start_time <= now <= data_collection_stop_time:
                threading.Thread(target=get_maps_data_threaded, daemon=True).start()
                for node_object in node_objects:
                    que.put(node_object.get_maps_data)
                que.join()
                time.sleep(30)
                now = datetime.datetime.now().time()
    except KeyboardInterrupt:
        for node_object in node_objects:
            node_object.map_data_csv.close()


