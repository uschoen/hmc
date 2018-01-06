'''
Created on 06.01.2018

@author: uschoen
'''
import logging
import json
from unittest.test.testmock.testpatch import function

class web(object):
    '''
    classdocs
    TODO: write and define Protocol
    '''


    def __init__(self,params):
        '''
        configuration data
        '''
        self.__params={
                    "password": "password", 
                    "user": "user"
                    }
        self.__params.update(params)
        ''' logging instance '''
        self.__log=logging.getLogger(__name__)
        
    def decode(self,string):
        self.__log.info("get new web message to decode")
        try:
            
        except:
    
    def encode(self,data,resultStatus): 
        self.__log.info("get new web message to encode")
        try:
            
        except:
            
                
    def _unserialMSG(self,string):
        '''
        unserial a message to a dictionary
        '''
        self.__log.debug("unserial message")
        try:
            jsonString=json.loads(string)
            return jsonString
        except:
            self.__log.error("can not unserial message %s"%(string),exc_info=True)  
            
    def _serialMSG(self,dicVar):
        '''
        serial a message to a string
        '''
        self.__log.debug("unserial message")
        try:
            jsonString=json.dumps(dicVar)
            return jsonString
        except:
            self.__log.error("can not unserial message %s"%(string),exc_info=True)   
              