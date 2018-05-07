'''
Created on Mar 19, 2018

@author: ridwan
'''
from flask import jsonify
from chatbot.response.responsedb import ResponseDBService
from exception import ApiError
from flask.globals import request
from chatbot.category.categorydb import CategoryDBService
from chatbot.category.context.contextdb import ContextDBService
from chatbot.response import Response, ResponseSerializer
from validator import APIValidator
from validator.paramtype import ParamType
from flask.helpers import make_response
from exception.exception import *
from auth.user import *
from flask import jsonify, g

POST_RESPONSE_PARAM = [ParamType("sentence", str, False, True, False),
                       ParamType("category", int, False, True, False),
                       ParamType("context", int, False, True, False)]
POST_LIST_RESPONSE_PARAM = [ParamType(POST_RESPONSE_PARAM, str, True, True, True)]
PUT_RESPONSE_PARAM = [ParamType("sentence", str, False, True, False)]

class ResponsesAPIService:
    app = None
    root = None
    auth_api = None
    api_validator = None
    response_dbs = None
    category_dbs = None
    context_dbs = None


    def __init__(self, response_dbs, category_dbs, context_dbs, auth_api, app, root):
        self.app = app
        self.root = root
        self.auth_api = auth_api
        self.api_validator = APIValidator()
        self.response_dbs = response_dbs
        self.category_dbs = category_dbs
        self.context_dbs = context_dbs
        
        self.build_api()
    
    def get_route(self, route):
        return (self.root + route)
    
    def build_api(self):
        app = self.app
        auth = self.auth_api.auth
    
        @app.route(self.get_route('/response'), methods=['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def save_response():
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
                    valid, error = self.api_validator.check_request(request, POST_RESPONSE_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    
                    context = self.context_dbs.retrieve_context_by_categorycontextid(content['category'], content['context'], tenantid)
                    if (not context):
                        return make_response(CHATBOT_CONTEXT_NOT_FOUND, 400)
                    
                    sentence = content['sentence']
                    response = Response(sentence, context.id)
                    
                    dbresult = self.response_dbs.save_response(response, tenantid)
                    jsons = {"resource_id":dbresult}
                    
                return make_response(jsonify(jsons), 200)
    
        @app.route(self.get_route('/responses'), methods=['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def save_responses():
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
                    valid, error = self.api_validator.check_request(request, POST_LIST_RESPONSE_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    json_list = request.json
                    
                    result = []
                    for content in json_list:
                        context = self.context_dbs.retrieve_context_by_categorycontextid(content['category'], content['context'], tenantid)
                        if (not context):
                            return make_response(CHATBOT_CONTEXT_NOT_FOUND, 400)
                        
                        sentence = content['sentence']
                        response = Response(sentence, context.id)
                        
                        dbresult = self.response_dbs.save_response(response, tenantid, commit=False)
                        result.append(dbresult)
                    
                    self.response.dbs.database.commit(tenantid)
                    jsons = {"resource_ids":dbresult}
                    
                return make_response(jsonify(jsons), 200)
    
        @app.route(self.get_route('/response/<response_id>'), methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
        @auth.login_required
        def response_operations(response_id):
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
                response = self.response_dbs.retrieve_response(response_id, tenantid)
                
                if (not response):
                    return make_response(CHATBOT_RESPONSE_NOT_FOUND, 400)
                
                if (request.method == 'GET'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    jsons = ResponseSerializer(response).data
                elif (request.method == 'PUT'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, PUT_RESPONSE_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    response.sentence = content['sentence']
                    dbresult = self.response_dbs.update_response(response, tenantid)
                    jsons = {"resource_id": dbresult}
                elif (request.method == 'DELETE'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    dbresult = self.response_dbs.delete_response(response, tenantid)
                    jsons = {"resource_id": dbresult}
                    
                return make_response(jsonify(jsons), 200)
        
        
            
            
        