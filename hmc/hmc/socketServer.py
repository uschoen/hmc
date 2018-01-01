'''
Created on 18.10.2017

@author: uschoen
'''
from time import sleep
import socket
import threading,logging
import coreProtokoll

class server(threading.Thread):
    '''
    classdocs
    '''


    def __init__(self,params,core):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.core=core
        self.logger=logging.getLogger(__name__) 
        self.args=params
        self.running=1
        self.socket=False
        self.coreDataobj=coreProtokoll.code(self.args['user'],self.args['password'],self.args['aes'])
        self.logger.debug("build socket Server")
        self.sendNR=0
            
    def run(self):
        self.logger.debug("starting socket server")
        while self.running:
            try:
                if not self.socket:
                    self.buildSocket()
                (con, addr) = self.socket.accept()  
                self.logger.debug("get connection from %s"%(addr[0]))
                threading.Thread(target=self.listenToClient,args = (con,addr)).start()
                self.logger.debug("start new client thread:%s"%(con))
            except :
                self.logger.error("socket error, wait %i sec. for new connection"%(self.args['timeout']),exc_info=True)
                sleep(self.args['timeout'])
                
    def listenToClient(self, client, address):
        size = 81920
        while True:
            try:
                lock=threading.Lock()
                lock.acquire()
                data = client.recv(size)
                if data:
                    try:
                        #self.logger.debug("recive:%s"%(data))
                        self.logger.debug("get message try to decode")
                        (user,password,calling,args)=self.coreDataobj.uncrypt(data)
                        self.logger.debug("calling function:%s user:%s"%(calling,user))
                        lock.release() 
                        #file = open('log/recive.txt','a') 
                        #file.write('%i %s %s\n'%(self.sendNR,calling,args)) 
                        #file.close() 
                        #self.sendNR=self.sendNR+1
                        method_to_call = getattr(self.core,calling)
                        method_to_call(*args)
                        client.sendall(self.coreDataobj.decrypt('result',{'result':"success"}))
                        self.logger.debug("send result success")
                    except:
                        self.logger.error("get error back from core",exc_info=True)
                        client.sendall(self.coreDataobj.decrypt('result',{'result':"error"}))
                        self.logger.debug("send result error")
                        lock.release() 
                else:
                    self.logger.debug("client disconnected")
                    lock.release() 
                    break
            except:
                self.logger.error("some error for lissen to the client",exc_info=True)
                self.logger.debug("close client connection")
                client.close()
                lock.release() 
                return False
            
    def buildSocket(self):
        self.logger.debug("try to build socket ip:%s:%s"%(self.args['ip'],self.args['port']))
        try:
            self.socket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.args['ip'],int(self.args['port'])))
            self.socket.listen(5)
            self.logger.info("socket ip:%s:%s is ready"%(self.args['ip'],self.args['port']))
        
        except :
            self.socket=False
            self.logger.error("can not build socket ip:%s:%s"%(self.args['ip'],self.args['port']),exc_info=True)
            raise
        
        
