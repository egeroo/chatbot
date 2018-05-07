'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''
from datetime import datetime
from chatbot.category.context import Context, ContextSerializer
from chatbot.category.context.intent import Intent, IntentSerializer
from chatbot.category import Category, CategorySerializer
from serpy import Serializer
from serpy.fields import *

class Record:
    id = None
    sentence = None
    category = None
    context = None
    intent = None
    record_time = None
    
    def __init__(self, sentence, category, context, intent, record_time=datetime.utcnow(), id=None):
        self.id = id
        self.sentence = sentence
        self.category = category
        self.context = context
        self.intent = intent
        self.record_time = record_time
    
class RecordSerializer(Serializer):
    id = IntField(required=True)
    sentence = StrField(required=True)
    category = CategorySerializer(required=True)
    context = ContextSerializer(required=True)
    intent = IntentSerializer(required=False)
    record_time = StrField(required=True)
    
    
    