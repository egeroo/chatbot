'''
Created on Apr 24, 2018

@author: Muhammad Ridwan
'''

#Headers
API_HEADERS = ["tenant-id"]

class APIValidator:
    
    def check_header(self, headers):
        missing = False
        missing_headers = None
        for header in API_HEADERS:
            if not (header in headers):
                if(missing):
                    missing_headers += ", " + header
                else:
                    missing_headers = header
                    missing = True
        
        return missing, missing_headers
    
    def check_param(self, json_request, param, list_element=False):
        if not (type(json_request) is dict):
            return False, ("Need key for value: "+str(json_request))
        if (param.mandatory):
            if not (param.name in json_request):
                return False, ("Missing parameter: "+param.name)
            
        if(param.name in json_request):
            if (param.islist and not list_element):
                    if not (type(json_request[param.name]) is list):
                        return False, ("Expected list: "+param.name)
                    else:
                        valid = True
                        errors = ""
                        for p in json_request[param.name]:
                            v, e = self.check_param({param.name: p}, param, list_element=True)
                            valid = v and valid
                            errors += e
                        
                        if not valid:
                            return valid, errors
            
            elif (param.isclass):
                valid = True
                errors = ""
                for p in param.type:
                    v, e = self.check_param(json_request[param.name], p)
                    valid = v and valid
                    errors += e
                
                if not valid:
                    return valid, errors
            else:
                if not (type(json_request[param.name]) is param.type):
                    return False, ("Expected type of "+str(param.type)+" for parameter "+param.name)
                    
        
        return True, ""
    
    def check_request(self, request, params):
        missing, headers = self.check_header(request.headers)
        if(missing):
            return False, ("Missing header: "+headers)
        
        errors = None
        error = False
        if (params):
            for param in params:
                valid, response = self.check_param(request.json, param)
                if(not valid):
                    if (error):
                        errors += "\n" + response
                    else:
                        errors = response
                        error = True
        
        return (not error), errors
                    