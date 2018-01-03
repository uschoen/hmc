'''
Created on 18.10.2017

@author: uschoen
'''
from time import sleep
import socket
import threading,logging
import coreProtocol

BUFFER=8192

class server(threading.Thread):
    '''
    classdocs
    '''


    def __init__(self,args,core):
        '''
        Constructor
        '''
        self.STARTMARKER="!!!<<<start>>>"
        self.ENDMARKER="<<<end>>>!!!"
        threading.Thread.__init__(self)
        self.core=core
        self.logger=logging.getLogger(__name__) 
        self.args={
                    "enable": False, 
                    "hostName": "unkown", 
                    "ip": "127.0.0.1", 
                    "password": "password", 
                    "port": 5090, 
                    "timeout": 50, 
                    "user": "user",
                    "aes":False}
        self.args.update(args)
        self.running=1
        self.socket=False
        self.coreDataobj=coreProtocol.code(self.args['user'],self.args['password'],self.args['aes'])
        self.logger.debug("build socket Server")
        self.sendNR=0
        self.__lastMSG=""
            
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
                self.logger.error("socket error",exc_info=True)
                
                
    def listenToClient(self, clientsocket, address):
        while self.running:
            try:
                data = self.__readClientData(clientsocket)
                if data:
                    try:
                        #self.logger.debug("recive:%s"%(data))
                        self.logger.debug("get message try to decode")
                        (user,password,calling,args)=self.coreDataobj.uncrypt(data)
                        self.logger.debug("calling function:%s user:%s"%(calling,user))
                    except:
                        self.logger.error("get error uncryt message",exc_info=True)
                        resultMSG=self.coreDataobj.decrypt('result',{'result':"error"})+self.ENDMARKER     
                        clientsocket.sendall(resultMSG)
                        self.logger.debug("send result error")
                        clientsocket.close()
                        break
                    #file = open('log/recive.txt','a') 
                    #file.write('%i %s %s\n'%(self.sendNR,calling,args)) 
                    #file.close() 
                    #self.sendNR=self.sendNR+1
                     
                    try:     
                        method_to_call = getattr(self.core,calling)
                        method_to_call(*args)
                        resultMSG=self.coreDataobj.decrypt('result',{'result':"success"})+self.ENDMARKER
                        clientsocket.sendall(resultMSG)
                        clientsocket.close()
                        self.logger.debug("send result success")
                        break
                    except:
                        self.logger.error("get error from core, for function:%s"%(calling),exc_info=True)
                        resultMSG=self.coreDataobj.decrypt('result',{'result':"error"})+self.ENDMARKER
                        clientsocket.sendall(resultMSG)
                        self.logger.debug("send result error")
                        clientsocket.close()
                        break
                else:
                    self.logger.debug("client disconnected") 
                    break
            except:
                self.logger.error("some error for lissen to the client",exc_info=True)
                self.logger.debug("close client connection")
                clientsocket.close()
                return False
    
    def __readClientData (self,clientsocket):
        revData=self.__lastMSG
        try:
            while True:
                data = clientsocket.recv(BUFFER)
                revData=revData+data
                if self.ENDMARKER in revData or not data:
                    if revData.endswith(self.ENDMARKER):
                        self.__lastMSG=""
                        revData=revData.replace(self.ENDMARKER,"")
                        break   
                    if self.ENDMARKER in revData:
                        (revData,self.__lastMSG)=revData.split(self.ENDMARKER)
                        break
                    if not data:
                        self.logger.error("receive no %s data from core %s %s"%(self.ENDMARKER,self.args['hostName'],revData))
                        raise
            return revData
        except:
            self.logger.error("error to receive answer from core %s"%(self.args['hostName']),exc_info=True) 
            raise  
                
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
    def _socketClose(self):
        '''
        ' close the network socket
        '''
        self.logger.info("close socket from server")
        self.socket.close() 
           
    def shutdown(self):
        '''
        ' shutdown the cocket server
        '''
        self.logger.info("shutdown socket server")
        self.running=False
        self._socketClose()
