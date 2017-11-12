'''
Created on 18.10.2017

@author: uschoen
'''
from time import localtime, strftime,sleep
from datetime import datetime
import socket
import sys,os,threading
import coreProtokoll

class server(threading.Thread):
    '''
    classdocs
    '''


    def __init__(self,params,core,logger):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.core=core
        self.logger=logger
        self.args=params
        self.running=1
        self.socket=False
        self.coreDataobj=coreProtokoll.code(self.args['user'],self.args['password'],self.logger)
        self.log("debug","build socket Server")
        
    def log (self,level="unkown",messages="no messages"):
        if self.logger:
            dt = datetime.now()
            conf={}
            conf['package']="%s.%s"%(__name__,self.args['hostName'])
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.logger.write(conf)  
            
    def run(self):
        self.log("debug","starting socket server")
        while self.running:
            try:
                if not self.socket:
                    self.buildSocket()
                (con, addr) = self.socket.accept()  
                self.log("debug","get connection from %s"%(addr[0]))
                threading.Thread(target=self.listenToClient,args = (con,addr)).start()
                self.log("debug","start new client thread:%s"%(con))
            except :
                self.log("error",sys.exc_info())
                tb = sys.exc_info()
                for msg in tb:
                    self.log("error","Traceback Info:%s"%(msg)) 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
                self.log("error","socket error, wait %i sec for new connection"%(self.args['timeout']))
                sleep(self.args['timeout'])
                
    def listenToClient(self, client, address):
        size = 8192
        while True:
            try:
                data = client.recv(size)
                if data:
                    try:
                        self.log("debug","get message: %s"%(data))
                        (user,password,calling,args)=self.coreDataobj.encode(data)
                        self.log("debug","calling function:%s user:%s"%(calling,user))
                        self.log("debug","args %s"%(args))
                        method_to_call = getattr(self.core,calling)
                        method_to_call(*args)
                        client.sendall(self.coreDataobj.decode('result',{'result':"success"}))
                        self.log("debug","send result success")
                    except:
                        tb = sys.exc_info()
                        for msg in tb:
                            self.log("error","Traceback Info:%s"%(msg)) 
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
                        client.sendall(self.coreDataobj.decode('result',{'result':"error"}))
                        self.log("debug","send result error")
                else:
                    self.log("debug","client disconnected")
                    break
            except:
                self.log("error",sys.exc_info())
                tb = sys.exc_info()
                for msg in tb:
                    self.log("error","Traceback Info:%s"%(msg)) 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
                self.log("debug","close client connection")
                client.close()
                return False
            
    def buildSocket(self):
        self.log("debug","try to build socket ip:%s:%s"%(self.args['ip'],self.args['port']))
        try:
            self.socket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.args['ip'],int(self.args['port'])))
            self.socket.listen(5)
            self.log("info","socket ip:%s:%s is ready"%(self.args['ip'],self.args['port']))
        
        except :
            self.socket=False
            self.log("error","can not build socket ip:%s:%s"%(self.args['ip'],self.args['port']))
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info: %s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            raise
        
        
