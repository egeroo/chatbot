'''
Created on Mar 19, 2018

@author: ridwan
'''
from database import Database
from chatbot.record import Record
from chatbot.category.categorydb import CategoryDBService
from chatbot.category.context.contextdb import ContextDBService
from chatbot.category.context.intent.intentdb import IntentDBService

class RecordDBService:
    database = None
    category_dbs = None
    context_dbs = None
    intent_dbs = None

    def __init__(self, database, category_dbs, context_dbs, intent_dbs):
        self.database = database
        self.category_dbs = category_dbs
        self.context_dbs = context_dbs
        self.intent_dbs = intent_dbs
        
    def save_record(self, record, tenantid, commit=True):
        query = ("insert into tr_lib_record(sentence, contextid, intentid, recordtime) values('"+
                 record.sentence+"', "+str(record.context.id)+", ")
        if(record.intent):
            query += str(record.intent.id)
        else:
            query += "null"
        query += ", '"+str(record.record_time)+"')"
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(id) from tr_lib_record where sentence = '"+record.sentence+"' and recordtime = '"+str(record.record_time)+"'")['max']
    
    def delete_record(self, record, tenantid, commit=True):
        query = ("delete from tr_lib_record where id ="+str(record.id))
        self.database.execute(tenantid, query, commit=commit)
        return record.id
    
    def retrieve_records(self, start_time, end_time, limit, offset, tenantid):
        query = ("select r.id as id, r.sentence as sentence r.contextid as contextid, r.intentid as intentid, r.recordtime as recordtime "+
                 "from tr_lib_record as r ")
        condition = None
        if (start_time):
            condition = "where r.recordtime >= '"+str(start_time)+"' "
        if (end_time):
            if(condition):
                condition += "and "
            else:
                condition = "where "
            condition += "r.recordtime <= '"+str(end_time)+"' "
        
        query += condition+"order by r.id asc limit "+str(limit)+" offset "+str(offset)
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            category = None
            context = None
            intent = None
            if(row['contextid']):
                context = self.context_dbs.retrieve_context(row['contextid'], tenantid)
            if(context and context.category_id):
                category = self.category_dbs.retrieve_category(context.category_id, tenantid)
            if(row['intentid']):
                intent = self.intent_dbs.retrieve_intent(row['intentid'], tenantid)
            record = Record(row['sentence'], category, context, intent, record_time=row['recordtime'], id=row['id'])
            result.append(record)
        return result
    
    def retrieve_record(self, id, tenantid):
        query = ("select r.id as id, r.sentence as sentence, r.contextid as contextid, r.intentid as intentid, r.recordtime as recordtime "+
                 "from tr_lib_record as r where r.id = "+str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        record = None
        if(fetch_result):
            category = None
            context = None
            intent = None
            if(fetch_result['contextid'] != None):
                context = self.context_dbs.retrieve_context(fetch_result['contextid'], tenantid)
            if(context and context.category_id != None):
                category = self.category_dbs.retrieve_category(context.category_id, tenantid)
            if(fetch_result['intentid'] != None):
                intent = self.intent_dbs.retrieve_intent(fetch_result['intentid'], tenantid)
            record = Record(fetch_result['sentence'], category, context, intent, record_time=fetch_result['recordtime'], id=fetch_result['id'])
        
        return record
            