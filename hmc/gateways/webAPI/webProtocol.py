'''
Created on 06.01.2018

@author: uschoen
'''
import logging
import json


class web(object):
    '''
    classdocs
    
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
        ''' Protocol Version '''
        self.__VERSION=1
        
    def decode(self,string):
        '''
        decode a string 
        
        return function,args,resutStatus
        function: function you want to call
        args: arguments
        resultStatus=true or false
        '''
        self.__log.info("get new web message to decode")
        try:
            sendDicVar=self._unserialMSG(string)
            dicVar={
                "user":"unknown",
                "password":"unknown",
                "version":self.__VERSION,
                "function":"unknown",
                "args":{},
                "resultStatus":0
                }
            dicVar.update(sendDicVar)
            userStatus=False
            if dicVar.get('user')==self.__params.get('user') and dicVar.get('password')==self.__params.get('password'):
                userStatus=True
                self.__log.info("request from user:%s ,check user and password is ok"%(self.__params.get('user')))
            else:
                self.__log.warning("request from user:%s ,check user and password  is faild"%(self.__params.get('user')))
            functionName=dicVar.get('function')
            args=dicVar.get('args')
            
            return (functionName,args,userStatus)
        except:
            self.__log.error("some error to decode")
            raise Exception
    
    def encode(self,functionName,args,resultStatus):
        ''' 
        encode function,args,resultStatus to a string
        
        functionName: function you call 
        args: arguments to give back
        resultStatus: true or false, true=success false=fail
        
        return a string
        give the exception back
        '''
        self.__log.info("get new message to encode")
        try:
            dicVar={
                "user":self.__params.get('user'),
                "password":self.__params.get('user'),
                "version":self.__VERSION,
                "function":functionName,
                "args":args,
                "resultStatus":resultStatus
                }
            MSGstring=self._serialMSG(dicVar)
            return MSGstring
        except:
            self.__log.error("can not encode the message",exc_info=True)
                
    def _unserialMSG(self,string):
        '''
        unserial a message to a dictionary
        '''
        self.__log.debug("unserial message")
        try:
            jsonString=json.loads(string)
            return jsonString
        except:
            self.__log.error("can not unserial message %s to a dictionary"%(string),exc_info=True)  
            
    def _serialMSG(self,dicVar):
        '''
        serial a message to a string
        '''
        self.__log.debug("serial message")
        try:
            jsonString=json.dumps(dicVar)
            return jsonString
        except:
            self.__log.error("can not serial message to a string",exc_info=True)