'''
Created on Mar 16, 2018

@author: Muhammad Ridwan
'''

from serpy import Serializer
from serpy.fields import *

class Word:
    id = None
    value = None
    
    def __init__(self, value, id=None):
        self.id = id
        self.value = value

class RawWord:
    id = None
    value = None
    word_id = None
    word = None
    
    def __init__(self, value, word_id, id=None):
        self.id = id
        self.value = value
        self.word_id = word_id
    
    def set_word(self, word):
        self.word = word
    
class NeuronBow:
    word = None
    category = None
    context = None
    ascii = None
    
    def __init__(self, word, category, context):
        self.word = word
        self.category = category
        self.context = context
    
    def set_ascii(self, ascii):
        self.ascii = ascii

class RawWordSerializer(Serializer):
    id = IntField(required=True)
    value = StrField(required=True)
    word_id = IntField(required=False)
    word = StrField(required=False)
    
class WordSerializer(Serializer):
    id = IntField(required=True)
    value = StrField(required=True)