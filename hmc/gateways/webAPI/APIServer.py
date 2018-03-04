'''
Created on 06.01.2018

@author: uschoen
'''


import threading
import socket
import logging
import time
import webProtocol


__version__="3.0"
BUFFER=8192

class server(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        ''' core instance '''
        self.__core=core
        ''' configuration '''
        self.__args={
                    "enable": True, 
                    "hostName": "unknown", 
                    "ip": "127.0.0.1", 
                    "password": "password", 
                    "port": 9090, 
                    "timeout": 50, 
                    "user": "user"
                    }
        self.__args.update(params)
        ''' 
        allow call able function 
        TODO: test and add all core function to allowFunktions
        '''
        self.__allowFunktions=[
            "getAllDeviceId",
            "getAllDeviceChannel",
            "writeAllConfiguration",
            "writeEventHandlerFile",
            "writeDevicesFile"]
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
        ''' MSG End marker '''
        self.__ENDMARKER="<<<end>>>!!!"
        ''' webProtocol class '''
        self.__webProtocol=webProtocol.web({"user":self.__args.get('user'),"password":self.__args.get('password')})
        
        self.__log.debug("build  %s instance with version %s"%(__name__,__version__))
    
    def run(self):
        '''
        run gateway
        '''
        try:
            self.__log.info("%s start"%(__name__))
            while self.running:
                self.__buildSocket()
                if self.__blockTime<int(time.time()):
                    try:
                        self.__socket.settimeout(3)
                        (con, addr) = self.__socket.accept() 
                        self.__socket.settimeout(None) 
                        self.__log.debug("get connection from %s"%(addr[0]))
                        threading.Thread(target=self.__listenToClient,args = (con,addr[0])).start()
                        self.__log.debug("start new client thread:%s"%(con))
                    except:
                        pass
                time.sleep(0.1)    
            self.__log.critical("%s normally stop:"%(__name__))
        except:
            self.__log.critical("%s have a problem and stop"%(__name__),exc_info=True) 
          
    
    def shutdown(self):
        '''
        shutdown server
        '''
        self.running=0
        self.__closeSocket(self.__socket)
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
                        raise Exception
            return revData
        except:
            self.__log.error("error to receive answer from core %s"%(self.__args.get('hostName')),exc_info=True) 
            raise Exception
        
    def __listenToClient(self,clientsocket,address):
        '''
        working client request
        '''
        self.__log.debug("get new client request from %s"%(address))
        while self.running:
            try:
                data = self.__readClientData(clientsocket)
                (function,args,userStatus)=self.__webProtocol.decode(data)
            except:
                self.__sendAnwser(clientsocket,self.__webProtocol.encode("result",{"message":"error in json data"},"0"))
                break
            if not userStatus:
                self.__sendAnwser(clientsocket,self.__webProtocol.encode("result",{"message":"user or password error"},"0"))
                break
            try:
                if function in self.__allowFunktions:
                    self.__log.info("try to call function: %s"%(function))
                    try:
                        method_to_call = getattr(self.__core,function)
                        funcArgs=method_to_call(*args)
                        self.__sendAnwser(clientsocket,self.__webProtocol.encode("result",funcArgs,"1"))
                        break
                    except:
                        self.__log.error("can not call function: %s"%(function),exc_info=True)
                        self.__sendAnwser(clientsocket,self.__webProtocol.encode("result",{"message":"function %s have some error"%(function)},"0"))
                        break
                else: 
                    self.__log.error("error function: %s i not allow"%(function))
                    self.__sendAnwser(clientsocket,self.__webProtocol.encode("result",{"message":"function_%s not allow"%(function)},"0"))
                    break
                     
            except:
                self.__log.error("error while fetching data from %s"%(address),exc_info=True)
                self.__sendAnwser(clientsocket,self.__webProtocol.encode("result",{"message":"error in request"},"0"))
                break
        self.__closeSocket(clientsocket)       
                
    
    def __sendAnwser(self,clientsocket,MSGstring):
        try:
            clientsocket.sendall(MSGstring+self.__ENDMARKER)
        except:
            self.__log.error("can not send message",exc_info=True)
           
    def __closeSocket(self,clientsocket):
        ''' close the server socket '''
        try:
            if clientsocket:
                clientsocket.close()
        except:
            pass
        self.__log.debug("close socket server")
                
    
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
        self.__log.debug("try to build socket ip:%s:%s"%(self.__args.get('ip'),self.__args.get('port')))
        try:
            self.__socket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((self.__args.get('ip'),int(self.__args.get('port'))))
            self.__socket.setblocking(0)
            self.__socket.listen(5)
            self.__unblockServer()
            self.__log.info("socket ip:%s:%s is ready"%(self.__args.get('ip'),self.__args.get('port')))
        except :
            self.__blockServer()
            self.__socket=False
            self.__log.error("can not build socket ip:%s:%s"%(self.__args.get('ip'),self.__args.get('port')),exc_info=True)
            