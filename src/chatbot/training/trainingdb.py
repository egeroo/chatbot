'''
Created on Mar 19, 2018

@author: Muhammad Ridwan
'''
from database import Database
from chatbot.record.recorddb import RecordDBService
from chatbot.category.context.contextdb import ContextDBService
from chatbot.category.context.intent.intentdb import IntentDBService
from chatbot.training import Training
from chatbot.category.categorydb import CategoryDBService

class TrainingDBService:
    database = None
    record_dbs = None
    category_dbs = None
    context_dbs = None
    intent_dbs = None

    def __init__(self, database, record_dbs, category_dbs, context_dbs, intent_dbs):
        self.database = database
        self.record_dbs = record_dbs
        self.category_dbs = category_dbs
        self.context_dbs = context_dbs
        self.intent_dbs = intent_dbs
    
    def save_training(self, training, tenantid, commit=True):
        context_id = 'null'
        intent_id = 'null'
        if(training.context):
            context_id = str(training.context.id)
        if(training.intent):
            intent_id = str(training.intent.id)
        
        query = ("insert into tr_lib_training(recordid, contextid, intentid) values ("+
                 str(training.record.id)+", "+context_id+", "+intent_id+")")
        
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(id) from tr_lib_training where recordid = "+str(training.record.id))['max']
    
    def update_training(self, training, tenantid, commit=True):
        context_id = 'null'
        intent_id = 'null'
        if(training.context):
            context_id = str(training.context.id)
        if(training.intent):
            intent_id = str(training.intent.id)
        query = ("update tr_lib_training set recordid = "+str(training.record.id)+", contextid = "+context_id+
                 ", intentid = "+intent_id+" where id = "+str(training.id))
        
        self.database.execute(tenantid, query, commit=commit)
        return training.id
    
    def delete_training(self, training, tenantid, commit=True):
        query = ("delete from tr_lib_training where id = "+str(training.id))
        self.database.execute(tenantid, query, commit=commit)
        return training.id
    
    def retrieve_trainings(self, start_time, end_time, limit, offset, tenantid):
        query = ("select t.id as id, t.recordid as recordid, t.contextid as contextid, "+
                 "t.intentid as intentid from tr_lib_training as t "+
                 "left join tr_lib_record as r on r.id=t.recordid ")
        condition = None
        if (start_time):
            condition = "where r.recordtime >= '"+str(start_time)+"' "
        if (end_time):
            if(condition):
                condition += "and "
            else:
                condition = "where "
            condition += "r.recordtime <= '"+str(end_time)+"' "
        
        if(condition):
            query += condition
        if (limit):
            query += " order by r.id asc limit "+str(limit)
        if (offset):
            query += " offset "+str(offset)
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            record = self.record_dbs.retrieve_record(row['recordid'], tenantid)
            category = None
            context = None
            intent = None
            if(row['contextid']):
                context = self.context_dbs.retrieve_context(row['contextid'], tenantid)
            if(context):
                category = self.category_dbs.retrieve_category(context.category_id, tenantid)
            if(row['intentid']):
                intent = self.intent_dbs.retrieve_intent(row['intentid'], tenantid)
            training = Training(record, category, context, intent, id=row['id'])
            result.append(training)
        return result
    
    def retrieve_training(self, id, tenantid):
        query = ("select t.id as id, t.recordid as recordid, t.contextid as contextid, "+
                 "t.intentid as intentid from tr_lib_training as t "+
                 "where t.id = "+str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        training = None
        if(fetch_result):
            record = self.record_dbs.retrieve_record(fetch_result['recordid'], tenantid)
            category = None
            context = None
            intent = None
            if(fetch_result['contextid'] != None):
                context = self.context_dbs.retrieve_context(fetch_result['contextid'], tenantid)
            if(context):
                category = self.category_dbs.retrieve_category(context.category_id, tenantid)
            if(fetch_result['intentid'] != None):
                intent = self.intent_dbs.retrieve_intent(fetch_result['intentid'], tenantid)
            training = Training(record, category, context, intent, id=fetch_result['id'])
        return training
    
    def retrieve_training_categorized_ids(self, tenantid):
        query = ("select t.id as id from tr_lib_training as t "+
                 "left join ms_lib_context as c on c.id = t.contextid "+
                 "where t.contextid is not null and c.contextid != 0")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            result.append(row['id'])
        
        return result
                  