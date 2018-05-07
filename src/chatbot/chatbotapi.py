'''
Created on Mar 19, 2018

@author: ridwan
'''
from flask import jsonify, g
from flask_httpauth import HTTPBasicAuth
from flask.globals import request
from exception import ApiError
from chatbot.record.recorddb import RecordDBService
from chatbot.training.trainingdb import TrainingDBService
from chatbot.category.categorydb import CategoryDBService
from chatbot.category.context.contextdb import ContextDBService
from chatbot.record import Record
from chatbot.category import UNCATEGORIZED, CategoryLibrarySerializer
from chatbot.training import Training, TrainingSerializer
from neuralnetwork.neuralnetworkdb import NeuralNetworkDBService
from datetime import datetime, timedelta
from neuralnetwork.neuron.neurondb import NeuronDBService
from neuralnetwork.weight.weightdb import WeightDBService
from chatbot.word import NeuronBow, RawWord, RawWordSerializer, WordSerializer
from chatbot.response.responsedb import ResponseDBService
import random
from neuralnetwork import NeuralNetwork
from flask.wrappers import Response
from nltk.tokenize import TweetTokenizer
from database.source import *
from chatbot.category.context import NO_CONTEXT_UNCATEGORIZED
from flask.helpers import make_response
from validator import APIValidator
from validator.paramtype import ParamType
from exception.exception import *
from auth.user import *
from passlib.apps import custom_app_context as pwd_context
import os
import math

MAX_EPOCH = 10000
ERROR_RATE = 0.15
WORD_THRESHOLD = 0.5

POST_TRAIN_PARAM = [ParamType("training_data", str, False, True, False),
                    ParamType("max_epoch", int, False, False, False),
                    ParamType("error_rate", float, False, False, False),
                    ParamType("data", int, False, False, True)]
POST_CHAT_PARAM = [ParamType("sentence", str, False, True, False),
                   ParamType("category", int, False, True, False),
                   ParamType("context", int, False, True, False)]
PUT_MAPWORD_PARAM = [ParamType("id", int, False, True, False),
                      ParamType("word_id", int, False, False, False)]
PUT_MULTIPLE_MAPWORD_PARAM = [ParamType("map", PUT_MAPWORD_PARAM, True, True, True)]

class ChatBotAPIService:
    app = None
    root = None
    database = None
    auth_api = None
    api_validator = None
    record_dbs = None
    training_dbs = None
    category_dbs = None
    context_dbs = None
    nn_dbs = None
    neuron_dbs = None
    weight_dbs = None
    word_dbs = None
    response_dbs = None
    
    classifiers = {}
    word_tokenizers = {}
    tokenizer = TweetTokenizer()

#    constructor
    def __init__(self, record_dbs, training_dbs, category_dbs, context_dbs, 
                 nn_dbs, word_dbs, neuron_dbs, weight_dbs,
                 response_dbs, auth_api, database, app, root):
        self.app = app
        self.root = root
        self.database = database
        self.auth_api = auth_api
        self.api_validator = APIValidator()
        self.record_dbs = record_dbs
        self.training_dbs = training_dbs
        self.category_dbs = category_dbs
        self.context_dbs = context_dbs
        self.nn_dbs = nn_dbs
        self.word_dbs = word_dbs
        self.neuron_dbs = neuron_dbs
        self.weight_dbs = weight_dbs
        self.response_dbs = response_dbs
        
        self.tenants = database.get_tenants()
        self.classifiers = {}
        self.word_tokenizers = {}
        for tenant in self.tenants:
            if not os.path.exists(os.path.join("tenant-data", tenant)):
                os.makedirs(os.path.join("tenant-data", tenant))
            self.classifiers[tenant] = self.nn_dbs.retrieve_and_build_network(NETWORK_NAME_CLASSIFIER, tenant)
            if (self.classifiers[tenant]):
                self.classifiers[tenant].run_network()
            else:
                self.clear_network(tenant)
                self.classifiers[tenant].run_network()
            self.word_tokenizers[tenant] = self.nn_dbs.retrieve_and_build_network(NETWORK_NAME_WORD_TOKENIZER, tenant)
            if (self.word_tokenizers[tenant]):
                self.word_tokenizers[tenant].run_network()
            else:
                self.clear_word_tokenizers(tenant)
                self.word_tokenizers[tenant].run_network()
        self.build_api()

#    verify network is compatible with training data
    def verify_network(self, training_data, tenantid):
        words = []
        for data in training_data:
            words.extend(self.tokenizer.tokenize(data.record.sentence))
        words = list(set(words))

#        verify input neuron is exists for each word
        for w in words:
            neuronbow = self.word_dbs.retrieve_neuronbow_by_word(w.lower(), NETWORK_NAME_CLASSIFIER, tenantid)
            if (not neuronbow):
                word = self.word_dbs.retrieve_word_by_word(w.lower(), tenantid)
                if (word == None):
                    rawword = self.word_dbs.retrieve_rawword_by_word(w.lower(), tenantid)
                    if (rawword != None and rawword.word_id != None):
                        word = self.word_dbs.retrieve_word(rawword.word_id, tenantid)
                    else:
                        rawword = RawWord(w.lower(), None)
                        self.word_dbs.save_rawword(rawword, tenantid)
                        
                if (word):
                    neuron = self.classifiers[tenantid].input_layer[self.classifiers[tenantid].add_input_neuron()]
                    neuronbow = NeuronBow(word.value, None, None)
                    neuron.set_bow(neuronbow)
                    self.classifiers[tenantid].input_layer[len(self.classifiers[tenantid].input_layer)-1] = neuron

#        verify input and output neurons are exists for each category
        for i in range(self.category_dbs.max_categoryid(tenantid)):
            neuronbow = self.word_dbs.retrieve_neuronbow_by_category(i, NETWORK_NAME_CLASSIFIER, tenantid)
            if (not neuronbow):
#                input layer
                neuron = self.classifiers[tenantid].input_layer[self.classifiers[tenantid].add_input_neuron()]
                neuronbow = NeuronBow(None, i, None)
                neuron.set_bow(neuronbow)
                self.classifiers[tenantid].input_layer[len(self.classifiers[tenantid].input_layer)-1] = neuron
                
#                output layer
                neuron = self.classifiers[tenantid].output_layer[self.classifiers[tenantid].add_output_neuron()]
                neuronbow = NeuronBow(None, i, None)
                neuron.set_bow(neuronbow)
                self.classifiers[tenantid].output_layer[len(self.classifiers[tenantid].output_layer)-1] = neuron

#        verify input and output neurons are exists for each context
        for i in range(self.context_dbs.max_contextid(tenantid)):
            neuronbow = self.word_dbs.retrieve_neuronbow_by_context(i, NETWORK_NAME_CLASSIFIER, tenantid)
            if (not neuronbow):
#                input layer
                neuron = self.classifiers[tenantid].input_layer[self.classifiers[tenantid].add_input_neuron()]
                neuronbow = NeuronBow(None, None, i)
                neuron.set_bow(neuronbow)
                self.classifiers[tenantid].input_layer[len(self.classifiers[tenantid].input_layer)-1] = neuron
                
                #output layer
                neuron = self.classifiers[tenantid].output_layer[self.classifiers[tenantid].add_output_neuron()]
                neuronbow = NeuronBow(None, None, i)
                neuron.set_bow(neuronbow)
                self.classifiers[tenantid].output_layer[len(self.classifiers[tenantid].output_layer)-1] = neuron
        
        self.nn_dbs.update_neural_network(self.classifiers[tenantid], tenantid)
        
        
    def verify_network_word_mapper(self, training_data, tenantid):
        for data in training_data:
            word = self.word_dbs.retrieve_word(data.word_id, tenantid)
            if word:
                neuronbow = self.word_dbs.retrieve_neuronbow_by_word(word.value, NETWORK_NAME_WORD_TOKENIZER, tenantid)
                if (not neuronbow):
                    neuron = self.word_tokenizers[tenantid].output_layer[self.word_tokenizers[tenantid].add_output_neuron()]
                    neuronbow = NeuronBow(word.value, None, None)
                    neuron.set_bow(neuronbow)
                    self.word_tokenizers[tenantid].output_layer[len(self.word_tokenizers[tenantid].output_layer)-1] = neuron
        
                    self.nn_dbs.update_neural_network(self.word_tokenizers[tenantid], tenantid)
        
#    check if word exists in dictionary
    def check_word(self, w, tenantid):
        word = self.word_dbs.retrieve_word_by_word(w, tenantid)
        if (word == None):
            rawword = self.word_dbs.retrieve_rawword_by_word(w, tenantid)
            if (rawword == None):
                rawword = RawWord(w, None)
                self.word_dbs.save_rawword(rawword, tenantid)

    def create_mapper_bow(self, rawword, tenantid):
        input_bow = [0] * 256
        for i in range(len(rawword.value)):
            input_bow[ord(rawword.value[i])] += (1 / (1 + math.exp(-i)))
            
        output_bow = []
        for neuron in self.word_tokenizers[tenantid].output_layer:
            while(len(output_bow) <= neuron.index):
                output_bow.append(0)
            word = self.word_dbs.retrieve_word_by_word(neuron.bow.word, tenantid)
            if (rawword.word_id != None):
                if (word.id == rawword.word_id):
                    output_bow[neuron.index] += 1
        
        return input_bow, output_bow

#    create input and output bow
    def create_bow(self, sentence, prev_category, prev_context, category, context, tenantid):
        words = self.tokenizer.tokenize(sentence)
        for i in range(len(words)):
            words[i] = words[i].lower()
            self.check_word(words[i], tenantid)
            
        mapped_word = []
        for word in words:
            mapped_word.append(self.predict_word(word, tenantid))
        
        inputbow = []
        for neuron in self.classifiers[tenantid].input_layer:
            while(len(inputbow) <= neuron.index):
                inputbow.append(0)
            if(neuron.bow.word != None):
                word = self.word_dbs.retrieve_word_by_word(neuron.bow.word, tenantid)
                if word and word.value in words:
                    inputbow[neuron.index] += 1.0
                else:
                    for mw in mapped_word:
                        for m in mw:
                            if(neuron.bow.word == m['word'] and m['conf'] > WORD_THRESHOLD):
                                inputbow[neuron.index] += m['conf']
            elif(neuron.bow.category != None):
                if(neuron.bow.category == prev_category.category_id):
                    inputbow[neuron.index] += 0.5
            elif(neuron.bow.context != None):
                if(neuron.bow.context == prev_context.context_id):
                    inputbow[neuron.index] += 0.3
        
        outputbow = []
        for neuron in self.classifiers[tenantid].output_layer:
            while(len(outputbow) <= neuron.index):
                outputbow.append(0)
            if(neuron.bow.category != None):
                if(neuron.bow.category == category.category_id):
                    outputbow[neuron.index] += 1.0
            elif(neuron.bow.context != None):
                if(neuron.bow.context == context.context_id):
                    outputbow[neuron.index] += 1.0
        
        return inputbow, outputbow

#    convert bow to category, context, and confidence level
    def convert_bow(self, bow, tenantid):
        category = 0
        context = 0
        category_conf = 0.0
        context_conf = 0.0
        for i in range(len(bow)):
            neuronbow = self.word_dbs.retrieve_output_neuronbow_by_neuronindex(NETWORK_NAME_CLASSIFIER, i, tenantid)
            
            if(neuronbow.category != None and bow[i] > category_conf):
                category = neuronbow.category
                category_conf = bow[i]
            elif(neuronbow.context != None and bow[i] > context_conf):
                context = neuronbow.context
                context_conf = bow[i]
        conf = (category_conf + context_conf) / 2
        
        return category, context, conf
    
    def clear_word_tokenizers(self, tenantid):
        if(self.word_tokenizers[tenantid]):
            self.word_tokenizers[tenantid].stop_network()
            self.nn.dbs.delete_neural_network(self.word_tokenizers[tenantid], tenantid)
        self.word_tokenizers[tenantid] = NeuralNetwork(NETWORK_NAME_WORD_TOKENIZER, learning_rate=0.1, id=2)
        words = self.word_dbs.retrieve_mapped_rawwords(tenantid)
        self.word_tokenizers[tenantid].build_new(input_layer_neurons=0, hidden_layers_neurons=[300, 300], output_layer_neurons=0)
        try:
            self.word_tokenizers[tenantid].id = self.nn_dbs.save_neural_network(self.word_tokenizers[tenantid], tenantid)
        except BaseException as e:
            raise ApiError(e.args)
        
        for i in range(256):
            neuron = self.word_tokenizers[tenantid].input_layer[self.word_tokenizers[tenantid].add_input_neuron()]
            neuron_bow = NeuronBow(None, None, None)
            neuron_bow.set_ascii(i)
            neuron.set_bow(neuron_bow)
            self.word_tokenizers[tenantid].input_layer[len(self.word_tokenizers[tenantid].input_layer)-1] = neuron
        
        for i in range(len(words)):
            word = self.word_dbs.retrieve_word(words[i].word_id, tenantid)
            if word:
                neuron_bow = self.word_dbs.retrieve_neuronbow_by_word(word.value, NETWORK_NAME_WORD_TOKENIZER, tenantid)
                if not neuron_bow:
                    neuron = self.word_tokenizers[tenantid].output_layer[self.word_tokenizers[tenantid].add_output_neuron()]
                    neuron_bow = NeuronBow(word.value, None, None)
                    neuron.set_bow(neuron_bow)
                    self.word_tokenizers[tenantid].output_layer[len(self.word_tokenizers[tenantid].output_layer)-1] = neuron
                    self.nn_dbs.update_neural_network(self.word_tokenizers[tenantid], tenantid)
        
        input_data = []
        output_data = []
        
        for word in words:
            input_bow, output_bow = self.create_mapper_bow(word, tenantid)
            input_data.append(input_bow)
            output_data.append(output_bow)
        
        self.word_tokenizers[tenantid].run_network()
        if (input_data):
            epoch, accuracy = self.word_tokenizers[tenantid].train(input_data, output_data, max_epoch= 1000, error_rate=0.8)
        self.nn_dbs.update_neural_network(self.word_tokenizers[tenantid], tenantid)
    
    def predict_word(self, word, tenantid):
        input_bow, output_bow = self.create_mapper_bow(RawWord(word, None), tenantid)
        prediction = self.word_tokenizers[tenantid].predict([input_bow])[0][0]
        
        result = []
        for neuron in self.word_tokenizers[tenantid].output_layer:
            while len(result) <= neuron.index:
                result.append(None)
            result[neuron.index] = {"word": neuron.bow.word, "conf": prediction[neuron.index]}
        
        return result
    
    def clear_network(self, tenantid):
        if(self.classifiers[tenantid]):
            self.classifiers[tenantid].stop_network()
            self.nn_dbs.delete_neural_network(self.classifiers[tenantid], tenantid)
        self.classifiers[tenantid] = NeuralNetwork(NETWORK_NAME_CLASSIFIER, learning_rate=0.1, id=1)
        self.classifiers[tenantid].build_new(input_layer_neurons=0, hidden_layers_neurons=[300, 300], output_layer_neurons=0)
        try:
            self.classifiers[tenantid].id = self.nn_dbs.save_neural_network(self.classifiers[tenantid], tenantid)
        except BaseException as e:
            raise ApiError(e.args)
        
        for i in range(self.category_dbs.max_categoryid(tenantid) + 1):
            #input layer
            neuron = self.classifiers[tenantid].input_layer[self.classifiers[tenantid].add_input_neuron()]
            neuron_bow = NeuronBow(None, i, None)
            neuron.set_bow(neuron_bow)
            self.classifiers[tenantid].input_layer[len(self.classifiers[tenantid].input_layer)-1] = neuron
                
            #output layer
            neuron = self.classifiers[tenantid].output_layer[self.classifiers[tenantid].add_output_neuron()]
            neuron_bow = NeuronBow(None, i, None)
            neuron.set_bow(neuron_bow)
            self.classifiers[tenantid].output_layer[len(self.classifiers[tenantid].output_layer)-1] = neuron
        
        for i in range(self.context_dbs.max_contextid(tenantid) + 1):
            #input layer
            neuron = self.classifiers[tenantid].input_layer[self.classifiers[tenantid].add_input_neuron()]
            neuron_bow = NeuronBow(None, None, i)
            neuron.set_bow(neuron_bow)
            self.classifiers[tenantid].input_layer[len(self.classifiers[tenantid].input_layer)-1] = neuron
            
            #output layer
            neuron = self.classifiers[tenantid].output_layer[self.classifiers[tenantid].add_output_neuron()]
            neuron_bow = NeuronBow(None, None, i)
            neuron.set_bow(neuron_bow)
            self.classifiers[tenantid].output_layer[len(self.classifiers[tenantid].output_layer)-1] = neuron
        
        category = self.category_dbs.retrieve_category_by_categoryid(0, tenantid)
        context = self.context_dbs.retrieve_context_by_categorycontextid(0, 0, tenantid)
        input, output = self.create_bow("", category, context, category, context, tenantid)
        
        self.classifiers[tenantid].run_network()
        epoch, accuracy = self.classifiers[tenantid].train([input], [output], max_epoch= 100, error_rate=0.8)
        self.nn_dbs.update_neural_network(self.classifiers[tenantid], tenantid)
        
#    get route
    def get_route(self, route):
        return (self.root + route)
    
    def build_api(self):
        app = self.app
        auth = self.auth_api.auth
        
        @app.route(self.get_route('/lib'), methods=['GET','OPTIONS'])
        @auth.login_required
        def get_libraries():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else: 
                if(request.method == "GET"):
                    valid, error = self.api_validator.check_request(request, None)
                    if not valid:
                        return make_response(error, 400)
                    
                    tenantid = request.headers['tenant-id']
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    categories = self.category_dbs.get_visible_categories(tenantid)
                    for category in categories:
                        contexts = self.context_dbs.retrieve_contexts(category.id, tenantid)
                        c_contexts = []
                        for context in contexts:
                            if(context.context_id):
                                responses = self.response_dbs.retrieve_responses(context.id, tenantid)
                                context.set_responses(responses)
                                c_contexts.append(context)
                        category.set_contexts(c_contexts)
                    jsons = CategoryLibrarySerializer(categories, many=True).data
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/chat'), methods=['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def chat():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                if (request.method == 'POST'):
                    if not self.auth_api.permitted(g.user.id, [USER, ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, POST_CHAT_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    sentence = request.json['sentence']
                    category = request.json['category']
                    context = request.json['context']
                    category = self.category_dbs.retrieve_category_by_categoryid(category, tenantid)
                    context = self.context_dbs.retrieve_context_by_categorycontextid(category.category_id, context, tenantid)
                    category_id = 0
                    context_id = 0
                    conf = 1.0
                    
                    inputbow, outputbow = self.create_bow(sentence, category, context, category, context, tenantid)
                    
                    if (sum(inputbow) > 0.8):
                        prediction = self.classifiers[tenantid].predict([inputbow])[0][0]
                        category_id, context_id, conf = self.convert_bow(prediction, tenantid)
                        context = self.context_dbs.retrieve_context_by_categorycontextid(category_id, context_id, tenantid)
                    
                    if(not context):
                        category_id = 0
                        context_id = 0
                        conf = 1.0
                        context = self.context_dbs.retrieve_context_by_categorycontextid(category_id, context_id, tenantid)
                    
                    responses = self.response_dbs.retrieve_responses(context.id, tenantid)
                    
                    if (not responses):
                        context = self.context_dbs.retrieve_context_by_categorycontextid(0, 0, tenantid)
                        responses = self.response_dbs.retrieve_responses(context.id, tenantid)
                        
                    i = random.randint(0, (len(responses) - 1))
                    
                    jsons = {"sentence":responses[i].sentence, "category": category_id, "context": context_id, "confidence": conf}
                
                return make_response(jsonify(jsons), 200)
            
        @app.route(self.get_route('/train'), methods=['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def train_chatbot():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                if (request.method == 'POST'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, POST_TRAIN_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    training = request.json['training_data']
                    if (training == 'all'):
                        data = self.training_dbs.retrieve_training_categorized_ids(tenantid)
                    if (training == 'data'):
                        if not ('data' in request.json):
                            return make_response(TRAINING_DATA_MANDATORY, 400)
                        data = request.json['data']
                    max_epoch = MAX_EPOCH
                    if(('max_epoch' in request.json) and request.json['max_epoch']):
                        max_epoch = request.json['max_epoch']
                    error_rate = ERROR_RATE
                    if(('error_rate' in request.json) and request.json['error_rate']):
                        error_rate = request.json['error_rate']
                    training_input_data = []
                    training_output_data = []
                    trainings = []
                    for d in data:
                        training = self.training_dbs.retrieve_training(d, tenantid)
                        trainings.append(training)
                    
                    self.verify_network(trainings, tenantid)
                    
                    for training in trainings:
                        if(training.context and training.category):
                            input, output = self.create_bow(training.record.sentence, training.record.category, training.record.context, training.category, training.context, tenantid)
                            
                            if (training.record.category.category_id == 0 or training.record.context.context_id == 0):
                                input, output = self.create_bow(training.record.sentence, UNCATEGORIZED, NO_CONTEXT_UNCATEGORIZED, training.category, training.context, tenantid)
                            
                        else:
                            input, output = self.create_bow(training.record.sentence, training.record.category, training.record.context, training.record.category, training.record.context, tenantid)
                        
                        training_input_data.append(input)
                        training_output_data.append(output)
                    
#                     input, output = self.create_bow("", UNCATEGORIZED, NO_CONTEXT_UNCATEGORIZED, UNCATEGORIZED, NO_CONTEXT_UNCATEGORIZED, tenantid)
                    
                    for i in range(len(trainings)):
                        training_input_data.append(input)
                        training_output_data.append(output)
                    
                    self.classifiers[tenantid].stop_network()
                    self.classifiers[tenantid].run_network()
                    epoch, accuracy = self.classifiers[tenantid].train(training_input_data, training_output_data, max_epoch= max_epoch, error_rate=error_rate)
                    self.nn_dbs.update_neural_network(self.classifiers[tenantid], tenantid)
                    
                    jsons = {"epoch": epoch, "accuracy": str(accuracy)}
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/clear'), methods=['GET', 'OPTIONS'])
        @auth.login_required
        def clear_knowledge():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                
                if (request.method == 'GET'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    
                    self.clear_network(tenantid)
                    
                    jsons = Response("Success")
                
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/wordmap'), methods=['GET','OPTIONS'])
        @auth.login_required
        def get_wordmap():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else: 
                if(request.method == "GET"):
                    valid, error = self.api_validator.check_request(request, None)
                    if not valid:
                        return make_response(error, 400)
                    
                    tenantid = request.headers['tenant-id']
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    
                    rawwords = self.word_dbs.retrieve_rawwords(tenantid)
                    for i in range(len(rawwords)):
                        if (rawwords[i].word_id != None):
                            rawwords[i].set_word(self.word_dbs.retrieve_word(rawwords[i].word_id, tenantid).value)
                    jsons = RawWordSerializer(rawwords, many=True).data
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/similarword/<word>'), methods=['GET','OPTIONS'])
        @auth.login_required
        def search_similar_words(word):
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else: 
                if(request.method == "GET"):
                    valid, error = self.api_validator.check_request(request, None)
                    if not valid:
                        return make_response(error, 400)
                    
                    tenantid = request.headers['tenant-id']
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    
                    similar_words = self.word_dbs.retrieve_similar_words(word, 10, tenantid)
                    jsons = WordSerializer(similar_words, many=True).data
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/wordmaps'), methods=['GET', 'PUT', 'OPTIONS'])
        @auth.login_required
        def map_word():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                if (request.method == 'PUT'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, PUT_MULTIPLE_MAPWORD_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    data = request.json['map']
                    results = []
                    for d in data:
                        rawword = self.word_dbs.retrieve_rawword(d['id'], tenantid)
                        if rawword:
                            word = self.word_dbs.retrieve_word(d['word_id'], tenantid)
                            if word:
                                rawword.word_id = word.id
                                dbresult = self.word_dbs.update_rawword(rawword, tenantid)
                                results.append(dbresult)
                    
                    jsons = {"resource_ids": results}
                
                return make_response(jsonify(jsons), 200)
            
        @app.route(self.get_route('/trainwordmapper'), methods=['GET', 'OPTIONS'])
        @auth.login_required
        def train_word_mapper():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                if (request.method == 'GET'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    
                    data = self.word_dbs.retrieve_mapped_rawwords(tenantid)
                    words = self.word_dbs.retrieve_words(tenantid)
                    
                    training_input_data = []
                    training_output_data = []
                    
                    self.verify_network_word_mapper(data, tenantid)
                    
                    for d in data:
                        input_bow, output_bow = self.create_mapper_bow(d, tenantid)
                        
                        training_input_data.append(input_bow)
                        training_output_data.append(output_bow)
                    
                    self.word_tokenizers[tenantid].stop_network()
                    self.word_tokenizers[tenantid].run_network()
                    epoch, accuracy = self.word_tokenizers[tenantid].train(training_input_data, training_output_data, max_epoch= MAX_EPOCH, error_rate=ERROR_RATE)
                    self.nn_dbs.update_neural_network(self.word_tokenizers[tenantid], tenantid)
                    
                    jsons = {"epoch": epoch, "accuracy": str(accuracy)}
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/clearwordmapper'), methods=['GET', 'OPTIONS'])
        @auth.login_required
        def clear_wordmapper():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                
                if (request.method == 'GET'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    
                    self.clear_word_tokenizers(tenantid)
                    
                    jsons = Response("Success")
                
                return make_response(jsonify(jsons), 200)
            
        @app.route(self.get_route('/tenant'), methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
        def tenant_operations():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                if ('tenant-id' in request.headers) and (request.headers['tenant-id'] == DB_NAME):
                    content = request.json
                    if ('validation_key' in content) and (content['validation_key'] != None) and (type(content['validation_key']) is str) and pwd_context.verify(content['validation_key'], VALIDATION_KEY):
                        if ('id' in content) and (content['id'] != None) and (type(content['id']) is str):
                            if (request.method == 'POST'):
                                existing_tenant = list(filter(lambda x: x == content['id'], self.tenants))
                                if not existing_tenant:
                                    self.database.close_connection()
                                    tenantid = self.database.create_tenant(content['id'])
                                    self.database.open_connection()
                                    
                                    self.tenants.append(tenantid)
                                    self.classifiers[tenantid] = None
                                    self.clear_network(tenantid)
                                    if (self.classifiers[tenantid]):
                                        self.classifiers[tenantid].run_network()
                                    self.word_tokenizers[tenantid] = None
                                    self.clear_word_tokenizers(tenantid)
                                    if (self.word_tokenizers[tenantid]):
                                        self.word_tokenizers[tenantid].run_network()
                                        
                                    jsons = {"tenant-id": tenantid}
                                    return make_response(jsonify(jsons), 200)
                            elif (request.method == 'DELETE'):
                                existing_tenant = list(filter(lambda x: x == content['id'], self.tenants))
                                if existing_tenant:
                                    self.database.close_connection()
                                    tenantid = self.database.delete_tenant(content['id'])
                                    self.database.open_connection()
                                    
                                    if (tenantid):
                                        self.tenants.remove(tenantid)
                                        self.classifiers[tenantid].stop_network()
                                        self.classifiers[tenantid] = None
                                        jsons = {"tenant-id": tenantid}
                                        
                                        return make_response(jsonify(jsons), 200)
            
            return make_response("OK", 200)
        