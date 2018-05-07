'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''

from flask import Flask, jsonify, Response, make_response
import json
from chatbot.category.categoriesapi import CategoriesAPIService
from chatbot.category.context.contextsapi import ContextsAPIService
from database import Database
from database.source import *
from json.decoder import JSONArray
from tornado.escape import json_encode
from chatbot.category.categorydb import CategoryDBService
from chatbot.category.context.contextdb import ContextDBService
from chatbot.response.responsedb import ResponseDBService
from chatbot.category.context.intent.intentdb import IntentDBService
from chatbot.record.recorddb import RecordDBService
from chatbot.training.trainingdb import TrainingDBService
from chatbot.chatbotapi import ChatBotAPIService
from neuralnetwork.neuralnetworkdb import NeuralNetworkDBService
from neuralnetwork.weight.weightdb import WeightDBService
from neuralnetwork.neuron.neurondb import NeuronDBService
from chatbot.word.worddb import WordDBService
from chatbot.response.responsesapi import ResponsesAPIService
from chatbot.record.recordsapi import RecordsAPIService
from auth.user.userdb import UserDBService
from auth.authapi import AuthAPIService


class Server:
    app = None
    database = None
    route = None
    
    category_dbs = None
    context_dbs = None
    intent_dbs = None
    record_dbs = None
    training_dbs = None
    response_dbs = None
    
    nn_dbs = None
    neuron_dbs = None
    weight_dbs = None
    
    category_api = None
    context_api = None
    chatbot_api = None
    response_api = None
    record_api = None
    
#    constructor
    def __init__(self):
        self.app = Flask("EGEROO")
        self.app.config['SECRET_KEY'] = SECRET_KEY
        
        self.route = "/chatbot"
        self.database = Database(DB_HOST, DB_NAME, USER, PASSWORD)
        self.database.open_connection()
        
        self.category_dbs = CategoryDBService(self.database)
        self.context_dbs = ContextDBService(self.database)
        self.intent_dbs = IntentDBService(self.database)
        self.record_dbs = RecordDBService(self.database, self.category_dbs, self.context_dbs, self.intent_dbs)
        self.training_dbs = TrainingDBService(self.database, self.record_dbs, self.category_dbs, self.context_dbs, self.intent_dbs)
        self.response_dbs = ResponseDBService(self.database)
        
        self.weight_dbs = WeightDBService()
        self.neuron_dbs = NeuronDBService(self.database)
        self.word_dbs = WordDBService(self.database, self.neuron_dbs)
        self.nn_dbs = NeuralNetworkDBService(self.database, self.neuron_dbs, self.weight_dbs, self.word_dbs)
        
        self.user_dbs = UserDBService(self.database)
        self.auth_api = AuthAPIService(self.user_dbs, self.app, self.route)
        
        self.context_api = ContextsAPIService(self.context_dbs, self.response_dbs, self.auth_api, self.app, self.route)
        self.response_api = ResponsesAPIService(self.response_dbs, self.category_dbs, self.context_dbs, self.auth_api, self.app, self.route)
        self.record_api = RecordsAPIService(self.category_dbs, self.context_dbs, self.record_dbs, self.training_dbs, self.auth_api, self.app, self.route)
        self.chatbot_api = ChatBotAPIService(self.record_dbs, self.training_dbs, self.category_dbs, 
                                             self.context_dbs, self.nn_dbs, self.word_dbs, 
                                             self.neuron_dbs, self.weight_dbs, self.response_dbs, self.auth_api, self.database, self.app, self.route)

#    run server
    def run(self, host='127.0.0.1', port=5000):
        self.app.run(host=host, port=port)