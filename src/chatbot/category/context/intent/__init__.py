'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''
from serpy import Serializer
from serpy.fields import *

class Intent:
    id = None
    intent_id = None
    context_id = None
    name = None
    
    def __init__(self, name, context_id, intent_id=None, id=None):
        self.id = id
        self.intent_id = intent_id
        self.context_id = context_id
        self.name = name
        
class IntentSerializer(Serializer):
    id = IntField(required=True)
    intent_id = IntField(required=True)
    context_id = IntField(required=True)
    name = StrField(required=True)
    