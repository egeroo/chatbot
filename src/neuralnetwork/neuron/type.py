'''
Created on Mar 13, 2018

@author: Muhammad Ridwan
'''

class NeuronType:
    id = None
    label = None

#    constructor
    def __init__(self, id, label):
        self.id = id
        self.label = label

INPUT_NEURON = NeuronType(1, "Input Neuron")
HIDDEN_NEURON = NeuronType(2, "Hidden Neuron")
OUTPUT_NEURON = NeuronType(3, "Output Neuron")
HIDDEN_BIAS = NeuronType(4, "Hidden Bias")
OUTPUT_BIAS = NeuronType(5, "Output Bias")

def get_neuron_type(type):
    if type == 1:
        return INPUT_NEURON
    elif type == 2:
        return HIDDEN_NEURON
    elif type == 3:
        return OUTPUT_NEURON
    elif type == 4:
        return HIDDEN_BIAS
    elif type == 5:
        return OUTPUT_BIAS
    
    return None