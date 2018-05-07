'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''

from database import Database
from chatbot.category import Category

class CategoryDBService:
    database = None


    def __init__(self, database):
        self.database = database
    
    def save_category(self, category, tenantid, commit=True):
        category_id = self.database.fetch_one(tenantid, "select max(categoryid) from ms_lib_category")['max'] + 1
        query = ("insert into ms_lib_category(categoryid, name) " +
                 "values ("+str(category_id)+",'"+str(category.name)+"')")
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(categoryid) from ms_lib_category")['max']
    
    def update_category(self, category, tenantid, commit=True):
        query = ("update ms_lib_category set name = '"+str(category.name)+
                 "' where id = "+str(category.id))
        self.database.execute(tenantid, query, commit=commit)
        return category.id
    
    def delete_category(self, category, tenantid, commit=True):
        query = ("delete from ms_lib_category where id = "+str(category.id))
        self.database.execute(tenantid, query, commit=commit)
        return category.id
    
    def get_visible_categories(self, tenantid):
        query = ("select c.id as id, c.categoryid as categoryid, c.name as name from ms_lib_category as c "+
                 "where c.id not in (0, 1) order by c.id asc")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            category = Category(row['name'], category_id= row['categoryid'], id=row['id'])
            result.append(category)
        return result
    
    def retrieve_categories(self, tenantid):
        query = ("select c.id as id, c.categoryid as categoryid, c.name as name from ms_lib_category as c "+
                 "order by c.id asc")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            category = Category(row['name'], category_id= row['categoryid'], id=row['id'])
            result.append(category)
        return result
    
    def retrieve_category(self, id, tenantid):
        query = ("select c.id as id, c.categoryid as categoryid, c.name as name from ms_lib_category as c "+
                 "where c.id = "+str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        category = None
        if(fetch_result):
            category = Category(fetch_result['name'], category_id= fetch_result['categoryid'], id=fetch_result['id'])
        
        return category
    
    def retrieve_category_by_categoryid(self, category_id, tenantid):
        query = ("select c.id as id, c.categoryid as categoryid, c.name as name from ms_lib_category as c "+
                 "where c.categoryid = "+str(category_id))
        fetch_result = self.database.fetch_one(tenantid, query)
        category = None
        if(fetch_result):
            category = Category(fetch_result['name'], category_id= fetch_result['categoryid'], id=fetch_result['id'])
        
        return category
    
    def max_categoryid(self, tenantid):
        return self.database.fetch_one(tenantid, "select max(categoryid) from ms_lib_category")['max']
    