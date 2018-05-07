'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''
from flask import jsonify, make_response
from chatbot.category.context import Context
from chatbot.category.context import ContextSerializer
from chatbot.category.context.contextdb import ContextDBService
from chatbot.response import Response
from flask.globals import request
from exception.exception import *
from exception import ApiError
from validator.paramtype import ParamType
from validator import APIValidator
from auth.user import *
from flask import jsonify, g
from chatbot.response.responsesapi import POST_RESPONSE_PARAM

POST_CONTEXT_PARAM = [ParamType("name", str, False, True, False),
                      ParamType("category_id", int, False, True, False),
                      ParamType("responses", POST_RESPONSE_PARAM, True, True, True)]
PUT_CONTEXT_PARAM = [ParamType("name", str, False, True, False)]

class ContextsAPIService:
    app = None
    root = None
    auth_api = None
    api_validator = None
    context_dbs = None
    response_dbs = None
    
    def __init__(self, context_dbs, response_dbs, auth_api, app, root):
        self.app = app
        self.root = root
        self.auth_api = auth_api
        self.api_validator = APIValidator()
        self.context_dbs = context_dbs
        self.response_dbs = response_dbs
        
        self.build_api()
    
    def get_route(self, route):
        return (self.root + route)
    
    def build_api(self):
        app = self.app
        auth = self.auth_api.auth
        
#         @app.route(self.get_route('/contexts/<category_id>'), methods=['GET'])
#         def get_all_contexts(category_id):
#             tenantid = request.headers['tenant-id']
#             data = self.context_dbs.retrieve_contexts(category_id, tenantid)
#             jsons = ContextSerializer(data, many=True).data
#             return jsonify(jsons)
        
        @app.route(self.get_route('/context'), methods=['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def save_context():
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
                if (request.method == "POST"):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, POST_CONTEXT_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    
                    if len(content['responses']) == 0:
                        return make_response(CHATBOT_CONTEXT_NO_RESPONSE, 400)
                    
                    context = Context(content['name'], content['category_id'])
                    context.id = self.context_dbs.save_context(context, tenantid, commit=False)
                    
                    for response_json in content['responses']:
                        response = Response(response_json['sentence'], context.id)
                        self.response_dbs.save_response(response, tenantid, commit=False)
                    
                    self.response_dbs.database.commit(tenantid)
                    self.context_dbs.database.commit(tenantid)
                    jsons = {"resource_id": context.id}
                
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/contexts'), methods=['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def save_contexts():
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
                if (request.method == "POST"):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, POST_CONTEXT_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    json_list = request.json
                    
                    result = []
                    for content in json_list:
                        if len(content['responses']) == 0:
                            return make_response(CHATBOT_CONTEXT_NO_RESPONSE, 400)
                        
                        context = Context(content['name'], content['category_id'])
                        context.id = self.context_dbs.save_context(context, tenantid, commit=False)
                        
                        for response_json in content['responses']:
                            response = Response(response_json['sentence'], context.id)
                            self.response_dbs.save_response(response, tenantid, commit=False)
                            result.append(context.id)
                            
                    self.response_dbs.database.commit(tenantid)
                    self.context_dbs.database.commit(tenantid)
                    jsons = {"resource_ids": result}
                
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/context/<context_id>'), methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
        @auth.login_required
        def context_operations(context_id):
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, PUT, DELETE, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                context = self.context_dbs.retrieve_context(context_id, tenantid)
                if (not context):
                    return make_response(CHATBOT_CONTEXT_NOT_FOUND, 400)
                
                if (request.method == 'GET'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    jsons = ContextSerializer(context).data
                elif (request.method == 'PUT'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, PUT_CONTEXT_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    context.name = content['name']
                    dbresult = self.context_dbs.update_context(context, tenantid)
                    jsons = {"resource_id": dbresult}
                elif (request.method == 'DELETE'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    responses = self.response_dbs.retrieve_responses(context.id, tenantid)
                    for response in responses:
                        self.response_dbs.delete_response(response, tenantid)
                    dbresult = self.context_dbs.delete_context(context, tenantid)
                    jsons = {"resource_id": dbresult}
                    
                return make_response(jsonify(jsons), 200)
                