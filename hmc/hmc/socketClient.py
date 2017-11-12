'''
Created on 19.10.2017

@author: uschoen
'''

import socket,threading,os,sys,copy
from time import localtime, strftime,sleep,time
from datetime import datetime
import coreProtokoll

class CoreConnection(threading.Thread): 
    def __init__(self, params,core,logger=False):
        threading.Thread.__init__(self)
        self.__core=core
        self.__arg=params
        self.__logger=logger
        self.running=1
        self.blockedTime=0
        self.queue={}
        self.syncQueue={}
        self.coreDataobj=coreProtokoll.code(self.__arg['user'],self.__arg['password'],self.__logger)
        self.sync=False
        self.__newQueue=False
        self.log("debug","build  "+__name__+" instance")
    
    def run(self):
        self.log("info %s start"%(__name__))
        while self.running:
            if not self.sync:
                self.syncAllCoreConfiguration()
            if self.blockedTime>time():
                self.log("warning","Core %s is blocked,wait for %i s "%(self.__arg['hostName'],self.blockedTime-time()))
                sleep(self.blockedTime-time())
                continue
            if len(self.queue)>0:
                self.log("info","find %i jobs in queue for core %s"%(len(self.queue),self.__arg['hostName'])) 
                try:
                    self.workQueue(copy.deepcopy(self.queue))
                except:
                    self.log("error","some job in queue for core %s has an error"%(self.__arg['hostName']))
            if self.__newQueue:
                continue
            sleep(0.2)
        self.log("info", __name__+" stop:")
    
    def workQueue(self,queue,syncQueue=False):
        self.log("info","work queue with %i items, for core %s"%(len(queue),self.__arg['hostName']))
        for queueEntry in queue:
            '''
            open socket
            '''
            try:
                coreSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                coreSocket.connect((self.__arg['ip'],int(self.__arg['port'])))
                self.log("info","connect to Core %s:%s"%(self.__arg['ip'],self.__arg['port']))
            except:
                self.log("error","can not connect to Core %s:%s , socket error"%(self.__arg['ip'],self.__arg['port']))
                self.__blockClient()
                raise 
            '''
            send message to core
            '''
            try:
                corData=self.coreDataobj.decode(queue[queueEntry]['calling'],queue[queueEntry]['arg'])
                self.log("debug","send message to core: %s"%(corData))
                coreSocket.sendall(corData)
                if syncQueue:
                    del self.syncQueue[queueEntry]
                else:
                    del self.queue[queueEntry]
                self.__newQueue=False
                self.__unblockClient()
                self.log("debug","send message success")
            except:
                self.log("error","can not send message to core %s, sending error"%(corData))
                self.__blockClient()
                coreSocket.close()
                raise
            '''
            wait for answer
            ''' 
            try:  
                self.listenToClient(coreSocket)
                coreSocket.close()
                self.log("debug","socket close to core")    
            except: 
                self.log("error","no answer from core %s"%(self.__arg['hostName'])) 
                
    def listenToClient(self,coreSocket):
        size = 1024
        while True:
            try:
                data = coreSocket.recv(size)
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
    
    def __syncCore(self,deviceID,calling,*arg):
        self.log("info","putting job for deviceID %s into sync queue"%(deviceID))
        queueID="%s%s"%(deviceID,calling)
        updateObj={
                    'deviceID':deviceID,
                    'calling':calling,
                    'arg':arg}
        self.syncQueue[queueID]=updateObj           
                   
    def updateCore(self,deviceID,calling,*arg):
        self.log("info","putting job for deviceID %s into queue"%(deviceID))
        queueID="%s%s"%(deviceID,calling)
        updateObj={
                    'deviceID':deviceID,
                    'calling':calling,
                    'arg':arg}
        self.queue[queueID]=updateObj
        self.__newQueue=True
    
    '''
    sync section
    '''
    def syncAllCoreConfiguration(self):
        self.log("info","start sync to core %s"%(self.__arg['hostName']))
        self.__clearSyncQueue()
        try:
            self.__syncCoreEventHandler()
            self.__syncCoreDefaultEventHandler()
            self.__syncCoreDevices()
            self.__syncCoreGateways()
            self.__syncCoreClients()
            self.workQueue(copy.deepcopy(self.syncQueue),True)
            self.sync=True
            self.__unblockClient()
            self.log("info","finish sync to core %s"%(self.__arg['hostName']))
            self.__clearSyncQueue()
        except:
            self.log("error","can not sync to core %s"%(self.__arg['hostName']))
            self.__blockClient()
            self.__clearSyncQueue()
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:%s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            
    def __clearSyncQueue(self):
        self.log("debug","clear sync queue")
        self.syncQueue={}  
           
    def __syncCoreDevices(self):
        try:
            self.log("info","sync Devices to core %s"%(self.__arg['hostName']))
            for deviceID in self.__core.getAllDeviceId():
                if not self.__core.eventHome(deviceID):
                    continue
                self.log("info","sync DevicesID %s to core %s"%(deviceID,self.__arg['hostName']))
                device=self.__core.devices[deviceID].getConfiguration()
                self.__syncCore(deviceID,'updateDevice',device)
        except:
            self.log("error","can not sync Devices to core %s"%(self.__arg['hostName']))
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:%s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            raise Exception
        
    def __syncCoreGateways(self):
        self.log("info","sync Gateways to core %s"%(self.__arg['hostName']))
        try:
            self.log("info","not implement")
        except:
            self.log("error","can not sync Gateways to core %s"%(self.__arg['hostName']))
            raise Exception
         
    def __syncCoreEventHandler(self):
        try:
            self.log("info","sync EventHandler to core %s"%(self.__arg['hostName']))
            self.log("info","not implement")
        except:
            self.log("info","can not sync EventHandler to core %s"%(self.__arg['hostName']))
            raise Exception
        
    def __syncCoreDefaultEventHandler(self):
        try:
            self.log("info","sync DefaultEventHandler to core %s"%(self.__arg['hostName']))
            self.log("info","not implement")
        except:
            self.log("error","can not sync DefaultEventHandler to core %s"%(self.__arg['hostName']))
            raise Exception
        
    def __syncCoreClients(self):
        try:
            self.log("info","sync CoreClients to core %s"%(self.__arg['hostName']))
            self.log("info","not implement")
        except:
            self.log("error","can not sync coreClients to core %s"%(self.__arg['hostName']))
            raise Exception
        
    def __syncCoreDefaultEvent(self):
        try:
            self.log("info","sync DefaultEvent to core %s"%(self.__arg['hostName']))
            self.log("info","not implement")
        except:
            self.log("error","can not sync DefaultEvent to core %s"%(self.__arg['hostName']))
            raise Exception
       
    def shutdown(self):
        self.running=0  
        self.log("info","close core connection")
     
    def __blockClient(self,timer=False):
        if not timer:
            timer=self.__arg['timeout']
        self.log("info","set core client %s for %i s to block"%(self.__arg['hostName'],timer))
        self.blockedTime=time()+timer
        self.sync=False
        
    def __unblockClient(self):
        self.log("info","unblock Client %s"%(self.__arg['hostName']))
        self.blockedTime=0
           
    def log (self,level="unkown",messages="no messages"):
        if self.__logger:
            dt = datetime.now()
            conf={}
            conf['package']="%s.%s"%(__name__,self.__arg['hostName'])
            conf['level']=level
            conf['messages']=messages
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.__logger.write(conf) 


    