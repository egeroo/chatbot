'''
Created on Mar 16, 2018

@author: M
'''

from database import Database
from chatbot.category.context.intent import Intent

class IntentDBService:
    database = None

    def __init__(self, database):
        self.database = database
    
    def save_intent(self, intent, tenantid, commit=True):
        intent_id = self.database.execute(tenantid, "select max(intentid) from ms_lib_context where contextid = "+str(intent.context_id))['max'] + 1
        query = ("insert into ms_lib_intent(intentid, name, contextid) "+
                 "values ("+intent_id+",'"+str(intent.name)+"', "+
                 str(intent.context_id)+")")
        self.database.execute(tenantid, query, commit=commit)
    
    def update_intent(self, intent, tenantid, commit=True):
        query = ("update ms_lib_intent set name = '"+str(intent.name)+
                 "' where id = "+str(intent.id))
        self.database.execute(tenantid, query, commit=commit)
    
    def delete_intent(self, intent, tenantid, commit=True):
        query = ("delete from ms_lib_intent where id = "+str(intent.id))
        self.database.execute(tenantid, query, commit=commit)
    
    def retrieve_intents(self, context_id, tenantid):
        query = ("select i.id as id, i.intentid as intentid, i.name as name, i.contextid as contextid "+
                 "from ms_lib_intent as i where i.contextid = "+str(context_id)+
                 " order by i.id asc")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            intent = Intent(row['name'], row['contextid'], intent_id=row['intentid'], id=row['id'])
            result.append(intent)
        return result

    def retrieve_intent(self, id, tenantid):
        query = ("select i.id as id, i.intentid as intentid, i.name as name, i.contextid as contextid "+
                 "from ms_lib_intent as i where i.id = " + str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        intent = None
        if(fetch_result):
            intent = Intent(fetch_result['name'], fetch_result['contextid'], intent_id=fetch_result['intentid'], id=fetch_result['id'])
        
        return intent

    def retrieve_intent_by_intentid(self, intent_id, tenantid):
        query = ("select i.id as id, i.intentid as intentid, i.name as name, i.contextid as contextid "+
                 "from ms_lib_intent as i where i.intentid = " + str(intent_id))
        fetch_result = self.database.fetch_one(tenantid, query)
        intent = None
        if(fetch_result):
            intent = Intent(fetch_result['name'], fetch_result['contextid'], intent_id=fetch_result['intentid'], id=fetch_result['id'])
        
        return intent