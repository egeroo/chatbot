'''
Created on Apr 25, 2018

@author: Muhammad Ridwan
'''
from database import Database
from auth.user import *

class UserDBService:
    database = None


    def __init__(self, database):
        self.database = database
    
    def save_user(self, user, tenantid, commit=True):
        query = ("insert into tr_tnt_user(username, password_hash) values('"+
                 str(user.username)+"', '"+str(user.hashed_password)+"')")
        self.database.execute(tenantid, query, commit=False)
        user.id = self.database.fetch_one(tenantid, "select min(id) from tr_tnt_user where username = '"+str(user.username)+"'")['min']
        for role in user.roles:
            self.save_userrole(role, user.id, tenantid, commit=False)
        
        if(commit):
            self.database.commit(tenantid)
        return user.id
    
    def update_user(self, user, tenantid, commit=True):
        query = ("update tr_tnt_user set password_hash = '"+str(user.hashed_password)+"' where id = "+str(user.id))
        self.database.execute(tenantid, query, commit=False)
        
        saved_roles = self.retrieve_userroles(user.id, tenantid)
        for role in saved_roles:
            existing_role = list(filter(lambda x: x.id == role.id, user.roles))
            if not existing_role:
                self.delete_userrole(role, user.id, tenantid, commit=False)
        
        for role in user.roles:
            existing_role = list(filter(lambda x: x.id == role.id, saved_roles))
            if not existing_role:
                self.save_userrole(role, user.id, tenantid, commit=False)
        
        if(commit):
            self.database.commit(tenantid)
        return user.id
    
    def delete_user(self, user, tenantid, commit=True):
        query = ("delete from tr_tnt_user where id = "+str(user.id))
        self.database.execute(tenantid, query, commit=False)
        
        roles = self.retrieve_userroles(user.id, tenantid)
        for role in roles:
            self.delete_userrole(role, user.id, tenantid, commit=False)
            
        if(commit):
            self.database.commit(tenantid)
        return user.id
    
    def retrieve_user(self, id, tenantid):
        query = ("select u.id as id, u.username as username, u.password_hash as hashed_password "+
                 "from tr_tnt_user as u where u.id = "+str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        user = None
        if (fetch_result):
            user = User(fetch_result['username'], fetch_result['hashed_password'], self.retrieve_userroles(fetch_result['id'], tenantid), id=fetch_result['id'])
            
        
        return user
    
    def retrieve_user_by_username(self, username, tenantid):
        query = ("select u.id as id, u.username as username, u.password_hash as hashed_password "+
                 "from tr_tnt_user as u where u.username = '"+str(username)+"'")
        fetch_result = self.database.fetch_one(tenantid, query)
        user = None
        if (fetch_result):
            user = User(fetch_result['username'], fetch_result['hashed_password'], self.retrieve_userroles(fetch_result['id'], tenantid), id=fetch_result['id'])
        
        return user
    
    def retrieve_users(self, tenantid):
        query = ("select u.id as id, u.username as username, u.password_hash as hashed_password "+
                 "from tr_tnt_user as u")
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            user = User(row['username'], row['hashed_password'], self.retrieve_userroles(fetch_result['id'], tenantid), id=row['id'])
            result.append(user)
        
        return result
    
    def save_userrole(self, role, userid, tenantid, commit=True):
        query = ("insert into tr_tnt_userrole(userid, roleid) values("+
                 str(userid)+", "+str(role.id)+")")
        self.database.execute(tenantid, query, commit=commit)
        return userid, role.id
    
    def delete_userrole(self, role, userid, tenantid, commit=True):
        query = ("delete from tr_tnt_userrole where userid = "+str(userid)+" and roleid = "+str(role.id))
        self.database.execute(tenantid, query, commit=commit)
        return userid, role.id
    
    def retrieve_userroles(self, userid, tenantid):
        query = ("select r.id as id, r.name as name "+
                 "from tr_tnt_userrole as ur "+
                 "left join ms_tnt_role as r on r.id = ur.roleid where ur.userid = "+str(userid))
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            role = Role(row['name'], id=row['id'])
            result.append(role)
        
        return result
    
    def retrieve_role(self, id):
        query = ("select r.id as id, r.name as name "+
                 "from ms_tnt_role as r where r.id = "+str(id))
        fetch_result = self.database.fetch_one(tenantid, query)
        role = None
        if (fetch_result):
            role = Role(fetch_result['name'], id=fetch_result['id'])
        
        return role
        