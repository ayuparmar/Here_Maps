import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt


if __name__ == '__main__':
    node_objects = ["masjidbanda", "iiitdlf"]
    for node_object in node_objects:
        filename_map = "Data/mapData/" + node_object +"/data.csv"
        mapData = pd.read_csv(filename_map,header=None, names=["created_at", "jammingFactor"])
        filename_node ="Data/nodeData/" +node_object + "/NodeData.csv"
        nodeData = pd.read_csv(filename_node)
        mapData["created_at"] = pd.to_datetime(mapData["created_at"], format="%Y-%m-%d %H-%M-%S")
        mapData["created_at"]= mapData["created_at"].dt.floor(freq='30S')
        nodeData["created_at"] = nodeData["created_at"].astype(str).str[:-5]
        nodeData["created_at"] = pd.to_datetime(nodeData["created_at"])
        merged = pd.merge(nodeData, mapData,  
                       on='created_at',  
                       how='inner') 
        filename_final = "Data/mergedData/" + node_object +".csv"
        merged.to_csv(filename_final)


