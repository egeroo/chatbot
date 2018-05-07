'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''

from serpy import Serializer
from serpy.fields import *
from chatbot.category.context import ContextSerializer, ContextLibrarySerializer

class Category:
    id = None
    category_id = None
    name = None
    contexts = None
    
    def __init__(self, name, category_id = None, id=None):
        self.id = id
        self.category_id = category_id
        self.name = name
        self.contexts = []
    
    def set_contexts(self, contexts):
        self.contexts = contexts
    
class CategorySerializer(Serializer):
    id = IntField(required=True)
    category_id = IntField(required=True)
    name = StrField(required=True)

class CategoryLibrarySerializer(Serializer):
    category_id = IntField(required=True)
    name = StrField(required=True)
    contexts = ContextLibrarySerializer(many=True)

UNCATEGORIZED = Category("Uncategorized", category_id=0)
COMMAND = Category("Command", category_id=1)
PRODUCT_RELATED_CONVERSATION = Category("Product Related Conversation", category_id=2)
GENERAL_CONVERSATION = Category("General Conversation", category_id=3)
    