'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "2.0"


import json,base64,hashlib,logging
from Crypto.Cipher import AES


class code(object):
    '''
    classdocs
    '''


    def __init__(self,user,password):
    
        self.logger=logging.getLogger(__name__)  
        self.verion=1
        self.user=user
        self.password=password
        self.logger.info("corProtokoll build")
        
    def decode(self,calling,args):
        body=self.__decodeBody(calling, args, self.password)
        string=self.__decodeHeader(self.user,body)
        return (string)
    
    def encode(self,string):
        try:
            (user,body)=self.__enecodeHeader(string)
            (calling,args,password)=self.__encodeBody(body)
            return (user,password,calling,args)
        except:
            self.logger.error( "can not convert meassage")
            raise Exception  
    
    def __enecodeHeader(self,header):
        try:
            encodeHeader=self.__unserialData(header)
            if not 'user' in encodeHeader and not 'body' in encodeHeader:    
                self.logger.error( "no user or body found in meassage header")
                raise Exception
            return (encodeHeader['user'],encodeHeader['body'])          
        except:
            self.logger.error( "can not convert meassage")
            raise Exception
    
    def __decodeHeader(self,user,body):
        header={
                'user':user,
                'version':self.verion,
                'body':body}
        return self.__serialData(header)
    
    def __encodeBody(self,body):
        try:
            unserialBody=self.__unserialData(body)
            if 'calling' in unserialBody and 'args' in unserialBody and 'password' in unserialBody:
                return (unserialBody['calling'],unserialBody['args'],unserialBody['password'])
            self.logger.error( "body mismatch")
            raise Exception
        except:
            self.logger.error( "body mismatch")
            raise Exception
    
    def __decodeBody(self,calling,args,password):
        body={
                    'calling':calling,
                    'args':args,
                    'password':password}
        return self.__serialData(body)
    
    def __serialData(self,data):
        self.logger.debug("serial messages")
        return json.dumps(data)   
    
    def __unserialData(self,data):
        self.logger.debug("unserial messages")
        try:
            jsonData=json.loads(data)
            return jsonData
        except:
            self.logger.error( "can not covert to json string")
            raise Exception
    
    def __strgrjust(self,string):
        '''
        return extended a string with space with a mutible of 16
        '''
        if  (len(string)/float(16))-(len(string)/16)==0:
            return string   
        return string.rjust(((len(string)/16)+1)*16)
                
    def __decode(self,string):
        '''
        return a decode a string
        '''
        cipherOBJ = AES.new(self.__md5decode(self.__password),AES.MODE_ECB)
        stringBase64=base64.b64decode(self.__strgrjust(string))
        return cipherOBJ.decrypt(stringBase64)
                
    def __encode(self,string):
        '''
        return a encode a string
        '''
        cipher = AES.new(self.md5decode(self.self.__password),AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(string))
       
    def __md5decode(self,string):
        ''' 
        convert a string to a md5 hash
        '''
        md = hashlib.md5()
        md.update(string)
        return md.digest() 