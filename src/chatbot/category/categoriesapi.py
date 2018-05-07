'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''
from flask import jsonify, Response, make_response
from chatbot.category import Category, CategoryLibrarySerializer
from chatbot.category import CategorySerializer
from chatbot.category.categorydb import CategoryDBService
from flask.globals import request
from exception.exception import *
from exception import ApiError
from chatbot.category.context.contextdb import ContextDBService
from chatbot.response.responsedb import ResponseDBService

class CategoriesAPIService:
    app = None
    root = None
    category_dbs = None
    context_dbs = None
    response_dbs = None

    def __init__(self, category_dbs, context_dbs, response_dbs, app, root):
        self.app = app
        self.root = root
        self.category_dbs = category_dbs
        self.context_dbs = context_dbs
        self.response_dbs = response_dbs
        self.build_api()
    
    def get_route(self, route):
        return (self.root + route)
    
    def build_api(self):
        app = self.app
        
#         @app.route(self.get_route('/lib'), methods=['GET','OPTIONS'])
#         def get_libraries():
#             if (request.method == "OPTIONS"):
#                 resp = Response("OK")
#                 resp.headers["Access-Control-Allow-Origin"] = '*'
#                 resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
#                 resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
#                 resp.headers["Access-Control-Max-Age"] = "1728000"
#                 return resp
#             elif (request.method == "GET"):
#                 tenantid = request.headers['tenant-id']
#                 categories = self.category_dbs.get_visible_categories(tenantid)
#                 for category in categories:
#                     contexts = self.context_dbs.retrieve_contexts(category.id, tenantid)
#                     c_contexts = []
#                     for context in contexts:
#                         if(context.context_id):
#                             responses = self.response_dbs.retrieve_responses(context.id, tenantid)
#                             context.set_responses(responses)
#                             c_contexts.append(context)
#                     category.set_contexts(c_contexts)
#                 jsons = CategoryLibrarySerializer(categories, many=True).data
#                 
#                 resp = make_response(jsonify(jsons), 200)
#                 return resp
        
#         @app.route(self.get_route('/categories'), methods=['GET', 'OPTIONS'])
#         def get_all_categories():
#             tenantid = request.headers['tenant-id']
#             data = self.category_dbs.get_visible_categories(tenantid)
#             jsons = CategorySerializer(data, many=True).data
#             return jsonify(jsons)
#         
#         @app.route(self.get_route('/category/<category_id>'), methods=['GET'])
#         def category_operations(category_id):
#             tenantid = request.headers['tenant-id']
#             category = self.category_dbs.retrieve_category(category_id, tenantid)
#             if (not category):
#                 raise ApiError(CHATBOT_CATEGORY_NOT_FOUND)
#             if (request.method == 'GET'):
#                 jsons = CategorySerializer(category).data
#             
#             return jsonify(jsons)
                