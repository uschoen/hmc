'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "2.0"


import hashlib,logging,os
from Crypto.Cipher import AES
import logging.config
import cPickle


class code(object):
    '''
    classdocs
    '''


    def __init__(self,user,password):
    
        self.logger=logging.getLogger(__name__)  
        self.verion=1
        self.__user=user
        self.__password=password
        self.__AESmode = AES.MODE_CBC
        self.__BS = 16
        self.logger.info("corProtokoll build")
    
    def decode(self,calling,args):
        self.logger.error( "old function decode, use derypt")
        self.decrypt(calling, args)   
        
    def decrypt(self,calling,args):
        """
        give back a string with decode information. The messages
        will be translate in the core protocol.

        Args:
            calling (string): the function to call on the remote core
            args (dic): arguments as dictionary for the calling function
        Examples:
            
            >>>args={'arg1':5,'arg2':'test'}
            >>>string=code.decode('functiontocall',args)
        Returns:
            a string
        """
        self.logger.debug( "start decode message")
        try:
            body=self.__decryptBody(calling, args, self.__password)
            string=self.__decryptHeader(self.__user,body)
            self.logger.debug( "return decode message")
            return (string)
        except:
            self.logger.error( "can not decode message",exc_info=True)
            raise Exception 
    
    def encode(self,string):
        self.logger.error( "old function encode, use unrypt")
        self.uncrypt(string)
        
    def uncrypt(self,string):
        """
        encode a string with core protocol format .

        Args:
            string (string): the recvied decode message
        Examples:
            
            >>>stringMSG="hhssd77787/gsgdgs78"
            >>>(user,password,calling,args)=code.encode(stringMSG)
        Returns:
            user:username who decode
            password=password with decode
            calling=function to call
            args=arguments for the function
        """
        self.logger.debug( "start encode message")
        try:
            (user,body)=self.__encryptHeader(string)
            (calling,args,password)=self.__encryptBody(body)
            self.logger.debug( "return encode message")
            return (user,password,calling,args)
        except:
            self.logger.error( "can not encode message",exc_info=True)
            raise   
    
    def __encryptHeader(self,header):
        self.logger.debug( "read header")
        try:
            encodeHeader=self.__unserialData(header)
            if not 'user' in encodeHeader and not 'body' in encodeHeader:    
                self.logger.error( "no user and / or body found in header")
                raise 
            return (encodeHeader['user'],encodeHeader['body'])          
        except:
            self.logger.error( "can not read header",exc_info=True)
            raise 
    
    def __encryptBody(self,body):
        self.logger.debug( "read body")
        try:
            unserialBody=self.__encrypt(body)            
            unserialBody=self.__unserialData(unserialBody)
            if 'calling' in unserialBody and 'args' in unserialBody and 'password' in unserialBody:
                return (unserialBody['calling'],unserialBody['args'],unserialBody['password'])
            self.logger.error( "body mismatch")
            raise 
        except:
            self.logger.error( "can not read body")
            raise 
        
    def __decryptHeader(self,user,body):
        self.logger.debug( "write header")
        header={
                'user':user,
                'version':self.verion,
                'body':body}
        return self.__serialData(header)
    
    def __decryptBody(self,calling,args,password):
        self.logger.debug( "write body")
        try:
            body={      
                        'calling':calling,
                        'args':args,
                        'password':password}
            
            string=self.__serialData(body)
            body=self.__decrypt(string)
            return body
        except:
            self.logger.error( "can not write body", exc_info=True)
            raise
    
    def __serialData(self,data):
        self.logger.debug("serial data")
        serial_data=cPickle.dumps(data) 
        return serial_data 
    
    def __unserialData(self,data):
        self.logger.debug("un-serial data")
        try:
            jsonData=cPickle.loads(data)
            return jsonData
        except:
            self.logger.error( "can not covert to json string")
            raise Exception
    
    def __strgrjust(self,string):
        length = 16 - (len(string) % 16)
        string += chr(length)*length
        return string
    
    def __decrypt(self, string):
        self.logger.debug( "decrypt message")
        try:
            iv=self.__IVKey()
            decryption_suite = AES.new(self.__md5decode(self.__password), self.__AESmode,iv)
            plain_text =iv+decryption_suite.decrypt(self.__strgrjust(string))
            return plain_text
        except:
            self.logger.error( "can not decrypt message", exc_info=True)
            raise
    def __IVKey(self):
        return (os.urandom(128)[:self.__BS])
   
    def __encrypt(self,cryptstring):
        self.logger.debug( "encrypt message")
        try:
            iv=cryptstring[:self.__BS]
            cryptstring=cryptstring[self.__BS:]
            encryption_suite = AES.new(self.__md5decode(self.__password),self.__AESmode,iv)
            plaintext = encryption_suite.encrypt(cryptstring)
            return plaintext
        except:
            self.logger.error( "can not encrypt message", exc_info=True)
            raise
            
    def __md5decode(self,key):
        ''' 
        convert a string to a md5 hash
        '''
        m = hashlib.md5()
        m.update(key)
        return m.hexdigest()
    
    




if __name__ == "__main__":
    logger={
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "my_module": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": "no"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"]
    }}
    
    user="test"
    password="testpw"
    args={
        'deviceID':"defggf@fdde.de",
        'test':'tedd',
        'demo':{'testzzz':"hhhhh"}
    }
    
    log=logging.getLogger(__name__)  
    logging.config.dictConfig(logger)
    core=code(user,password)
    calling="addDevice"
   
    log.debug("user:%s password:%s"%(user,password)) 
    log.debug ("calling:%s args:%s"%(calling,args))  
   
    decodeString=core.decrypt(calling, args)
    log.debug ("decode string %s"%(decodeString))
    
    user,password,calling,args=core.uncrypt(decodeString) 
    log.debug ("user:%s password:%s calling:%s args:%s"%(user,password,calling,args))