'''
Created on 21.10.2017

@author: uschoen
'''
import base64,hashlib,sys,os
from time import localtime, strftime
from Crypto.Cipher import AES
from datetime import datetime
import json

class decode(object):
    '''
    classdocs
    '''
    def __init__(self,user,password,params,log):
        
        '''
        Constructor
        '''
        self.args=params
        self.logger=log
        self.__user=user
        self.__password=password
        self.__calling="unkown"
        self.__reqArgs={}
        self.__version=1
    
    def requstEncode(self,header):
        calling="unkown"
        argsEncode={}
        user="unkown"
        (user,body)=self.__enecodeHeader(self.__unserialData(header))
        (calling,argsEncode,password)=self.__encodeBody(body)
        return (user,calling,argsEncode)
    def __encodeBody(self,body):
        unserialBody=self.__unserialData(body)
        return (unserialBody['calling'],unserialBody['args'],unserialBody['password'])
    
    def __enecodeHeader(self,header):
        try:
            enheader=header
            return (enheader['user'],enheader['body'])
        except:
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:%s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))  
             
    def requst(self,version,calling,args):
        self.__reqArgs=args
        self.__calling=calling
        self._version=version
        return self.__serialData(self.__decodeHeader())
    
    def __decodeBody(self):
        body={
                    'calling':self.__calling,
                    'args':self.__reqArgs,
                    'password':self.__password}
        return self.__serialData(body)
        
    def __decodeHeader(self):
        header={
                'user':self.__user,
                'version':self.__version,
                'body':self.__decodeBody()}
        return header
                  
    def __serialData(self,data):
        return json.dumps(data)
    
    def __unserialData(self,data):
        return json.loads(data)
    
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
    def log (self,level="unkown",messages="no messages"):
        if self.logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.logger.write(conf)   