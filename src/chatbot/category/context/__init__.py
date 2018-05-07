'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''
from serpy import Serializer
from serpy.fields import *
from chatbot.response import ResponseLibrarySerializer

class Context:
    id = None
    context_id = None
    category_id = None
    name = None
    responses = None
    
    def __init__(self, name, category_id, context_id=None, id=None):
        self.id = id
        self.context_id = context_id
        self.category_id = category_id
        self.name = name
        self.responses = []
    
    def set_responses(self, responses):
        self.responses = responses
    
class ContextSerializer(Serializer):
    id = IntField(required=True)
    context_id = IntField(required=True)
    name = StrField(required=True)

class ContextLibrarySerializer(Serializer):
    context_id = IntField(required=True)
    name = StrField(required=True)
    responses = ResponseLibrarySerializer(many=True)
    
NO_CONTEXT_UNCATEGORIZED = Context("No Context", 0, context_id=0)
NO_CONTEXT_COMMAND = Context("No Context", 1, context_id=0)
NO_CONTEXT_PRODUCT_RELATED_CONVERSATION = Context("No Context", 2, context_id=0)
NO_CONTEXT_GENERAL_CONVERSATION = Context("No Context", 3, context_id=0)