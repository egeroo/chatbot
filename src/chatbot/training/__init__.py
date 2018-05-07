'''
Created on Mar 19, 2018

@author: Muhammad Ridwan
'''
from chatbot.record import Record, RecordSerializer
from chatbot.category.context import Context, ContextSerializer
from chatbot.category.context.intent import Intent, IntentSerializer
from chatbot.category import Category, CategorySerializer
from serpy import Serializer
from serpy.fields import *

class Training:
    id = None
    record = None
    category = None
    context = None
    intent = None
    
    def __init__(self, record, category, context, intent, id=None):
        self.id = id
        self.record = record
        self.category = category
        self.context = context
        self.intent = intent
        
class TrainingSerializer(Serializer):
    id = IntField(required=True)
    record = RecordSerializer(required=True)
    category = CategorySerializer(required=False)
    context = ContextSerializer(required=False)
    intent = IntentSerializer(required=False)
