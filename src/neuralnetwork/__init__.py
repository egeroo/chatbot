'''
Created on Mar 13, 2018

@author: Muhammad Ridwan
'''
import numpy as np
import tensorflow as tf
from neuralnetwork.neuron import Neuron
from neuralnetwork.neuron.type import *
from neuralnetwork.weight import Weight
from neuralnetwork.exception import *

class NeuralNetwork:
    #network identity
    id = None
    name = None
    learning_rate = None
    
    #network classes
    input_layer = None
    hidden_layers = None
    output_layer = None
    hidden_biases = None
    output_bias = None
    
    #tensorflow session
    sess = None
    
    #tensorflow network
    x = None
    y = None
    weights = None
    biases = None
    hidden_layer = None
    out_layer = None
    perdiction = None
    cross_entropy = None
    optimizer = None
    train_op = None
    correct_pred = None
    accuracy = None
    init = None
    
#    constructor
    def __init__(self, name, learning_rate=0.01, id=None):
        self.id = id
        self.name = name
        self.learning_rate = learning_rate

#    return neuron with maximum index
    def max_indexed_neuron(self, neurons):
        if (not neurons):
            return None
        neuron = None
        for n in neurons:
            if (neuron == None):
                neuron = n
            if (n.index > neuron.index):
                neuron = n
        return neuron

#    add new input neuron
    def add_input_neuron(self):
#        find last indexed neuron
        last_added_neuron = self.max_indexed_neuron(self.input_layer)
        
#        default last index is -1, so if the layer is empty, the index will start from 0
        last_index = -1
       
#        if last added neuron found, then last index is not -1
        if(last_added_neuron):
            last_index = last_added_neuron.index
            
#        create neuron, and since it's input layer, we should create the weights connecting the neuron to the next layer
        neuron = Neuron(0, last_index+1, INPUT_NEURON)
        weights = []
        for n in self.hidden_layers[0]:
            weight = Weight(neuron.layer, neuron.index, n.index, np.random.normal())
            weights.append(weight)
        neuron.set_weights(weights)
        self.input_layer.append(neuron)

#        return the index of neuron in layer (not the identity index, but the list index)
        return len(self.input_layer)-1

#        remove input neuron
    def remove_input_neuron(self, index):
        for n in self.input_layer:
            if n.index == index:
                for w in n.weights:
                    w.delete()
                n.delete()
                break

#    add new output neuron
    def add_output_neuron(self):
#        find last indexed neuron
        last_added_neuron = self.max_indexed_neuron(self.output_layer)
        
#        default last index is -1, so if the layer is empty, the index will start from 0
        last_index = -1
       
#        if last added neuron found, then last index is not -1
        if(last_added_neuron):
            last_index = last_added_neuron.index
            
#        create neuron, and since it's input layer, we should create the weights connecting the neuron to the next layer
        neuron = Neuron(len(self.hidden_layers)+1, last_index+1, OUTPUT_NEURON)
        for n in self.hidden_layers[len(self.hidden_layers)-1]:
            weight = Weight(n.layer, n.index, neuron.index, np.random.normal())
            n.add_weight(weight)
        weight = Weight(self.output_bias.layer, self.output_bias.index, neuron.index, np.random.normal())
        self.output_bias.add_weight(weight)
        self.output_layer.append(neuron)

#        return the index of neuron in layer (not the identity index, but the list index)
        return len(self.output_layer)-1
    
#        remove output neuron
    def remove_output_neuron(self, index):
        for n in self.hidden_layers[len(self.hidden_layers)-1]:
            for w in n.weights:
                if (w.neuron_target_index == index):
                    w.delete()
                    break
                    
        for w in self.output_bias.weights:
            if(w.neuron_target_index == index):
                w.delete()
                break
            
        for n in self.output_layer:
            if (n.index == index):
                n.delete()
                break

#    build new network
    def build_new(self, input_layer_neurons=0, hidden_layers_neurons=[20], output_layer_neurons=0):
#        check input parameter
        if (input_layer_neurons < 0 or output_layer_neurons < 0):
            raise BaseException(NETWORK_NETWORK_INPUT_ERROR)
        if (not hidden_layers_neurons):
            raise BaseException(NETWORK_NETWORK_INPUT_ERROR)
        else:
            for x in hidden_layers_neurons:
                if (x <= 0):
                    raise BaseException(NETWORK_NETWORK_INPUT_ERROR)
        
        neuron_id = 0
        
#        build input layer
        self.input_layer = []
        for i in range(input_layer_neurons):
            neuron = Neuron(0, i, INPUT_NEURON)
#             weights = []
#             for j in range(hidden_layers_neurons[0]):
#                 weight = Weight(None, j, np.random.normal())
#                 weights.append(weight)
#             neuron.set_weights(weights)
            self.input_layer.append(neuron)

#        build hidden layers
        self.hidden_layers = []
        for layer in range(len(hidden_layers_neurons)):
            hidden_layer = []
            for i in range(hidden_layers_neurons[layer]):
                neuron = Neuron(layer+1, i, HIDDEN_NEURON)
#                 weights = []
#                 if(layer == (len(hidden_layers_neurons) - 1)):
#                     weights_count = output_layer_neurons
#                 else:
#                     weights_count = hidden_layers_neurons[layer+1]
#                 for j in range(weights_count):
#                     weight = Weight(None, j, np.random.normal())
#                     weights.append(weight)
#                 neuron.set_weights(weights)
                hidden_layer.append(neuron)
            self.hidden_layers.append(hidden_layer)

#        build output layer
        self.output_layer = []
        for i in range(output_layer_neurons):
            neuron = Neuron(len(hidden_layers_neurons)+1, i, OUTPUT_NEURON)
            self.output_layer.append(neuron)

#        create biases
        self.hidden_biases = []
        for layer in range(len(hidden_layers_neurons)):
            neuron = Neuron(layer, 0, HIDDEN_BIAS)
            neuron_id += 1
#             weights = []
#             for i in range(hidden_layers_neurons[layer]):
#                 weight = Weight(None, i, np.random.normal())
#                 weights.append(weight)
#             neuron.set_weights(weights)
            self.hidden_biases.append(neuron)
        
        self.output_bias = Neuron(len(hidden_layers_neurons), 0, OUTPUT_BIAS)
        
#        weights
        for i in range(len(self.input_layer)):
            weights = []
            for target in self.hidden_layers[0]:
                weight = Weight(self.input_layer[i].layer, self.input_layer[i].index, target.index, np.random.normal())
                weights.append(weight)
            self.input_layer[i].set_weights(weights)
        
        for layer in range(len(self.hidden_layers)):
            for i in range(len(self.hidden_layers[layer])):
                weights = []
                if (layer == (len(self.hidden_layers) - 1)):
                    targets = self.output_layer
                else:
                    targets = self.hidden_layers[layer + 1]
                for target in targets:
                    weight = Weight(self.hidden_layers[layer][i].layer, self.hidden_layers[layer][i].index, target.index, np.random.normal())
                    weights.append(weight)
                self.hidden_layers[layer][i].set_weights(weights)
        
        for i in range(len(self.hidden_biases)):
            weights = []
            for target in self.hidden_layers[i]:
                weight = Weight(self.hidden_biases[i].layer, 0, target.index, np.random.normal())
                weights.append(weight)
            self.hidden_biases[i].set_weights(weights)
        
        weights = []
        for target in self.output_layer:
            weight = Weight(self.output_bias.layer, 0, target.index, np.random.normal())
            weights.append(weight)
        self.output_bias.set_weights(weights)
                
#         weights = []
#         for i in range(output_layer_neurons):
#             weight = Weight(None, i, np.random.normal())
#             weights.append(weight)
#         self.output_bias.set_weights(weights)

#    set network
    def set_network(self, input_layer, hidden_layers, output_layer, hidden_biases, output_bias):
        self.input_layer = input_layer
        self.hidden_layers = hidden_layers
        self.output_layer = output_layer
        self.hidden_biases = hidden_biases
        self.output_bias = output_bias

#    run network in tensorflow session
    def run_network(self):
#        if hidden layers are empty then network hadn't builded yet
        if(not self.hidden_layers):
            raise BaseException(NETWORK_NETWORK_NOT_BUILDED)
#        if network id is null then network hadn't saved yet
        if(not self.id):
            raise BaseException(NETWORK_NETWORK_NOT_SAVED)
        
#         with tf.device('/CPU:0'):
#        place holder for input layer
        self.x = tf.placeholder("float64", [None, len(self.input_layer)])
#        place holder for expected output to compare with result
        self.y = tf.placeholder("float64", [None, len(self.output_layer)])
        
#        hidden layers
        self.weights = []
        
        weight_value = []
        for neuron in self.input_layer:
            while(len(weight_value) <= neuron.index):
                weight_value.append([])
            for weight in neuron.weights:
                while(len(weight_value[neuron.index]) <= weight.neuron_target_index):
                    weight_value[neuron.index].append(0.0)
                weight_value[neuron.index][weight.neuron_target_index] = weight.value
        weight_layer = tf.Variable(np.array(weight_value))
        self.weights.append(weight_layer)
        
        for layer in self.hidden_layers:
            weight_value = []
            for neuron in layer:
                while(len(weight_value) <= neuron.index):
                    weight_value.append([])
                for weight in neuron.weights:
                    while(len(weight_value[neuron.index]) <= weight.neuron_target_index):
                        weight_value[neuron.index].append(0.0)
                    weight_value[neuron.index][weight.neuron_target_index] = weight.value
            weight_layer = tf.Variable(np.array(weight_value))
            self.weights.append(weight_layer)
        
#        biases
        self.biases = []
        
        for neuron in self.hidden_biases:
            bias_value = []
            for weight in neuron.weights:
                while(len(bias_value) <= weight.neuron_target_index):
                    bias_value.append(0.0)
                bias_value[weight.neuron_target_index] = weight.value
            bias_layer = tf.Variable(np.array(bias_value))
            self.biases.append(bias_layer)
        
        bias_value = []
        for weight in self.output_bias.weights:
            while(len(bias_value) <= weight.neuron_target_index):
                bias_value.append(0.0)
            bias_value[weight.neuron_target_index] = weight.value
        bias_layer = tf.Variable(np.array(bias_value))
        self.biases.append(bias_layer)
        
        self.hidden_layer = []
        for i in range(len(self.hidden_layers)):
            if(i == 0):
                layer = tf.add(tf.matmul(self.x, self.weights[i]), self.biases[i])
            else:
                layer = tf.add(tf.matmul(self.hidden_layer[i-1], self.weights[i]), self.biases[i])
            self.hidden_layer.append(layer)
            
        layer_count = len(self.hidden_layers)
    
#        output layer
        self.out_layer = tf.add(tf.matmul(self.hidden_layer[layer_count-1], self.weights[layer_count]), self.biases[layer_count])
#        prediction result
        self.prediction = tf.nn.sigmoid(self.out_layer)
        self.cross_entropy = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=self.out_layer, labels=self.y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate = self.learning_rate)
        self.train_op = self.optimizer.minimize(self.cross_entropy)
        
        self.correct_pred = tf.equal(self.y, self.prediction)
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
        self.init = tf.global_variables_initializer()
        
#        session
        self.sess = tf.Session()#config=tf.ConfigProto(log_device_placement=True))
        self.sess.run(self.init)
    
#    stop tensorflow network
    def stop_network(self):
        if (self.sess):
            self.sess.close()
        self.sess = None 
    
#    train the network
    def train(self, input, output, max_epoch=1000, error_rate=0.15):
#        if session is null, network is not running
        if (not self.sess):
            raise BaseException(NETWORK_NETWORK_NOT_RUNNING)
        
        epoch = 0
        error = 1.0
        while((epoch < max_epoch) and (error > error_rate)):
            _, accuracy = self.sess.run([self.train_op, self.accuracy], feed_dict={self.x: np.array(input, dtype=np.float32), self.y:np.array(output, dtype=np.float32)})
            
            error = 1.0 - accuracy
            epoch += 1
        
#        save tensorflow network to network class
        weights, biases = self.sess.run([self.weights, self.biases], feed_dict={self.x: np.array(input, dtype=np.float32), self.y:np.array(output, dtype=np.float32)})
        self.build_from_model(weights, biases)
        return epoch, accuracy
       
#    build weights and biases from model
    def build_from_model(self, weights, biases):
        for layer in range(len(weights)):
            if (layer == 0):
                for neuron in self.input_layer:
                    for weight in neuron.weights:
                        weight.value = weights[neuron.layer][neuron.index][weight.neuron_target_index]
            else:
                for neuron in self.hidden_layers[layer-1]:
                    for weight in neuron.weights:
                        weight.value = weights[neuron.layer][neuron.index][weight.neuron_target_index]
        
        for layer in range(len(biases)):
            if (layer == len(biases)-1):
                for weight in self.output_bias.weights:
                    weight.value = weights[self.output_bias.layer][self.output_bias.index][weight.neuron_target_index]
            else:
                for weight in self.hidden_biases[layer].weights:
                    weight.value = weights[self.hidden_biases[layer].layer][self.hidden_biases[layer].index][weight.neuron_target_index]
    
#    predict
    def predict(self, input):
#        if session is null, network is not running
        if (not self.sess):
            raise BaseException(NETWORK_NETWORK_NOT_RUNNING)
        
        prediction = self.sess.run([self.prediction], feed_dict={self.x: np.array(input, dtype=np.float32)})
        
        return prediction
    