'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''

from serpy import Serializer
from serpy.fields import *

class Response:
    id = None
    sentence = None
    context_id = None
    intent_id = None
    
    def __init__(self, sentence, context_id, intent_id=None, id=None):
        self.id = id
        self.sentence = sentence
        self.context_id = context_id
        self.intent_id = intent_id

class ResponseSerializer(Serializer):
    id = IntField(required=True)
    sentence = StrField(required=True)
    context_id = IntField(required=True)
    intent_id = IntField()

class ResponseLibrarySerializer(Serializer):
    id = IntField(required=True)
    sentence = StrField(required=True)