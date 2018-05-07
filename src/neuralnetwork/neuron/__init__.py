'''
Created on Mar 13, 2018

@author: Muhammad Ridwan
'''
from neuralnetwork.weight import Weight
from neuralnetwork.neuron.type import NeuronType

class Neuron:
    type = None
    layer = None
    index = None
    weights = None
    bow = None
    deleted = False

#    constructor
    def __init__(self, layer, index, type):
        self.layer = layer
        self.index = index
        self.type = type

    def set_weights(self, weights):
        self.weights = weights
    
    def set_bow(self, bow):
        self.bow = bow
    
    def delete(self):
        self.deleted = True
    
    def add_weight(self, weight):
        if (not self.weights):
            self.weights = []
        self.weights.append(weight)