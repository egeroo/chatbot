'''
Created on Apr 24, 2018

@author: ridwan
'''

class ParamType:
    name = None
    type = None
    isclass = None
    mandatory = None
    islist = None

    def __init__(self, name, type, isclass, mandatory, islist):
        self.name = name
        self.type = type
        self.isclass = isclass
        self.mandatory = mandatory
        self.islist = islist
        