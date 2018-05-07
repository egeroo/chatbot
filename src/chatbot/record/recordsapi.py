'''
Created on Apr 25, 2018

@author: ridwan
'''
from flask import jsonify
from flask.globals import request
from chatbot.record import Record
from validator import APIValidator
from chatbot.category import UNCATEGORIZED, CategoryLibrarySerializer
from chatbot.training import Training, TrainingSerializer
from datetime import datetime, timedelta
from chatbot.response import Response
from flask.helpers import make_response
from validator.paramtype import ParamType
from exception.exception import *
from auth.user import *
from flask import jsonify, g

POST_RECORD_PARAM = [ParamType("sentence", str, False, True, False),
                     ParamType("category", int, False, True, False),
                     ParamType("context", int, False, True, False)]
PUT_RECORD_PARAM = [ParamType("id", int, False, True, False),
                     ParamType("category", int, False, False, False),
                     ParamType("context", int, False, False, False)]
POST_RECORDS_PARAM = [ParamType("records", POST_RECORD_PARAM, True, True, True)]
PUT_RECORDS_PARAM = [ParamType("records", PUT_RECORD_PARAM, True, True, True)]

class RecordsAPIService:
    app = None
    root = None
    auth_api = None
    api_validator = None
    category_dbs = None
    context_dbs = None
    record_dbs = None
    training_dbs = None

    def __init__(self, category_dbs, context_dbs, record_dbs, training_dbs, auth_api, app, root):
        self.app = app
        self.root = root
        self.auth_api = auth_api
        self.api_validator = APIValidator()
        self.category_dbs = category_dbs
        self.context_dbs = context_dbs
        self.record_dbs = record_dbs
        self.training_dbs = training_dbs
    
        self.build_api()
    
    def get_route(self, route):
        return (self.root + route)
    
    def build_api(self):
        app = self.app
        auth = self.auth_api.auth
        
        @app.route(self.get_route('/record'), methods=['GET', 'POST', 'PUT', 'OPTIONS'])
        @auth.login_required
        def handle_record():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
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
                    valid, error = self.api_validator.check_request(request,POST_RECORD_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    category = self.category_dbs.retrieve_category_by_categoryid(content['category'], tenantid)
                    if not category:
                        return make_response(CHATBOT_CATEGORY_NOT_FOUND, 400)
                    
                    context = self.context_dbs.retrieve_context_by_categorycontextid(content['category'], content['context'], tenantid)
                    if not context:
                        return make_response(CHATBOT_CONTEXT_NOT_FOUND, 400)
                    
                    record = Record(content['sentence'], category, context, None)
                    record_id = self.record_dbs.save_record(record, tenantid, commit=False)
                    record.id = record_id
                    
                    training_category = UNCATEGORIZED
                    training_context = self.context_dbs.retrieve_context_by_categorycontextid(training_category.category_id, 0, tenantid)
                    training = Training(record, training_category, training_context, None)
                
                    dbresult = self.training_dbs.save_training(training, tenantid, commit=False)
                    
                    self.record_dbs.database.commit(tenantid)
                    self.training_dbs.database.commit(tenantid)
                    jsons = {"resource_id": dbresult}
                    
                elif (request.method == 'PUT'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request,PUT_RECORD_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    training = self.training_dbs.retrieve_training(content['id'], tenantid)
                    if ((not ('context' in content) or content['context'] < 1) and (not ('category' in content) or content['category'] < 1)):
                        training.context = self.context_dbs.retrieve_context_by_categorycontextid(0, 0, tenantid)
                    else:
                        training.context = self.context_dbs.retrieve_context_by_categorycontextid(content['category'], content['context'], tenantid)
                        if (not training.context):
                            training.context = self.context_dbs.retrieve_context_by_categorycontextid(0, 0, tenantid)
                    dbresult = self.training_dbs.update_training(training, tenantid)
                    jsons = {"resource_id": dbresult}
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/records'), methods=['GET', 'POST', 'PUT', 'OPTIONS'])
        @auth.login_required
        def handle_records():
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
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
                    start_time = request.args.get('from')
                    if (start_time):
                        start_time = datetime.strptime(start_time, '%d-%m-%Y')
                    end_time = request.args.get('to')
                    if (end_time):
                        end_time = datetime.strptime(end_time, '%d-%m-%Y') + timedelta(days=1)
                    limit = request.args.get('limit')
                    offset = request.args.get('offset')
                    trainings = self.training_dbs.retrieve_trainings(start_time, end_time, limit, offset, tenantid)
                    jsons = TrainingSerializer(trainings, many=True).data
                elif (request.method == 'POST'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request,POST_RECORDS_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    contents = request.json['records']
                    result = []
                    for content in contents:
                        category = self.category_dbs.retrieve_category_by_categoryid(content['category'], tenantid)
                        if not category:
                            return make_response(CHATBOT_CATEGORY_NOT_FOUND, 400)
                        
                        context = self.context_dbs.retrieve_context_by_categorycontextid(content['category'], content['context'], tenantid)
                        if not context:
                            return make_response(CHATBOT_CONTEXT_NOT_FOUND, 400)
                        
                        record = Record(content['sentence'], category, context, None)
                        record_id = self.record_dbs.save_record(record, tenantid, commit=False)
                        record.id = record_id
                        
                        training_category = UNCATEGORIZED
                        training_context = self.context_dbs.retrieve_context_by_categorycontextid(training_category.category_id, 0, tenantid)
                        training = Training(record, training_category, training_context, None)
                    
                        dbresult = self.training_dbs.save_training(training, tenantid, commit=False)
                        
                        result.append(dbresult)
                        
                    self.record_dbs.database.commit(tenantid)
                    self.training_dbs.database.commit(tenantid)
                    jsons = {"resource_ids": dbresult}
                elif (request.method == 'PUT'):
                    if not self.auth_api.permitted(g.user.id, [ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request,PUT_RECORDS_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    contents = request.json['records']
                    result = []
                    for content in contents:
                        training = self.training_dbs.retrieve_training(content['id'], tenantid)
                        if ((not ('context' in content) or content['context'] < 1) and (not ('category' in content) or content['category'] < 1)):
                            training.context = self.context_dbs.retrieve_context_by_categorycontextid(0, 0, tenantid)
                        else:
                            training.context = self.context_dbs.retrieve_context_by_categorycontextid(content['category'], content['context'], tenantid)
                            if (not training.context):
                                training.context = self.context_dbs.retrieve_context_by_categorycontextid(0, 0, tenantid)
                        dbresult = self.training_dbs.update_training(training, tenantid, commit=False)
                        result.append(dbresult)
                    
                    self.record_dbs.database.commit(tenantid)
                    self.training_dbs.database.commit(tenantid)
                    jsons = {"resource_ids": result}
                    
                return make_response(jsonify(jsons), 200)
        