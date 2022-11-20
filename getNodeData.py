import copy
import io
import pandas as pd
import requests


def get_node_data(api_key, channel, start_date, end_date, start_time, end_time):
    """
    :rtype: None, Creates data csv file
    :param api_key: str, api key of the node
    :param channel: str, channel id of the node
    :param start_date: str, start date in the format YYYY-MM-DD
    :param end_date: str, end date in the format YYYY-MM-DD
    :param start_time: str, start tim in the format HH:MM:SS
    :param end_time: str, end time in the format HH:MM:SS
    """
    continent = 'Asia'
    city = 'Kolkata'
    filename = channel + start_date + '.csv'
    url = "https://api.thingspeak.com/channels/" + channel + "/feeds.csv?api_key=" + api_key + "&start=" + start_date + "%20" + start_time + "&end=" + end_date + "%20" + end_time + "&timezone=" + continent + "%2F" + city
    content_raw = requests.get(url).content
    content = pd.read_csv(io.StringIO(content_raw.decode('utf-8')))
    content2 = copy.deepcopy(content)
    x = content['created_at'].iloc[0].split(' ')[0]
    y = content['created_at'].iloc[0].split(' ')[1]

    while len(content2) == 8000:
        if x != start_date and y != start_time:
            end_date = x
            end_time = y
            url = "https://api.thingspeak.com/channels/" + channel + "/feeds.csv?api_key=" + api_key + "&start=" + start_date + "%20" + start_time + "&end=" + end_date + "%20" + end_time + "&timezone=" + continent + "%2F" + city
            content_raw = requests.get(url).content
            content2 = pd.read_csv(io.StringIO(content_raw.decode('utf-8')))
            content = content2.merge(content, how='outer')
            x = content['created_at'].iloc[0].split(' ')[0]
            y = content['created_at'].iloc[0].split(' ')[1]
    print("{} generated".format(filename))
    content.to_csv(filename)


if __name__ == '__main__':
    pass