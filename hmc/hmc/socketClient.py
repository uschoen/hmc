'''
Created on 19.10.2017

@author: uschoen
'''

import socket,sys,os,threading
from time import localtime, strftime,time
from datetime import datetime
import coreProtokoll

class CoreConnection(object):
    
    def __init__(self,args,core,logs):
    
        threading.Thread.__init__(self)
        self.logger=logs
        self.core=core
        self.arg=args     
        self.blocked=0
        self.coreDataobj=coreProtokoll.code(self.arg['user'],self.arg['password'],self.logger)
        self.sync=False
        self.coreSocket=False
        self.log("info","build core connection")
        self.syncAllCoreConfiguration()
        
    def syncAllCoreConfiguration(self):
        self.log("info","sync to core %s"%(self.arg['coreName']))
        try:
            self.connectCore()
            self.__syncCoreEventHandler()
            self.__syncCoreDefaultEventHandler()
            self.__syncCoreDevices()
            self.__syncCoreGateways()
            self.sync=True
        except:
            self.log("error","can not sync to core %s"%(self.arg['coreName']))
            self.sync=False
            
    def __syncCoreDevices(self):
        try:
            self.log("info","sync Devices to core %s"%(self.arg['coreName']))
            for deviceID in self.core.getAllDeviceId():
                self.core.updateRemoteCore(deviceID,'updateDevice',self.core.getAllDeviceAttribute(deviceID))
                self.log("info","sync DevicesID %s to core %s"%(deviceID,self.arg['coreName']))
        except:
            self.log("error","can not sync Devices to core %s"%(self.arg['coreName']))
            raise Exception
        
    def __syncCoreGateways(self):
        self.log("info","sync Gateways to core %s"%(self.arg['coreName']))
        try:
            self.log("warning","not implement")
        except:
            self.log("error","can not sync Gateways to core %s"%(self.arg['coreName']))
            raise Exception
         
    def __syncCoreEventHandler(self):
        try:
            self.log("info","sync EventHandler to core %s"%(self.arg['coreName']))
            self.log("warning","not implement")
        except:
            self.log("error","can not sync EventHandler to core %s"%(self.arg['coreName']))
            raise Exception
        
    def __syncCoreDefaultEventHandler(self):
        try:
            self.log("info","sync DefaultEventHandler to core %s"%(self.arg['coreName']))
            self.log("warning","not implement")
        except:
            self.log("error","can not sync DefaultEventHandler to core %s"%(self.arg['coreName']))
            raise Exception
        
    def __syncCoreClients(self):
        try:
            self.log("info","sync CoreClients to core %s"%(self.arg['coreName']))
            self.log("warning","not implement")
        except:
            self.log("error","can not sync coreClients to core %s"%(self.arg['coreName']))
            raise Exception
        
    def __syncCoreDefaultEvent(self):
        try:
            self.log("info","sync DefaultEvent to core %s"%(self.arg['coreName']))
            self.log("warning","not implement")
        except:
            self.log("error","can not sync DefaultEvent to core %s"%(self.arg['coreName']))
            raise Exception
        
    def updateCore(self,calling,*args):
        if self.blocked>time():
            self.log("warning","Core is blocked for %i s"%(self.blocked-time()))
            raise Exception
        try:
            if not self.sync:
                self.syncAllCoreConfiguration()
            threading.Thread(target=self.sendData,args = (self.coreDataobj.decode(calling,args))).start()
            self.log("info","send data in new thread")
        except:
            self.log("error","can not send data")   
            raise Exception
    
    def sendData(self,corData):
        try:
            self.connectCore()
            self.log("debug","send: %s"%(corData))
            self.coreSocket.sendall(corData)
            self.log("debug","send message to core")
            self.listenToClient(self.coreSocket)
            self.closeSocket()
            self.log("debug","socket close to core")
        except:
            self.log("error","can not send message to core")
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:" + str(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            self.closeSocket()
            raise Exception
    
    def closeSocket(self):
        try:
            self.coreSocket.close()    
            self.coreSocket=False
            self.log("debug","close socket")
        except:
            self.log("error","can not close socket")
       
    def listenToClient(self, client):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    (user,password,calling,args)=self.coreDataobj.encode(data)
                    self.log("debug","calling function:%s user:%s"%(calling,user))
                    self.log("debug","args %s"%(args))
                    if args['result']=="success":
                        self.log("debug","result was success")
                        break
                    else:
                        self.log("info","result was not success") 
                        break
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
                self.closeSocket()
                
            

    def connectCore(self):
        try:
            self.coreSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.coreSocket.connect((self.arg['coreIP'],int(self.arg['corePort'])))
            self.log("info","connect to Core %s:%s"%(self.arg['coreIP'],self.arg['corePort']))
        except socket.error:
            self.log("error","can not connect to Core")
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:" + str(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            self.blocked=time()+self.arg['timeout']
            self.closeSocket()
            raise
        except:
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:" + str(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            self.blocked=time()+self.arg['timeout']
            self.closeSocket()
            raise
        
    def reciveData(self):
        self.coreSocket.settimeout(1.0)
        data = self.coreSocket.recv(1024)
        self.coreSocket.settimeout(None)
        
    def shutdown(self):
        self.coreSocket.close()  
        self.log("info","close core connection")
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


    