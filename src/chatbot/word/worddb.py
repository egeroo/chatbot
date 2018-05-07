'''
Created on Mar 27, 2018

@author: Muhammad Ridwan
'''
from database import Database
from chatbot.word import Word, RawWord
from chatbot.word import NeuronBow
import pandas as pd
from neuralnetwork.neuron.type import OUTPUT_NEURON
import os

class WordDBService:
    database = None
    neurondbs = None

    def __init__(self, database, neurondbs):
        self.database = database
        self.neurondbs = neurondbs
    
    def save_rawword(self, rawword, tenantid, commit=True):
        rawword_id = "null"
        if (rawword.word_id != None):
            rawword_id = str(rawword.word_id)
        query = ("insert into tr_lib_rawword(rawword, wordid) values ('"+rawword.value+
                 "', "+rawword_id+")")
        self.database.execute(tenantid, query, commit=commit)
        return self.database.fetch_one(tenantid, "select max(id) from tr_lib_rawword where rawword = '"+rawword.value+"'")['max']
    
    def update_rawword(self, rawword, tenantid, commit=True):
        rawword_id = "null"
        if (rawword.word_id != None):
            rawword_id = str(rawword.word_id)
        query = ("update tr_lib_rawword set rawword = '"+rawword.value+"', wordid = "+rawword_id+
                 " where id = "+str(rawword.id))
        self.database.execute(tenantid, query, commit=commit)
        return rawword.id
    
    def retrieve_rawword(self, id, tenantid):
        query = ("select r.id as id, r.rawword as value, r.wordid as word_id "+
                 "from tr_lib_rawword as r where r.id = "+str(id))
    
        fetch_result = self.database.fetch_one(tenantid, query)
        rawword = None
        if(fetch_result):
            rawword = RawWord(fetch_result['value'], fetch_result['word_id'], id=fetch_result['id'])
        
        return rawword
    
    def retrieve_rawword_by_word(self, word, tenantid):
        query = ("select r.id as id, r.rawword as value, r.wordid as word_id "+
                 "from tr_lib_rawword as r where r.rawword = '"+word+"'")
    
        fetch_result = self.database.fetch_one(tenantid, query)
        rawword = None
        if(fetch_result):
            rawword = RawWord(fetch_result['value'], fetch_result['word_id'], id=fetch_result['id'])
        
        return rawword
    
    def retrieve_rawwords(self, tenantid):
        query = ("select r.id as id, r.rawword as value, r.wordid as word_id "+
                 "from tr_lib_rawword as r ")
    
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            rawword = RawWord(row['value'], row['word_id'], id=row['id'])
            result.append(rawword)
        
        return result
    
    def retrieve_mapped_rawwords(self, tenantid):
        query = ("select r.id as id, r.rawword as value, r.wordid as word_id "+
                 "from tr_lib_rawword as r where r.wordid IS NOT NULL ")
    
        fetch_result = self.database.fetch_all(tenantid, query)
        result = []
        for row in fetch_result:
            rawword = RawWord(row['value'], row['word_id'], id=row['id'])
            result.append(rawword)
        
        return result
    
#     def save_neuronbow(self, neuronbow, tenantid, commit=True):
#         neuron_id = str(neuronbow.neuron_id)
#         word_id = 'null'
#         if (neuronbow.word_id != None):
#             word_id = str(neuronbow.word_id)
#         category_id = 'null'
#         if (neuronbow.category_id != None):
#             category_id = str(neuronbow.category_id)
#         context_id = 'null'
#         if (neuronbow.context_id != None):
#             context_id = str(neuronbow.context_id)
#         n_ascii = 'null'
#         if (neuronbow.ascii != None):
#             n_ascii = str(neuronbow.ascii)
#         query = ("insert into tr_lib_neuronbow(neuronid, wordid, categoryid, contextid, ascii) select " +
#                  neuron_id +", "+word_id+", "+category_id+", "+context_id+", "+n_ascii+" where not exists (select id from tr_lib_neuronbow where neuronid = "+neuron_id+")")
#         self.database.execute(tenantid, query, commit=commit)
#         return self.database.fetch_one(tenantid, "select max(id) from tr_lib_neuronbow where neuronid = "+neuron_id)['max']
    
#     def update_neuronbow(self, neuronbow, tenantid, commit=True):
#         neuron_id = str(neuronbow.neuron_id)
#         word_id = 'null'
#         if (neuronbow.word_id != None):
#             word_id = str(neuronbow.word_id)
#         category_id = 'null'
#         if (neuronbow.category_id != None):
#             category_id = str(neuronbow.category_id)
#         context_id = 'null'
#         if (neuronbow.context_id != None):
#             context_id = str(neuronbow.context_id)
#         n_ascii = 'null'
#         if (neuronbow.ascii != None):
#             n_ascii = str(neuronbow.ascii)
#         query = ("update tr_lib_neuronbow set neuronid = "+neuron_id+", wordid = "+word_id+
#                  ", categoryid = "+category_id+", contextid = "+context_id+", ascii = "+n_ascii+" where id = "+str(neuronbow.id))
#         self.database.execute(tenantid, query, commit=commit)
#         return neuronbow.id
    
#     def delete_neuronbow(self, neuronbow, tenantid, commit=True):
#         query = ("delete from tr_lib_neuronbow where id = "+str(neuronbow.id))
#         self.database.execute(tenantid, query, commit=commit)
#         return neuronbow.id
    
#     def retrieve_neuronbow_by_neuron(self, neuron_id, tenantid):
#         query = ("select n.id as id, n.neuronid as neuronid, n.wordid as wordid, n.contextid as contextid, "+
#                  "n.categoryid as categoryid from tr_lib_neuronbow as n where n.neuronid = "+str(neuron_id))
#         fetch_result = self.database.fetch_one(tenantid, query)
#         neuronbow = None
#         if(fetch_result):
#             neuronbow = NeuronBow(fetch_result['neuronid'], fetch_result['wordid'], fetch_result['categoryid'], fetch_result['contextid'], id=fetch_result['id'])
#         
#         return neuronbow
    
    def retrieve_neuronbow_by_word(self, word, network_name, tenantid):
        neurons = self.neurondbs.load_neurons_from_file(network_name, tenantid)
        neuronbow = None
        
        nb = neurons[neurons['word'] == word]
        if(len(nb) != 0):
            neuronbow = NeuronBow(nb.iloc[0]['word'], nb.iloc[0]['category'], nb.iloc[0]['context'])
        
        return neuronbow
    
#     def retrieve_neuronbow_by_category(self, category_id, tenantid):
#         query = ("select n.id as id, n.neuronid as neuronid, n.wordid as wordid, n.contextid as contextid, "+
#                  "n.categoryid as categoryid from tr_lib_neuronbow as n where n.categoryid = "+str(category_id))
#         fetch_result = self.database.fetch_one(tenantid, query)
#         neuronbow = None
#         if(fetch_result):
#             neuronbow = NeuronBow(fetch_result['neuronid'], fetch_result['wordid'], fetch_result['categoryid'], fetch_result['contextid'], id=fetch_result['id'])
#         
#         return neuronbow

    def retrieve_neuronbow_by_category(self, category, network_name, tenantid):
        neurons = self.neurondbs.load_neurons_from_file(network_name, tenantid)
        neuronbow = None
        
        nb = neurons[neurons['category'] == category]
        if(len(nb) != 0):
            neuronbow = NeuronBow(nb.iloc[0]['word'], nb.iloc[0]['category'], nb.iloc[0]['context'])
        
        return neuronbow
    
#     def retrieve_neuronbow_by_context(self, context_id, tenantid):
#         query = ("select n.id as id, n.neuronid as neuronid, n.wordid as wordid, n.contextid as contextid, "+
#                  "n.categoryid as categoryid from tr_lib_neuronbow as n where n.contextid = "+str(context_id))
#         fetch_result = self.database.fetch_one(tenantid, query)
#         neuronbow = None
#         if(fetch_result):
#             neuronbow = NeuronBow(fetch_result['neuronid'], fetch_result['wordid'], fetch_result['categoryid'], fetch_result['contextid'], id=fetch_result['id'])
#         
#         return neuronbow

    def retrieve_neuronbow_by_context(self, context, network_name, tenantid):
        neurons = self.neurondbs.load_neurons_from_file(network_name, tenantid)
        neuronbow = None
        
        nb = neurons[neurons['context'] == context]
        if(len(nb) != 0):
            neuronbow = NeuronBow(nb.iloc[0]['word'], nb.iloc[0]['category'], nb.iloc[0]['context'])
        
        return neuronbow
    
    def retrieve_word(self, id, tenantid):
        words = pd.read_csv(os.path.join(os.path.join("tenant-data", tenantid),"words.csv"))
#         words = words.where(pd.notnull(words), None)
        word = None
        
        w = words[words['id'] == id]
        if(len(w) != 0):
            word = Word(w.iloc[0]['word'], id=w.iloc[0]['id'])
        
        return word
    
    def retrieve_words(self, tenantid):
        df = pd.read_csv(os.path.join(os.path.join("tenant-data", tenantid),"words.csv"))
#         df = df.where(pd.notnull(df), None)
        words = []
        for index, w in df.iterrows():
            word = Word(w['word'], id=w['id'])
            words.append(word)
        return words
    
    def retrieve_word_by_word(self, value, tenantid):
        words = pd.read_csv(os.path.join(os.path.join("tenant-data", tenantid),"words.csv"))
#         words = words.where(pd.notnull(words), None)
        word = None
        
        w = words[words['word'] == value]
        if(len(w) != 0):
            word = Word(w.iloc[0]['word'], id=w.iloc[0]['id'])
        
        return word
    
    def retrieve_similar_words(self, value, limit, tenantid):
        words = pd.read_csv(os.path.join(os.path.join("tenant-data", tenantid),"words.csv"))
        handle_nan = "nan".startswith(value)
        filtered_words = words[words['word'].str.startswith(value, na=handle_nan)]
        result = []
        for index, w in filtered_words.iterrows():
            if(len(result) < limit):
                word = Word(w['word'], id=w['id'])
                result.append(word)
        
        return result
    
    def retrieve_output_neuronbow_by_neuronindex(self, network_name, neuron_index, tenantid):
        neurons = self.neurondbs.load_neurons_from_file(network_name, tenantid)
        
        neuronbow = None
        
        nb = neurons[(neurons['type'] == OUTPUT_NEURON.id) & (neurons['index'] == neuron_index)]
        if(len(nb) != 0):
            neuronbow = NeuronBow(nb.iloc[0]['word'], nb.iloc[0]['category'], nb.iloc[0]['context'])
        
        return neuronbow
        