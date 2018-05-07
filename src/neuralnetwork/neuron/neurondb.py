'''
Created on Mar 14, 2018

@author: Muhammad Ridwan
'''

from neuralnetwork.neuron import Neuron
from neuralnetwork.neuron.type import NeuronType, get_neuron_type
from neuralnetwork.exception import *
from database import Database
import pandas as pd
import os
from chatbot.word import NeuronBow
    
class NeuronDBService:
    database = None

#    constructor
    def __init__(self, database):
        self.database = database
    
#    save neuron
    def save_neuron(self, neuron, network_id, tenantid, commit=True):
        check = self.retrieve_neuron(network_id, neuron.layer, neuron.index, neuron.type, tenantid)
        if(check):
            raise BaseException(NETWORK_NEURON_ALREADY_EXISTS)
        query = ("insert into tr_nn_neuron(layer, index, neurontypeid, networkid) " +
                 "values ("+str(neuron.layer)+","+str(neuron.index)+","+str(neuron.type.id)+","+str(network_id)+")")
        
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(id) from tr_nn_neuron where layer = "+str(neuron.layer)+" and index = "+str(neuron.index)+" and neurontypeid = "+str(neuron.type.id)+" and networkid = "+str(network_id))['max']
    
    def save_neurons_to_file(self, neurons, network_name, tenantid):
        data = []
        for n in neurons:
            neuron = {'layer': int(n.layer), 'index': int(n.index), 'type': int(n.type.id), 'word': None, 'category': None, 'context': None, 'ascii': None}
            if (n.bow != None):
                neuron['word'] = n.bow.word
                neuron['category'] = n.bow.category
                neuron['context'] = n.bow.context
                neuron['ascii'] = n.bow.ascii
            data.append(neuron)
        
        df = pd.DataFrame(data, columns = ['layer', 'index', 'type', 'word', 'category', 'context', 'ascii'])
        df.to_csv(os.path.join(os.path.join("tenant-data", tenantid),network_name+"-neurons.csv"))
        
    def load_neurons_from_file(self, network_name, tenantid):
        df = pd.read_csv(os.path.join(os.path.join("tenant-data", tenantid),network_name+"-neurons.csv"))
        df = df.where(pd.notnull(df), None)
        return df
    
#    update neuron
    def update_neuron(self, neuron, tenantid, commit=True):
        query = ("update tr_nn_neuron set layer = "+str(neuron.layer)+
                 ", index = "+str(neuron.index)+
                 ", neurontypeid = "+str(neuron.type.id)+
                 " where id = "+str(neuron.id))
        self.database.execute(tenantid, query, commit=commit)
        return neuron.id

#    delete neuron
    def delete_neuron(self, neuron, tenantid, commit=True):
        query = ("delete from tr_nn_neuron where id =" + str(neuron.id))
        self.database.execute(tenantid, query, commit=commit)
        return neuron.id

#    retrieve neurons by network, layer, and type
    def retrieve_neurons(self, network_id, layer, type, tenantid):
        query = ("select n.id as id, n.layer as layer, n.index as index, nt.id as neurontypeid, " +
                 "nt.label as neurontypelabel, n.networkid as networkid from tr_nn_neuron as n " +
                 "left join ms_nn_neurontype nt on nt.id = n.neurontypeid where n.networkid = " + str(network_id) + " "
                 "and n.layer = " + str(layer) + " and n.neurontypeid = " + str(type.id))
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            type = NeuronType(row['neurontypeid'], row['neurontypelabel'])
            neuron = Neuron(row['layer'], row['index'], type, id=row['id'])
            result.append(neuron)
        return result

#    retrieve neuron by network, layer, type, and index
    def retrieve_neuron(self, network_id, layer, index, type, tenantid):
        query = ("select n.id as id, n.layer as layer, n.index as index, nt.id as neurontypeid, " +
                 "nt.label as neurontypelabel, n.networkid as networkid from tr_nn_neuron as n " +
                 "left join ms_nn_neurontype nt on nt.id = n.neurontypeid where n.networkid = " + str(network_id) + " "
                 "and n.layer = " + str(layer) + " and n.index = " + str(index) + " and n.neurontypeid = " + str(type.id))
        fetch_result = self.database.fetch_one(tenantid, query)
        neuron = None
        if(fetch_result):
            neurontype = NeuronType(fetch_result['neurontypeid'], fetch_result['neurontypelabel'])
            neuron = Neuron(fetch_result['layer'], fetch_result['index'], neurontype, id=fetch_result['id'])
        return neuron
    
    def retrieve_neuron_by_word(self, word, network_name, tenantid):
        neurons = self.load_neurons_from_file(network_name, tenantid)
        neuron = None
        
        nb = neurons[neurons['word'] == word]
        if(len(nb) != 0):
            neuron = Neuron(int(nb.iloc[0]['layer']), int(nb.iloc[0]['index']), get_neuron_type(int(nb.iloc[0]['type'])))
            neuronbow = NeuronBow(nb.iloc[0]['word'], nb.iloc[0]['category'], nb.iloc[0]['context'])
            neuron.set_bow(neuronbow)
        
        return neuron
    