'''
Created on 19.10.2017

@author: uschoen
'''
__version__=3.0


import threading
import logging
import Queue                    #@UnresolvedImport
import time
import socket
import coreProtocol

BUFFER=8192

'''
TODO: 
insert the STARTMARKER to check ! for cleint and server
TODO:
check user and password
TODO:
Change to a HMC Gateway, not as inculudet function
'''

class CoreConnection(threading.Thread): 
    
    
    def __init__(self,params,core):
        threading.Thread.__init__(self)
        
        self.STARTMARKER="!!!<<<start>>>"
        self.ENDMARKER="<<<end>>>!!!"
        
        self.__lastMSG=""
        '''
        if  running true, loop is running
        '''
        self.running=1
        '''
        core instance
        '''
        self.__core=core
        '''
        core client configuration
        '''
        self.__arg={
                    "aes": False, 
                    "enable": False, 
                    "hostName": "unkown-host", 
                    "ip": "127.0.0.1", 
                    "password": "password", 
                    "port": 5091, 
                    "timeout": 50, 
                    "user": "user"}
        self.__arg.update(params)
        '''
        if core sync false/true
        '''
        self.__isCoreSync=False
        '''
        sync Queue, jobs to sync the core        
        '''
        self.__syncQueue=Queue.Queue()
        '''
        sync Queue, jobs from core to core
        '''
        self.__coreQueue=Queue.Queue()
        '''
        block time to block the client
        '''
        self.__blockedTime=0
        '''
        class to build core protocol
        '''
        self.__encodeCoreProtocol=coreProtocol.code(self.__arg['user'],self.__arg['password'],self.__arg['aes'])
        '''
        logger instance
        '''
        self.logger=logging.getLogger(__name__) 
        self.logger.debug("build  "+__name__+" instance")
        self.sendNR=0
    def run(self):
        '''
        client loop
        '''
        self.logger.info("%s start"%(__name__))
        while self.running:
            time.sleep(0.1)
            if self.__blockedTime<int(time.time()):
                self.__coreSync()
                while self.__isCoreSync and self.running:
                    if not self.__coreQueue.empty():
                        try:
                            self.__workJob(self.__coreQueue.get())
                        except:
                            self.logger.error("can not finish coreQueue to core %s"%(self.__arg['hostName'])) 
                            self.__blockClient()
                time.sleep(0.1)   
        self.logger.error("core client to core %s stop"%(__name__))
    
    def getSyncStatus(self):
        '''
        return if core client sync
        '''
        return self.__isCoreSync
    
    def setSyncStatus(self,syncStatus):
        ''' 
        set the core sync status
        '''
        if syncStatus==True or syncStatus==False:
            self.logger.debug("set core client %s sync status to %s"%(self.__arg['hostName'],syncStatus))
            self.__isCoreSync=syncStatus
            
    def updateCore(self,deviceID,calling,arg):
        '''
        ' put a job in the work queue
        '''
        self.logger.info("putting job for deviceID:%s calling:%s into queue"%(deviceID,calling))
        updateObj={
                    'deviceID':deviceID,
                    'calling':calling,
                    'arg':arg}
        self.__coreQueue.put(updateObj)
        if self.__blockedTime<int(time.time()):
            self.logger.info("core client block for %i s"%(self.__blockedTime-int(time.time())))
    
    def __workJob(self,syncJob):
        '''
        send a job to an other core
        syncJob={
                    deviceID: <<deviceId to sync>>,
                    calling: <<function to call>>,
                    arg: <<arguments>>
                }
        '''
        self.logger.info("work job for deviceID %s calling %s"%(syncJob['deviceID'],syncJob['calling']))
        '''
        network connect to core
        '''
        try:
            clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect((self.__arg['ip'],int(self.__arg['port'])))
            self.logger.info("connect to Core %s:%s"%(self.__arg['ip'],self.__arg['port']))
        except socket.error:
            self.logger.error("socket error, can not connect to Core %s:%s"%(self.__arg['ip'],self.__arg['port']))
            raise Exception
        except:
            self.logger.error("can not connect to Core %s:%s"%(self.__arg['ip'],self.__arg['port']),exc_info=True)
            raise Exception
        '''
        convert command to core protocol
        '''
        try:
            socketDataString="%s%s"%(self.__encodeCoreProtocol.decrypt(syncJob['calling'],syncJob['arg']),self.ENDMARKER)
            '''  only for debug
            file = open('log/send.txt','a') 
            file.write('%i %s %s\n'%(self.sendNR,syncJob['calling'],syncJob['arg'])) 
            file.close() 
            self.sendNR=self.sendNR+1 
            self.logger.debug("send:%s"%(corData))
            '''
            self.logger.debug("send message to core")
            clientsocket.sendall(socketDataString)
        except:
            self.logger.error("can not send message to core, sending error",exc_info=True)
            clientsocket.close()
            raise Exception
        '''
        wait for answer from core client
        '''
        try:  
            coreClientAnswer=self.__readClientData(clientsocket)
            clientsocket.close()
            (user,password,calling,args)=self.__encodeCoreProtocol.uncrypt(coreClientAnswer)
            self.logger.debug("calling function:%s user:%s"%(calling,user))
            if args['result']=="success":
                self.logger.debug("result was success")
                return
            else:
                self.logger.info("result was not success") 
                raise Exception    
        except:
            self.logger.error("error in answer from core %s"%(self.__arg['hostName']),exc_info=True) 
            clientsocket.close()
            raise Exception
        
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
                if self.ENDMARKER in revData or not data:
                    if revData.endswith(self.ENDMARKER):
                        self.__lastMSG=""
                        revData=revData.replace(self.ENDMARKER,"")
                        break   
                    if self.ENDMARKER in revData:
                        (revData,self.__lastMSG)=revData.split(self.ENDMARKER)
                        break
                    if not data:
                        self.logger.error("receive no %s data from core %s %s"%(self.ENDMARKER,self.__arg['hostName'],revData))
                        raise Exception
            return revData
        except: 
            self.logger.error("error to receive answer from core %s"%(self.__arg['hostName']),exc_info=True) 
            raise Exception       
                           
    def shutdown(self):
        '''
        shutdown client connection
        '''
        self.running=0  
        self.logger.critical("shutdown core connection to %s"%(self.__arg['hostName']))
    
    def __clearSyncQueue(self):
        '''
        ' clear the sync Queue
        '''
        self.logger.info("clear sync queue")
        self.__syncQueue.queue.clear()
        
    def __clearCoreQueue(self):
        '''
        ' clear the core Queue
        '''
        self.logger.info("clear core queue")
        self.__coreQueue.queue.clear()    
    
    def __coreSync(self):
        '''
        sync core to client
        '''
        self.logger.info("start sync to core %s"%(self.__arg['hostName']))
        self.__clearSyncQueue()
        self.__clearCoreQueue()
        self.__syncCoreEventHandler()
        self.__syncCoreDefaultEventHandler()
        self.__syncCoreDevices()
        self.__syncCoreGateways()
        self.__syncCoreClients()
        while not self.__isCoreSync:
            if self.__syncQueue.empty():
                self.logger.info("nothing to sync to core %s, finish"%(self.__arg['hostName']))
                self.__isCoreSync=True
                break
            try:
                self.__workJob(self.__syncQueue.get())
            except:
                self.logger.error("can not sync to core %s"%(self.__arg['hostName']))
                self.__blockClient()  
                return
        self.__unblockClient()
           
    
    def __syncCoreDevices(self):
        '''
        sync all devices from this host
        '''
        self.logger.info("sync devices to core %s"%(self.__arg['hostName']))
        for deviceID in self.__core.getAllDeviceId():
            if not self.__core.eventHome(deviceID):
                continue
            self.logger.info("sync devicesID %s to core %s"%(deviceID,self.__arg['hostName']))
            device=self.__core.devices[deviceID].getConfiguration()
            args=(device['device'],device['channels'])
            updateObj={
                    'deviceID':deviceID,
                    'calling':'updateDevice',
                    'arg':args}
            self.__syncQueue.put(updateObj)
        
    def __syncCoreGateways(self):
        '''
        sync all gateways events from this host
        '''
        self.logger.info("sync Gateways to core %s"%(self.__arg['hostName']))
        self.logger.info("sync Gateways not implement")
        
    def __syncCoreEventHandler(self):
        '''
        sync all eventHandler from this host
        '''
        self.logger.info("sync EventHandler to core %s"%(self.__arg['hostName']))
        self.logger.info("sync EventHandler not implement")

    def __syncCoreDefaultEventHandler(self):
        '''
        sync all default eventshandler from this host
        '''
        self.logger.info("sync DefaultEventHandler to core %s"%(self.__arg['hostName']))
        self.logger.info("sync DefaultEventHandler not implement")
        
    def __syncCoreClients(self):
        '''
        sync all core clients from this host
        '''
        self.logger.info("sync CoreClients to core %s"%(self.__arg['hostName']))
        for coreName in self.__core.coreClientsCFG:
            if not self.__core.eventHome(coreName):
                continue
            args=(coreName,self.__core.coreClientsCFG[coreName])
            updateObj={
                        'deviceID':coreName,
                        'calling':'updateCoreClient',
                        'arg':args}
            self.__syncQueue.put(updateObj)
        
    def __syncCoreDefaultEvent(self):
        '''
        sync all default events from this host
        '''
        self.logger.info("sync DefaultEvent to core %s"%(self.__arg['hostName']))
        self.logger.info("sync DefaultEvent not implement")
    
    def __blockClient(self,timer=False):
        '''
        block connection to client for x sec
        timer: sec to block
        if timer false, use time from configuration file
        and set sync to false
        ''' 
        if not timer:
            timer=self.__arg['timeout']
        self.logger.info("block core client to core %s for %i s"%(self.__arg['hostName'],timer))
        self.__blockedTime=int(time.time()+timer)
        self.__isCoreSync=False
        
    def __unblockClient(self):
        '''
        unblock core client
        '''
        if self.__blockedTime==0:
            return
        self.logger.info("unblock core Client to client %s"%(self.__arg['hostName']))
        self.__blockedTime=0