'''
Created on Mar 13, 2018

@author: Muhammad Ridwan
'''

class Weight:
    neuron_origin_layer = None
    neuron_origin_index = None
    neuron_target_index = None
    value = None
    deleted = False

#    constructor
    def __init__(self, neuron_origin_layer, neuron_origin_index, neuron_target_index, value):
        self.neuron_origin_layer = neuron_origin_layer
        self.neuron_origin_index = neuron_origin_index
        self.neuron_target_index = neuron_target_index
        self.value = value
    
    def delete(self):
        self.deleted = True