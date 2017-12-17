'''
Created on 19.10.2017

@author: uschoen
'''

import socket,threading,copy,logging
from time import sleep,time
import coreProtokoll

class CoreConnection(threading.Thread): 
    def __init__(self,params,core):
        threading.Thread.__init__(self)
        self.__core=core
        self.__arg=params
        self.logger=logging.getLogger(__name__) 
        self.running=1
        self.blockedTime=0
        self.queue={}
        self.syncQueue={}
        self.coreDataobj=coreProtokoll.code(self.__arg['user'],self.__arg['password'])
        self.sync=False
        self.__newQueue=False
        self.logger.debug("build  "+__name__+" instance")
    
    def run(self):
        self.logger.info("%s start"%(__name__))
        while self.running:
            if not self.sync:
                self.syncAllCoreConfiguration()
            if self.blockedTime>time():
                self.logger.warning("Core %s is blocked,wait for %i s "%(self.__arg['hostName'],self.blockedTime-time()))
                sleep(self.blockedTime-time())
                continue
            if len(self.queue)>0:
                self.logger.info("find %i jobs in queue for core %s"%(len(self.queue),self.__arg['hostName'])) 
                try:
                    self.workQueue(copy.deepcopy(self.queue))
                except:
                    self.logger.error("some job in queue for core %s has an error"%(self.__arg['hostName']))
            if self.__newQueue:
                continue
            sleep(0.2)
        self.logger.info( __name__+" stop:")
    
    def workQueue(self,queue,syncQueue=False):
        self.logger.info("work queue with %i items, for core %s"%(len(queue),self.__arg['hostName']))
        for queueEntry in queue:
            '''
            open socket
            '''
            try:
                coreSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                coreSocket.connect((self.__arg['ip'],int(self.__arg['port'])))
                self.logger.info("connect to Core %s:%s"%(self.__arg['ip'],self.__arg['port']))
            except:
                self.logger.error("can not connect to Core %s:%s , socket error"%(self.__arg['ip'],self.__arg['port']),exc_info=True)
                self.__blockClient()
                raise 
            '''
            send message to core
            '''
            try:
                corData=self.coreDataobj.decrypt(queue[queueEntry]['calling'],queue[queueEntry]['arg'])
                self.logger.debug("send message to core")
                coreSocket.sendall(corData)
                if syncQueue:
                    del self.syncQueue[queueEntry]
                else:
                    del self.queue[queueEntry]
                self.__newQueue=False
                self.__unblockClient()
                self.logger.debug("send message success")
            except:
                self.logger.error("can not send message to core, sending error",exc_info=True)
                self.__blockClient()
                coreSocket.close()
                raise
            '''
            wait for answer
            ''' 
            try:  
                self.listenToClient(coreSocket)
                coreSocket.close()
                self.logger.debug("socket close to core")    
            except: 
                self.logger.error("no answer from core %s"%(self.__arg['hostName']),exc_info=True) 
                
    def listenToClient(self,coreSocket):
        size = 1024
        while True:
            try:
                data = coreSocket.recv(size)
                if data:
                    (user,password,calling,args)=self.coreDataobj.uncrypt(data)
                    self.logger.debug("calling function:%s user:%s"%(calling,user))
                    self.logger.debug("args %s"%(args))
                    if args['result']=="success":
                        self.logger.debug("result was success")
                        break
                    else:
                        self.logger.info("result was not success") 
                        break
                else:
                    self.logger.debug("client disconnected")
                    break
            except:
                self.logger.error("some error in client communication",exc_info=True) 
                self.logger.debug("close client connection")
    
    def __syncCore(self,deviceID,calling,*arg):
        self.logger.info("putting job for deviceID %s into sync queue"%(deviceID))
        queueID="%s%s"%(deviceID,calling)
        updateObj={
                    'deviceID':deviceID,
                    'calling':calling,
                    'arg':arg}
        self.syncQueue[queueID]=updateObj           
                   
    def updateCore(self,deviceID,calling,*arg):
        self.logger.info("putting job for deviceID %s into queue"%(deviceID))
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
        self.logger.info("start sync to core %s"%(self.__arg['hostName']))
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
            self.logger.info("finish sync to core %s"%(self.__arg['hostName']))
            self.__clearSyncQueue()
        except:
            self.logger.error("can not sync to core %s"%(self.__arg['hostName']),exc_info=True)
            self.__blockClient()
            self.__clearSyncQueue()
            
    def __clearSyncQueue(self):
        self.logger.debug("clear sync queue")
        self.syncQueue={}  
           
    def __syncCoreDevices(self):
        try:
            self.logger.info("sync Devices to core %s"%(self.__arg['hostName']))
            for deviceID in self.__core.getAllDeviceId():
                if not self.__core.eventHome(deviceID):
                    continue
                self.logger.info("sync DevicesID %s to core %s"%(deviceID,self.__arg['hostName']))
                device=self.__core.devices[deviceID].getConfiguration()
                self.__syncCore(deviceID,'updateDevice',device)
        except:
            self.logger.error("can not sync Devices to core %s"%(self.__arg['hostName']),exc_info=True)
            raise Exception
        
    def __syncCoreGateways(self):
        self.logger.info("sync Gateways to core %s"%(self.__arg['hostName']))
        try:
            self.logger.info("not implement")
        except:
            self.logger.error("can not sync Gateways to core %s"%(self.__arg['hostName']))
            raise Exception
         
    def __syncCoreEventHandler(self):
        try:
            self.logger.info("sync EventHandler to core %s"%(self.__arg['hostName']))
            self.logger.info("not implement")
        except:
            self.logger.info("can not sync EventHandler to core %s"%(self.__arg['hostName']))
            raise Exception
        
    def __syncCoreDefaultEventHandler(self):
        try:
            self.logger.info("sync DefaultEventHandler to core %s"%(self.__arg['hostName']))
            self.logger.info("not implement")
        except:
            self.logger.error("can not sync DefaultEventHandler to core %s"%(self.__arg['hostName']))
            raise Exception
        
    def __syncCoreClients(self):
        try:
            self.logger.info("sync CoreClients to core %s"%(self.__arg['hostName']))
            self.logger.info("not implement")
        except:
            self.logger.error("can not sync coreClients to core %s"%(self.__arg['hostName']))
            raise Exception
        
    def __syncCoreDefaultEvent(self):
        try:
            self.logger.info("sync DefaultEvent to core %s"%(self.__arg['hostName']))
            self.logger.info("not implement")
        except:
            self.logger.error("can not sync DefaultEvent to core %s"%(self.__arg['hostName']))
            raise Exception
       
    def shutdown(self):
        self.running=0  
        self.logger.info("close core connection")
     
    def __blockClient(self,timer=False):
        if not timer:
            timer=self.__arg['timeout']
        self.logger.info("set core client %s for %i s to block"%(self.__arg['hostName'],timer))
        self.blockedTime=time()+timer
        self.sync=False
        
    def __unblockClient(self):
        self.logger.info("unblock Client %s"%(self.__arg['hostName']))
        self.blockedTime=0
           
    


    