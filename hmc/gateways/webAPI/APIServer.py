'''
Created on 06.01.2018

@author: uschoen
'''


import threading
import socket
import logging
import time
import webProtocol
from gateways.webAPI import webProtocol

__version__="3.0"
BUFFER=8192

class server(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        ''' core instance '''
        self.__core=core
        ''' configuration '''
        self.__args={
                    "enable": False, 
                    "hostName": "unknown", 
                    "ip": "127.0.0.1", 
                    "password": "password", 
                    "port": 9090, 
                    "timeout": 50, 
                    "user": "user"
                    }
        self.__args.update(params)
        ''' logger instance '''
        self.__log=logging.getLogger(__name__) 
        ''' running flag '''
        self.running=self.__args.get('enable')
        ''' blocking time'''
        self.__blockTime=0
        ''' server socket '''
        self.__socket=False
        ''' recvied msg '''
        self.__lastMSG=""
        ''' MSG Start marker '''
        self.__STARTMARKER="!!!<<<start>>>"
        ''' MSG End marker '''
        self.__ENDMARKER="<<<end>>>!!!"
        ''' webProtocol class '''
        self.__webProtocol=webProtocol.web()
        self.__log.debug("build  %s instance with version %s"%(__name__,__version__))
    
    def run(self):
        '''
        run gateway
        '''
        self.__log.info("%s start"%(__name__))
        while self.running:
            self.__buildSocket()
            if self.__blockTime<int(time.time()):
                (con, addr) = self.__socket.accept()  
                self.__log.debug("get connection from %s"%(addr[0]))
                threading.Thread(target=self.__listenToClient,args = (con,addr)).start()
                self.__log.debug("start new client thread:%s"%(con))
            time.sleep(0.1)    
        self.__log.critical("%s stop:"%(__name__))   
    
    def shutdown(self):
        '''
        shutdown server
        '''
        self.running=0
        self.__closeSocket()
        self.__log.critical("stop %s thread"%(__name__))
    
    def __readClientData (self,clientsocket):
        '''
        read the data from a socket and check if the endmarker set
        
        clientsocket: network socket of the communication
        
        exception: raise a exception if a error in the communication
        '''
        revData=self.__lastMSG
        try:
            while True:
                data = clientsocket.recv(BUFFER)
                revData=revData+data
                if self.__ENDMARKER in revData or not data:
                    if revData.endswith(self.__ENDMARKER):
                        self.__lastMSG=""
                        revData=revData.replace(self.__ENDMARKER,"")
                        break   
                    if self.__ENDMARKER in revData:
                        (revData,self.__lastMSG)=revData.split(self.__ENDMARKER)
                        break
                    if not data:
                        self.__log.error("receive no %s data from core %s %s"%(self.__ENDMARKER,self.__args.get('hostName'),revData))
                        raise
            return revData
        except:
            self.__log.error("error to receive answer from core %s"%(self.__args.get('hostName'),exc_info=True) 
            raise  
        
    def __listenToClient(self,clientsocket,address):
        '''
        working client request
        '''
        self.__log.debug("get new client request from %s"%(address))
        while self.running:
            try:
                data = self.__readClientData(clientsocket)
                (function,args)=self.__webProtocol.decode(data) #TODO: define args to take over to webProtokoll
                ''' TODO: write function to end
            except:
                self.__log.error("error while fetching data from %s"%(address),exc_info=True)
    
    def __closeSocket(self):
        ''' close the server socket '''
        try:
            if self.__socket:
                self.__socket.close()
                self.__log.critical("close socket server")
        except:
            self.__log.warning("socket is closed")
                
    
    def __unblockServer(self):
        '''
        unblock the server for new connections
        '''
        self.__log.info("unblock server ")
        self.__blockTime=0
        
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        self.__log.error("block server for %i sec"%(self.__args.get('timeout')))
        self.__blockTime=self.__args.get('timeout')+int(time.time())
        
    def __buildSocket(self):
        '''
        build a socket connection
        
        fetch exception
        '''
        if self.__socket or self.__blockTime>int(time.time()):
            return
        self.__log.debug("try to build socket ip:%s:%s"%(self.args.get('ip'),self.args.get('port')))
        try:
            self.__socket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((self.args.get('ip'),int(self.args.get('port'))))
            self.__socket.listen(5)
            self.____unblockServer()
            self.__log.info("socket ip:%s:%s is ready"%(self.args.get('ip'),self.args.get('port')))
        except :
            self.__blockServer()
            self.__socket=False
            self.__log.error("can not build socket ip:%s:%s"%(self.args.get('ip'),self.args.get('port')),exc_info=True)
            