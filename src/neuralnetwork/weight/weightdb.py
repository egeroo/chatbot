'''
Created on Mar 13, 2018

@author: Muhammad Ridwan
'''

from neuralnetwork.weight import Weight
from neuralnetwork.exception import *
from database import Database
import pandas as pd
import os

class WeightDBService:
    
    def save_weights_to_file(self, weights, network_name, tenantid):
        data = []
        for w in weights:
            weight = {'origin_layer': int(w.neuron_origin_layer), 'origin_index': int(w.neuron_origin_index), 'target_index': int(w.neuron_target_index), 'value': w.value}
            data.append(weight)
            
        df = pd.DataFrame(data, columns=['origin_layer', 'origin_index', 'target_index', 'value'])
        df.to_csv(os.path.join(os.path.join("tenant-data", tenantid),network_name+"-weights.csv"))
        
    def load_weights_from_file(self, network_name, tenantid):
        df = pd.read_csv(os.path.join(os.path.join("tenant-data", tenantid),network_name+"-weights.csv"))
        df = df.where(pd.notnull(df), None)
        return df
