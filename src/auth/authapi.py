'''
Created on Apr 24, 2018

@author: Muhammad Ridwan
'''
from flask.globals import request
from flask_httpauth import HTTPBasicAuth
from validator import APIValidator
from flask.helpers import make_response
from validator.paramtype import ParamType
from exception.exception import *
from auth.user import *
from flask import jsonify, g
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

POST_USER_PARAM = [ParamType("username", str, False, True, False),
                   ParamType("password", str, False, True, False),
                   ParamType("is_admin", bool, False, False, False)]
PUT_CHANGEPASSWORD_PARAM = [ParamType("old_password", str, False, True, False),
                            ParamType("new_password", str, False, True, False),
                            ParamType("confirmation_new_password", str, False, True, False)]
PUT_CHANGEROLE_PARAM = [ParamType("user_id", int, False, True, False),
                            ParamType("is_admin", bool, False, True, False)]

class AuthAPIService:
    app = None
    root = None
    auth = None
    api_validator = None
    user_dbs = None


    def __init__(self, user_dbs, app, root):
        self.app = app
        self.root = root
        self.api_validator = APIValidator()
        self.user_dbs = user_dbs
        self.auth = HTTPBasicAuth()
        
        self.build_api()
    
    def get_route(self, route):
        return (self.root + route)
    
    def permitted(self, userid, permitted_roles, tenantid):
        roles = self.user_dbs.retrieve_userroles(userid, tenantid)
        for role in permitted_roles:
            r = list(filter(lambda x: x.id == role.id, roles))
            if (len(r) > 0):
                return True
        return False
    
    def build_api(self):
        app = self.app
        auth = self.auth
        
        @auth.verify_password
        def verify_password(username_or_token, password):
            valid, error = self.api_validator.check_request(request, None)
            if not valid:
                return make_response(error, 400)
            
            tenantid = request.headers['tenant-id']
            user = verify_auth_token(username_or_token, tenantid)
            if not user:
                user = self.user_dbs.retrieve_user_by_username(username_or_token, tenantid)
                if not user or not user.verify_password(password):
                    return False
            g.user = user
            return True
    
        def generate_auth_token(user, expiration = 600):
            s = Serializer(self.app.config['SECRET_KEY'], expires_in = expiration)
            return s.dumps({ 'id': user.id })

        def verify_auth_token(token, tenantid):
            s = Serializer(app.config['SECRET_KEY'])
            try:
                data = s.loads(token)
            except SignatureExpired:
                return None # valid token, but expired
            except BadSignature:
                return None # invalid token
            user = self.user_dbs.retrieve_user(data['id'], tenantid)
            return user
        
        @app.route(self.get_route('/token'))
        @auth.login_required
        def get_auth_token():
            token = generate_auth_token(g.user)
            return jsonify({ 'token': token.decode('ascii') })
        
        @app.route(self.get_route('/user'), methods = ['GET', 'POST', 'OPTIONS'])
        @auth.login_required
        def new_user():
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
                    if not self.permitted(g.user.id, [SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, POST_USER_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    username = request.json.get('username')
                    password = request.json.get('password')
                    user = self.user_dbs.retrieve_user_by_username(username, tenantid)
                    if user:
                        return make_response(AUTH_EXISTING_USER, 400)
                    roles = [USER]
                    if ('is_admin' in request.json) and request.json['is_admin']:
                        roles.append(ADMIN)
                    user = User(username, None, roles)
                    user.hash_password(password)
                    
                    dbresult = self.user_dbs.save_user(user, tenantid)
                    
                    jsons = {"resource_id": dbresult}
                    
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/changepassword'), methods = ['GET', 'PUT', 'OPTIONS'])
        @auth.login_required
        def change_password():
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
                if (request.method == "PUT"):
                    if not self.permitted(g.user.id, [USER, ADMIN, SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, PUT_CHANGEPASSWORD_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    user = User(g.user.username, g.user.hashed_password, g.user.roles, id=g.user.id)
                    if not user.verify_password(content['old_password']):
                        return make_response(AUTH_WRONG_PASSWORD, 400)
                    
                    if content['new_password'] != content['confirmation_new_password']:
                        return make_response(PASS_UNMATCHED, 400)
                    
                    user.hash_password(content['new_password'])
                    dbresult = self.user_dbs.update_user(user, tenantid)
                    
                    jsons = {"resource_id": dbresult}
                
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/changerole'), methods = ['GET', 'PUT', 'OPTIONS'])
        @auth.login_required
        def change_role():
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
                if (request.method == "PUT"):
                    if not self.permitted(g.user.id, [SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    valid, error = self.api_validator.check_request(request, PUT_CHANGEROLE_PARAM)
                    if not valid:
                        return make_response(error, 400)
                    
                    content = request.json
                    user = self.user_dbs.retrieve_user(content['user_id'], tenantid)
                    if not user:
                        return make_response(USER_NOT_FOUND, 400)
                        
                    if (user.is_admin() != content['is_admin']):
                        if (user.is_admin()):
                            user.remove_role(ADMIN)
                        else:
                            user.add_role(ADMIN)
                    
                    dbresult = self.user_dbs.update_user(user, tenantid)
                    
                    jsons = {"resource_id": dbresult}
                
                return make_response(jsonify(jsons), 200)
        
        @app.route(self.get_route('/user/<userid>'), methods = ['GET', 'DELETE', 'OPTIONS'])
        @auth.login_required
        def user_operations(userid):
            if (request.method == "OPTIONS"):
                resp = make_response("OK", 200)
                resp.headers["Access-Control-Allow-Origin"] = '*'
                resp.headers["Access-Control-Allow-Methods"] = "GET, DELETE, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "accept, content-type"
                resp.headers["Access-Control-Max-Age"] = "1728000"
                return resp
            else:
                valid, error = self.api_validator.check_request(request, None)
                if not valid:
                    return make_response(error, 400)
                
                tenantid = request.headers['tenant-id']
                if (request.method == "DELETE"):
                    if not self.permitted(g.user.id, [SUPERADMIN], tenantid):
                        return make_response(AUTH_INVALID_PERMISSION, 400)
                    
                    user = self.user_dbs.retrieve_user(userid, tenantid)
                    if not user:
                        return make_response(USER_NOT_FOUND, 400)
                    
                    if user.is_superadmin():
                        return make_response(USER_IS_SUPERADMIN, 400)
                    
                    dbresult = self.user_dbs.delete_user(user, tenantid)
                    
                    jsons = {"resource_id": dbresult}
                    
                return make_response(jsonify(jsons), 200)
            