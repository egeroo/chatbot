'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''

from database import Database
from chatbot.category.context import Context

class ContextDBService:
    database = None

    def __init__(self, database):
        self.database = database
    
    def save_context(self, context, tenantid, commit=True):
        context_id = self.database.fetch_one(tenantid, "select max(contextid) from ms_lib_context where categoryid = "+str(context.category_id))['max'] + 1
        query = ("insert into ms_lib_context(contextid, name, categoryid) " +
                 "values ("+str(context_id)+",'"+str(context.name)+"', " +
                 str(context.category_id) + ")")
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(id) from ms_lib_context where name = '"+context.name+"' and categoryid = "+str(context.category_id))['max']
    
    def update_context(self, context, tenantid, commit=True):
        query = ("update ms_lib_context set name = '" + str(context.name)+
                 "' where id = "+str(context.id))
        self.database.execute(tenantid, query, commit=commit)
        return context.id
    
    def delete_context(self, context, tenantid, commit=True):
        query = ("delete from ms_lib_context where id = "+str(context.id))
        self.database.execute(tenantid, query, commit=commit)
        return context.id
    
    def retrieve_contexts(self, category_id, tenantid):
        query = ("select c.id as id, c.contextid as contextid, c.name as name, c.categoryid as categoryid "+
                 "from ms_lib_context as c where c.categoryid = "+str(category_id)+
                 " order by c.id asc")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            context = Context(row['name'], row['categoryid'], context_id=row['contextid'], id=row['id'])
            result.append(context)
        return result
    
    def retrieve_context(self, id, tenantid):
        query = ("select c.id as id, c.contextid as contextid, c.name as name, c.categoryid as categoryid "+
                 "from ms_lib_context as c where c.id = " + str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        context = None
        if(fetch_result):
            context = Context(fetch_result['name'], fetch_result['categoryid'], context_id=fetch_result['contextid'], id=fetch_result['id'])
        
        return context
    
    def retrieve_context_by_categorycontextid(self, category_id, context_id, tenantid):
        query = ("select c.id as id, c.contextid as contextid, c.name as name, c.categoryid as categoryid "+
                 "from ms_lib_context as c "+
                 "left join ms_lib_category as ct on ct.id = c.categoryid "
                 "where c.contextid = " + str(context_id)+" and ct.categoryid = "+str(category_id))
        fetch_result = self.database.fetch_one(tenantid, query)
        context = None
        if(fetch_result):
            context = Context(fetch_result['name'], fetch_result['categoryid'], context_id=fetch_result['contextid'], id=fetch_result['id'])
        
        return context
    
    def max_contextid(self, tenantid):
        return self.database.fetch_one(tenantid, "select max(contextid) from ms_lib_context")['max']
    
    