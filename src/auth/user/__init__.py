'''
Created on Apr 24, 2018

@author: Muhammad Ridwan
'''
from passlib.apps import custom_app_context as pwd_context

class User:
    id = None
    username = None
    hashed_password = None
    roles = None
    
    def __init__(self, username, hashed_password, roles, id=None):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        if not roles:
            self.roles = []
        else:
            self.roles = roles
            
    def add_role(self, role):
        self.roles.append(role)
    
    def remove_role(self, role):
        new_roles = []
        for r in self.roles:
            if r.id != role.id:
                new_roles.append(r)
        self.roles = new_roles 
    
    def hash_password(self, password):
        self.hashed_password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)
    
    def is_admin(self):
        for role in self.roles:
            if role.id == ADMIN.id:
                return True
        return False
    
    def is_superadmin(self):
        for role in self.roles:
            if role.id == SUPERADMIN.id:
                return True
        return False

class Role:
    id = None
    name = None
    
    def __init__(self, name, id=None):
        self.id = id
        self.name = name
    
SUPERADMIN = Role("Super Admin", id=1)
ADMIN = Role("Admin", id=2)
USER = Role("User", id=3)