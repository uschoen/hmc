'''
Created on 06.01.2018

@author: uschoen
'''


import threading
import socket
import logging
import time
import coreProtocol


__version__="3.1"
BUFFER=1024

class server(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        ''' core instance '''
        self.__core=core
        ''' configuration '''
        self.__args={
                    "hostName": "unknown", 
                    "ip": "127.0.0.1", 
                    "password": "password", 
                    "port": 5090, 
                    "timeout": 50, 
                    "user": "user",
                    "aes":False
                    }
        self.__args.update(params)
        ''' 
        allow call able function 
        TODO: test and add all core function to allowFunktions
        '''
        self.__allowFunktions=[
            "updateCoreClient",
            "updateDevice",
            "updateEventHandler",
            "setDeviceChannelValue",
            "addDevice",
            "updateGateway",
            "addGateway",
            "deleteGateway",
            "startGateway",
            "stopGateway",
            "updateProgram",
            "addDeviceChannel"
            ]
        ''' logger instance '''
        self.__log=logging.getLogger(__name__) 
        ''' running flag '''
        self.running=self.__args.get('enable')
        ''' blocking time'''
        self.__blockTime=0
        ''' server socket '''
        self.__socket=False
        ''' end marker for messages  '''
        self.__ENDMARKER="<<<end>>>!!!"
        ''' webProtocol class '''
        self.__coreProtocol=coreProtocol.code(self.__args.get('user'),self.__args.get('password'),self.__args.get('aes'))
        
        self.__log.debug("build  %s instance with version %s"%(__name__,__version__))
    
    def run(self):
        '''
        run gateway
        '''
        try:
            socket=""
            self.__log.info("%s start"%(__name__))
            while self.running:
                if self.__blockTime<int(time.time()):
                    try:
                        socket=self.__buildSocket()
                        socket.settimeout(1)
                        (clientSocket, addr) = socket.accept() 
                        socket.settimeout(None) 
                        self.__log.debug("get connection from %s"%(addr[0]))
                        threading.Thread(target=self.__listenToClient,args = (clientSocket,addr[0])).start()
                        self.__log.debug("start new client thread:%s"%(clientSocket))
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
        self.__closeSocket()
        self.__log.critical("stop %s thread"%(__name__))
    
    def __readClientData (self,clientsocket,lastMSG):
        '''
        read the data from a socket and check if the endmarker set
        
        client socket: network socket of the communication
        
        exception: raise a exception if a error in the communication
        '''
        revData=lastMSG
        try:
            finish=False
            while True:
                data = clientsocket.recv(BUFFER)
                revData=revData+data
                if self.__ENDMARKER in revData or not data:
                    if revData.endswith(self.__ENDMARKER):
                        lastMSG=""
                        revData=revData.replace(self.__ENDMARKER,"")
                        break   
                    if self.__ENDMARKER in revData:
                        (revData,lastMSG)=revData.split(self.__ENDMARKER)
                        break
                    if not data:
                        finish=True
                        break
            return (revData,lastMSG,finish)
        except:
            self.__log.error("error to receive answer from core %s"%(self.__args.get('hostName')),exc_info=True) 
            raise Exception
        
    def __listenToClient(self,clientsocket,address):
        '''
        working client request
        '''
        self.__log.debug("get new client request from %s"%(address))
        lastMSG=""
        finish=False
        while self.running:
            ''' read client data '''
            try:
                (data,lastMSG,finish) = self.__readClientData(clientsocket,lastMSG)
                if not data and finish:
                    break
            except:
                self.__log.error("error while fetching data from %s"%(address),exc_info=True)
                self.__sendAnwser(clientsocket,self.__coreProtocol.decrypt('result',{'result':"error"}))
                continue
            ''' decode client data '''
            try:
                (user,password,calling,args)=self.__coreProtocol.uncrypt(data)
            except:
                self.__sendAnwser(clientsocket,self.__coreProtocol.decrypt('result',{'result':"error"}))
                continue
            ''' check user and passer an allow function '''
            if not self.__allowCredential(user, password, clientsocket): break
            if not self.__allowFunction(calling, clientsocket): continue
            ''' try to call the function '''
            self.__log.info("try to call function: %s"%(calling))
            try:
                method_to_call = getattr(self.__core,calling)
                funcArgs=method_to_call(*args)
                self.__log.debug("send success")
                self.__sendAnwser(clientsocket,self.__coreProtocol.decrypt('result',{'result':"success"}))
            except:
                self.__log.error("error function: %s"%(calling),exc_info=True)
                self.__sendAnwser(clientsocket,self.__coreProtocol.decrypt('result',{'result':"error"}))
                continue 
            if finish:
                break              
        self.__log.debug("end of communication")  
        self.__closeSocket(clientsocket)       
                
    def __allowCredential(self,user,password,clientsocket):
        if user<>self.__args.get('user') or password<>self.__args.get('password'):
            self.__log.error("user or password error: %s is not allow"%(user))
            self.__sendAnwser(clientsocket,self.__coreProtocol.decrypt('result',{'result':"error"}))
            return False
        return True            
    
    def __allowFunction(self,function,clientsocket):
        if function in self.__allowFunktions:
            self.__log.debug("function: %s allow"%(function))
            return True
        else:
            self.__log.error("function: %s not allow"%(function))
            self.__sendAnwser(clientsocket,self.__coreProtocol.decrypt('result',{'result':"error"}) )
            return False            
        
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
                self.__log.debug("close socket server")
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
        if self.__socket: return self.__socket
           
        self.__log.debug("try to build socket ip:%s:%s"%(self.__args.get('ip'),self.__args.get('port')))
        try:
            self.__socket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((self.__args.get('ip'),int(self.__args.get('port'))))
            self.__socket.setblocking(0)
            self.__socket.listen(20)
            self.__unblockServer()
            self.__log.info("socket ip:%s:%s is ready"%(self.__args.get('ip'),self.__args.get('port')))
        except :
            self.__blockServer()
            self.__socket=False
            self.__log.error("can not build socket ip:%s:%s"%(self.__args.get('ip'),self.__args.get('port')),exc_info=True)
        return self.__socket    