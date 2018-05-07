'''
Created on Mar 14, 2018

@author: ridwan
'''

from neuralnetwork import NeuralNetwork
from neuralnetwork.neuron.type import *
from neuralnetwork.weight import Weight
from neuralnetwork.exception import NETWORK_NETWORK_ALREADY_EXISTS
from neuralnetwork.neuron import Neuron
from chatbot.word import NeuronBow
import math

class NeuralNetworkDBService:
    database = None
    neurondbs = None
    weightdbs = None
    worddbs = None

#    constructor
    def __init__(self, database, neurondbs, weightdbs, worddbs):
        self.database = database
        self.neurondbs = neurondbs
        self.weightdbs = weightdbs
        self.worddbs = worddbs

#    save network
    def save_neural_network(self, neural_network, tenantid):
        check = self.retrieve_network(neural_network.name, tenantid)
        if(check):
            raise BaseException(NETWORK_NETWORK_ALREADY_EXISTS)
#        save network identity
        if (neural_network.id):
            query = ("insert into ms_nn_network(id, name, learning_rate) " +
                     "values ("+str(neural_network.id)+", '"+str(neural_network.name)+"',"+str(neural_network.learning_rate)+")")
        else:
            query = ("insert into ms_nn_network(name, learning_rate) " +
                     "values ('"+str(neural_network.name)+"',"+str(neural_network.learning_rate)+")")
        self.database.execute(tenantid, query, commit=False)
        network_result = self.retrieve_network(neural_network.name, tenantid)

#        weights to be saved to file
        weights = []
#        neurons to be saved to file
        neurons = []
        
#        save input layer
        for neuron in neural_network.input_layer:
#             neuron.id = self.neurondbs.save_neuron(neuron, network_result.id, tenantid, commit=False)
            neurons.append(neuron)
            for weight in neuron.weights:
                weights.append(weight)
        
#        save hidden layer
        for layer in neural_network.hidden_layers:
            for neuron in layer:
#                 neuron.id = self.neurondbs.save_neuron(neuron, network_result.id, tenantid, commit=False)
                neurons.append(neuron)
                for weight in neuron.weights:
                    weights.append(weight)
        
#        save output layer
        for neuron in neural_network.output_layer:
#             neuron.id = self.neurondbs.save_neuron(neuron, network_result.id, tenantid, commit=False)
            neurons.append(neuron)
        
#        save hidden bias
        for neuron in neural_network.hidden_biases:
#             neuron.id = self.neurondbs.save_neuron(neuron, network_result.id, tenantid, commit=False)
            neurons.append(neuron)
            for weight in neuron.weights:
                weights.append(weight)
        
#        save output bias
#         neural_network.output_bias.id = self.neurondbs.save_neuron(neural_network.output_bias, network_result.id, tenantid, commit=False)
        neurons.append(neural_network.output_bias)
        for weight in neural_network.output_bias.weights:
            weights.append(weight)

#        save neurons to file
        self.neurondbs.save_neurons_to_file(neurons, neural_network.name, tenantid)
#        save weights to file
        self.weightdbs.save_weights_to_file(weights, neural_network.name, tenantid)
        
#        commit
        self.database.commit(tenantid)

        return self.database.fetch_one(tenantid, "select max(id) from ms_nn_network where name = '"+neural_network.name+
                                       "' and learning_rate = "+str(neural_network.learning_rate))['max']
    
#    update network
    def update_neural_network(self, neural_network, tenantid):
#        update network identity
        query = ("update ms_nn_network set learning_rate = "+str(neural_network.learning_rate)+
                 " where id = "+str(neural_network.id))
        self.database.execute(tenantid, query, commit=False)
        
#        weights to be saved to file
        weights = []
#        neurons to be saved to file
        neurons = []
        
#        update input layer
        for neuron in neural_network.input_layer:
#             if(neuron.id == None):
#                 neuron_result_id = self.neurondbs.save_neuron(neuron, neural_network.id, tenantid, commit=False)
#                 for weight in neuron.weights:
#                     weights.append({'weight': weight, 'neuroninput_id': neuron_result_id})
#             else:
            if (not neuron.deleted):
#                 self.neurondbs.delete_neuron(neuron, tenantid, commit=False)
#             else:
                neurons.append(neuron)
                for weight in neuron.weights:
                    weights.append(weight)
        
#        update hidden layer
        for layer in neural_network.hidden_layers:
            for neuron in layer:
                if (not neuron.deleted):
                    neurons.append(neuron)
                    for weight in neuron.weights:
                        weights.append(weight)
#                 for weight in neuron.weights:
#                     if (not weight.deleted):
#                         weights.append({'weight': weight, 'neuroninput_id': neuron.id})
        
#        update output layer
        for neuron in neural_network.output_layer:
            if (not neuron.deleted):
                neurons.append(neuron)
#             if(neuron.id == None):
#                 self.neurondbs.save_neuron(neuron, neural_network.id, tenantid, commit=False)
#             else:
#                 if (neuron.deleted):
#                     self.neurondbs.delete_neuron(neuron, tenantid, commit=False)
        
#        update hidden bias
        for neuron in neural_network.hidden_biases:
            neurons.append(neuron)
            for weight in neuron.weights:
                weights.append(weight)
#             for weight in neuron.weights:
#                 weights.append({'weight': weight, 'neuroninput_id': neuron.id})
        
#        update output bias
        neurons.append(neural_network.output_bias)
        for weight in neuron.weights:
            weights.append(weight)
#         for weight in neural_network.output_bias.weights:
#             if (not weight.deleted):
#                 weights.append({'weight': weight, 'neuroninput_id': neural_network.output_bias.id})
        
#        save neurons to file
        self.neurondbs.save_neurons_to_file(neurons, neural_network.name, tenantid)
#        save weights to file
        self.weightdbs.save_weights_to_file(weights, neural_network.name, tenantid)
        
#        commit
        self.database.commit(tenantid)
        
        return neural_network.id

#    delete network
    def delete_neural_network(self, neural_network, tenantid):
#        delete input layer
#         for neuron in neural_network.input_layer:
#             neuronbow = self.worddbs.retrieve_neuronbow_by_neuron(neuron.id, tenantid)
#             if(neuronbow):
#                 self.worddbs.delete_neuronbow(neuronbow, tenantid, commit=False)
#             self.neurondbs.delete_neuron(neuron, tenantid, commit=False)
            
#        delete hidden layer
#         for layer in neural_network.hidden_layers:
#             for neuron in layer:
#                 self.neurondbs.delete_neuron(neuron, tenantid, commit=False)
        
#        delete output layer
#         for neuron in neural_network.output_layer:
#             neuronbow = self.worddbs.retrieve_neuronbow_by_neuron(neuron.id, tenantid)
#             if(neuronbow):
#                 self.worddbs.delete_neuronbow(neuronbow, tenantid, commit=False)
#             self.neurondbs.delete_neuron(neuron, tenantid, commit=False)
        
#        delete hidden bias
#         for neuron in neural_network.hidden_biases:
#             self.neurondbs.delete_neuron(neuron, tenantid, commit=False)
        
#        delete output bias
#         self.neurondbs.delete_neuron(neural_network.output_bias, tenantid, commit=False)    
        
#        delete network identity
        query = ("delete from ms_nn_network where id =" + str(neural_network.id))
        self.database.execute(tenantid, query, commit=False)
        
#        commit
        self.database.commit(tenantid)

        return NeuralNetwork.id

#        retrieve all network identity
    def retrieve_networks(self, tenantid):
        query = ("select n.id as id, n.name as name, n.learning_rate as learning_rate " +
                "from ms_nn_network as n " +
                "order by n.id asc")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            network = NeuralNetwork(row['name'], float(row['learning_rate']), id=row['id'])
            result.append(network)
        return result
    
#        retrieve network identity
    def retrieve_network(self, network_name, tenantid):
        query = ("select n.id as id, n.name as name, n.learning_rate as learning_rate " +
                "from ms_nn_network as n " +
                "where name = '" + network_name + "'")
        fetch_result = self.database.fetch_one(tenantid, query)
        network = None
        if(fetch_result):
            network = NeuralNetwork(fetch_result['name'], float(fetch_result['learning_rate']), id=fetch_result['id'])
        
        return network

#    retrieve and build network
    def retrieve_and_build_network(self, network_name, tenantid):
#        retrieve network identity
        network = self.retrieve_network(network_name, tenantid)
        
#        if network exists
        if(network):
#            load weights from file
            weights_data = self.weightdbs.load_weights_from_file(network_name, tenantid)
            neurons_data = self.neurondbs.load_neurons_from_file(network_name, tenantid)
        
#            retrieve input layer
            input_layer = []
            filtered_neurons = neurons_data[(neurons_data['layer'] == 0) & (neurons_data['type'] == INPUT_NEURON.id)]
            for index, n in filtered_neurons.iterrows():
                neuron = Neuron(int(n['layer']), int(n['index']), INPUT_NEURON)
                word = n['word']
                category = n['category']
                if (category != None):
                    category = int(category)
                context = n['context']
                if (context != None):
                    context = int(context)
                n_ascii = n['ascii']
                if (n_ascii != None):
                    n_ascii = int(n_ascii)
                neuron_bow = NeuronBow(word, category, context)
                neuron_bow.set_ascii(n_ascii)
                neuron.set_bow(neuron_bow)
                
                filtered_weights = weights_data[(weights_data['origin_layer'] == neuron.layer) & (weights_data['origin_index'] == neuron.index)]
                weights = []
                for index, w in filtered_weights.iterrows():
                    weight = Weight(int(w['origin_layer']), int(w['origin_index']), int(w['target_index']), w['value'])
                    weights.append(weight)
                neuron.set_weights(weights)
                
                input_layer.append(neuron)
            
#            retrieve hidden layer
            hidden_layers = []
            retrieve = True
            layer = 1
            while (retrieve):
                hidden_layer = []
                filtered_neurons = neurons_data[(neurons_data['layer'] == layer) & (neurons_data['type'] == HIDDEN_NEURON.id)]
                if (len(filtered_neurons) > 0):
                    for index, n in filtered_neurons.iterrows():
                        neuron = Neuron(int(n['layer']), int(n['index']), HIDDEN_NEURON)
                        
                        filtered_weights = weights_data[(weights_data['origin_layer'] == neuron.layer) & (weights_data['origin_index'] == neuron.index)]
                        weights = []
                        for index, w in filtered_weights.iterrows():
                            weight = Weight(int(w['origin_layer']), int(w['origin_index']), int(w['target_index']), w['value'])
                            weights.append(weight)
                        neuron.set_weights(weights)
                        
                        hidden_layer.append(neuron)
                    hidden_layers.append(hidden_layer)
                    layer += 1
                else:
                    retrieve = False
            
#            retrieve output layer
            output_layer = []
            filtered_neurons = neurons_data[(neurons_data['layer'] == layer) & (neurons_data['type'] == OUTPUT_NEURON.id)]
            for index, n in filtered_neurons.iterrows():
                neuron = Neuron(int(n['layer']), int(n['index']), OUTPUT_NEURON)
                word = n['word']
                category = n['category']
                if (category != None):
                    category = int(category)
                context = n['context']
                if (context != None):
                    context = int(context)
                neuron_bow = NeuronBow(word, category, context)
                neuron.set_bow(neuron_bow)
                
                output_layer.append(neuron)
            
#            retrieve hidden bias
            hidden_biases = []
            for j in range(layer-1):
                filtered_neurons = neurons_data[(neurons_data['layer'] == j) & (neurons_data['type'] == HIDDEN_BIAS.id)]
                n = filtered_neurons.iloc[0]
                
                hidden_bias = Neuron(int(n['layer']), int(n['index']), HIDDEN_BIAS)
                
                filtered_weights = weights_data[(weights_data['origin_layer'] == hidden_bias.layer) & (weights_data['origin_index'] == hidden_bias.index)]
                weights = []
                for index, w in filtered_weights.iterrows():
                    weight = Weight(int(w['origin_layer']), int(w['origin_index']), int(w['target_index']), w['value'])
                    weights.append(weight)
                hidden_bias.set_weights(weights)
                hidden_biases.append(hidden_bias)
            
#            retrieve output bias
            filtered_neurons = neurons_data[(neurons_data['layer'] == layer-1) & (neurons_data['type'] == OUTPUT_BIAS.id)]
            n = filtered_neurons.iloc[0]
            output_bias = Neuron(int(n['layer']), int(n['index']), OUTPUT_BIAS)
            
            filtered_weights = weights_data[(weights_data['origin_layer'] == output_bias.layer) & (weights_data['origin_index'] == output_bias.index)]
            weights = []
            for index, w in filtered_weights.iterrows():
                weight = Weight(int(w['origin_layer']), int(w['origin_index']), int(w['target_index']), w['value'])
                weights.append(weight)
            output_bias.set_weights(weights)
            
            network.set_network(input_layer, hidden_layers, output_layer, hidden_biases, output_bias)
        
        return network