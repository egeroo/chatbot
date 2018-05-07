'''
Created on Mar 13, 2018

@author: Muhammad Ridwan
'''
import psycopg2
from psycopg2 import *
from psycopg2 import extras
import os
from datetime import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Tenant:
    host = None
    dbname = None
    user = None
    password = None
    connection = None
    cursor = None
    
    def __init__(self, host, dbname, user, password):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
    
    def open_connection(self):
        try:
            self.connection = connect(host=self.host, dbname="ailegro-tenant-"+self.dbname, user=self.user, password=self.password)
            self.cursor = self.connection.cursor(cursor_factory=extras.DictCursor)
        except BaseException as e:
            raise e
    
    def execute(self, query, commit=True):
        try:
            self.cursor.execute(query)
            if(commit):
                self.commit()
        except BaseException as e:
            raise e
    
    def fetch_one(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()
        except BaseException as e:
            raise e
    
    def fetch_all(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except BaseException as e:
            raise e
    
    def commit(self):
        try:
            self.connection.commit()
        except BaseException as e:
            raise e
    
    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.close()
        except BaseException as e:
            raise e

class Database:
    host = None
    dbname = None
    user = None
    password = None
    connection = None
    cursor = None
    tenants = []
    
    def __init__(self, host, dbname, user, password):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        try:
            self.connection = connect(host=self.host, dbname=self.dbname, user=self.user, password=self.password)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor(cursor_factory=extras.DictCursor)
            query = "select * from tenant where is_active = TRUE"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if (result):
                for row in result:
                    query = "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('ailegro-tenant-"+row['tenantid']+"');"
                    self.cursor.execute(query)
                    result = self.cursor.fetchone()
                    if not result:
                        query = 'CREATE DATABASE "ailegro-tenant-' + row['tenantid']+'";'
                        self.cursor.execute(query)
                    
                    tenant = Tenant(host, row['tenantid'], user, password)
                    query = ("select exists (select 1 from information_schema.tables where table_schema = 'public' " +
                             "and table_name = 'ms_tnt_version');")
                    tenant.open_connection()
                    result = tenant.fetch_one(query)[0]
                    if (not result):
                        for file in os.listdir("./database/sql"):
                            if file.startswith("1_1__") and file.endswith(".sql"):
                                filename = file.strip(".sql").split("__")
                                version = filename[0].replace('_', '.')
                                
                                fd = open("./database/sql/"+file, 'r')
                                query = fd.read()
                                description = filename[1].replace('-', ' ')
                                query += (" insert into ms_tnt_version(version, description, timestamp) values ('"+
                                         version+"', '"+description+"', '"+str(datetime.utcnow())+"');")
                                tenant.execute(query, commit=False)
                    
                    files = os.listdir("./database/sql")
                    files.sort(key=lambda x: float(x.split("__")[0].replace('_', '.')))
                    for file in files:
                        if file.endswith(".sql"):
                            filename = file.strip(".sql").split("__")
                            version = filename[0].replace('_', '.')
                            query = "select * from ms_tnt_version where version = '"+version+"'"
                            result = tenant.fetch_one(query)
                            if (not result):
                                fd = open("./database/sql/"+file, 'r')
                                query = fd.read()
                                description = filename[1].replace('-', ' ')
                                query += (" insert into ms_tnt_version(version, description, timestamp) values ('"+
                                         version+"', '"+description+"', '"+str(datetime.utcnow())+"');")
                                tenant.execute(query, commit=False)
                    tenant.commit()
                    tenant.close_connection()
                    self.tenants.append(tenant)
                    
        except BaseException as e:
            raise e
    
    def create_tenant(self, tenantid):
        try:
            query = "INSERT INTO tenant(tenantid) VALUES ('"+str(tenantid)+"');"
            self.cursor.execute(query)
            
            query = 'CREATE DATABASE "'+tenantid+'";'
            self.cursor.execute(query)
                    
            tenant = Tenant(self.host, tenantid, self.user, self.password)
            tenant.open_connection()
            files = os.listdir("./database/sql")
            files.sort(key=lambda x: float(x.split("__")[0].replace('_', '.')))
            for file in files:
                if file.endswith(".sql"):
                    filename = file.strip(".sql").split("__")
                    version = filename[0].replace('_', '.')
                    fd = open("./database/sql/"+file, 'r')
                    query = fd.read()
                    description = filename[1].replace('-', ' ')
                    query += (" insert into ms_tnt_version(version, description, timestamp) values ('"+
                             version+"', '"+description+"', '"+str(datetime.utcnow())+"');")
                    tenant.execute(query, commit=False)
            tenant.commit()
            tenant.close_connection()
            self.tenants.append(tenant)
            
            return tenantid        
        except BaseException as e:
            raise e
    
    def delete_tenant(self, tenantid):
        try:
            for tenant in self.tenants:
                if tenant.dbname == tenantid:
                    query = "UPDATE tenant SET is_active = FALSE where tenantid = '"+tenantid+"'"
                    self.cursor.execute(query)
                    
                    tenant.close_connection()
                    self.tenants.remove(tenant)
                    return tenantid
            return None        
        except BaseException as e:
            raise e
        
    
    def open_connection(self):
        for tenant in self.tenants:
            tenant.open_connection()
    
    def execute(self, tenant_id, query, commit=True):
        for tenant in self.tenants:
            if tenant.dbname == tenant_id:
                tenant.execute(query, commit=commit)
    
    def fetch_one(self, tenant_id, query):
        for tenant in self.tenants:
            if tenant.dbname == tenant_id:
                return tenant.fetch_one(query)
        return None
    
    def fetch_all(self, tenant_id, query):
        for tenant in self.tenants:
            if tenant.dbname == tenant_id:
                return tenant.fetch_all(query)
        return None
    
    def commit(self, tenant_id):
        for tenant in self.tenants:
            if tenant.dbname == tenant_id:
                tenant.commit()
    
    def close_connection(self):
        for tenant in self.tenants:
            tenant.close_connection()
    
    def get_tenants(self):
        t = []
        for tenant in self.tenants:
            t.append(tenant.dbname)
        return t
