'''
Created on Mar 19, 2018

@author: Muhammad Ridwan
'''

from chatbot.response import Response

class ResponseDBService:
    database = None

    def __init__(self, database):
        self.database = database
    
    def save_response(self, response, tenantid, commit=True):
        query = ("insert into tr_lib_response(sentence, contextid, intentid) values('"+
                 response.sentence+"', "+str(response.context_id)+", ")
        if (response.intent_id):
            query += str(response.intent_id)
        else:
            query += "null"
        query += ")"
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(id) from tr_lib_response where sentence = '"+str(response.sentence)+"' and contextid = "+str(response.context_id))['max']
    
    def update_response(self, response, tenantid, commit=True):
        query = ("update tr_lib_reponse set sentence = '"+response.sentence +
                 "', contextid = "+str(response.contextid))
        if (response.intent_id):
            query += ", intentid = "+str(response.intent_id)
        
        query += " where id = "+str(response.id)
        self.database.execute(tenantid, query, commit=commit)
        return response.id
    
    def delete_response(self, response, tenantid, commit=True):
        query = ("delete from tr_lib_response where id = "+str(response.id))
        self.database.execute(tenantid, query, commit=commit)
        return response.id
    
    def retrieve_responses(self, context_id, tenantid):
        query = ("select r.id as id, r.sentence as sentence, r.contextid as contextid, r.intentid as intentid "+
                 "from tr_lib_response as r where r.contextid = "+str(context_id)+
                 " order by r.id asc")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            response = Response(row['sentence'], row['contextid'], intent_id=row['intentid'], id=row['id'])
            result.append(response)
        return result
    
    def retrieve_response(self, id, tenantid):
        query = ("select r.id as id, r.sentence as sentence, r.contextid as contextid, r.intentid as intentid "+
                 "from tr_lib_response as r where r.id = "+str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        response = None
        if (fetch_result):
            response = Response(fetch_result['sentence'], fetch_result['contextid'], intent_id=fetch_result['intentid'], id=fetch_result['id'])
        
        return response
            