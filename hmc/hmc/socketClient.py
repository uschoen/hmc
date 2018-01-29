'''
Created on 19.10.2017

@author: uschoen
'''
__version__=3.1


import threading
import logging
import Queue                    #@UnresolvedImport
import time
import socket
import coreProtocol

BUFFER=8192

'''
NOTE:
'''

class CoreConnection(threading.Thread): 
    
    
    def __init__(self,params,core):
        threading.Thread.__init__(self)
        
        ''' end marker for a job '''
        self.__ENDMARKER="<<<end>>>!!!"
        
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
                    "user": "user",
                    "socketTimeout":8}
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
        socket object
        '''
        
        '''
        socket timer 
        '''
        self._socketTimer=0
        '''
        socket status, if true when socket is connect
        '''
        self.__socketConnect=False
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
                    if self._socketTimer<int(time.time()) and self.__socketConnect:
                        self.__socketClose()
                    if not self.__coreQueue.empty():
                        try:
                            self.__workingQueue(self.__coreQueue)
                        except:
                            self.logger.error("can not finish coreQueue to core %s"%(self.__arg['hostName'])) 
                            self.__blockClient()
                            self.__socketClose()
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
        if self.__blockedTime>int(time.time()):
            self.logger.debug("core client block for %i s"%(self.__blockedTime-int(time.time())))
            return
        self.logger.debug("putting job for deviceID:%s calling:%s into queue"%(deviceID,calling))
        updateObj={
                    'deviceID':deviceID,
                    'calling':calling,
                    'arg':arg}
        self.__coreQueue.put(updateObj)
        
    
    def __workingQueue(self,queueList):
        '''
        working a job from a Queue object
        '''
        if queueList.empty():
            ''' nothing do to list is empty '''
            return
        if not self.__socketConnect:
            ''' try to connect '''
            try:
                self.__connectToClient()
            except:
                raise Exception
        ''' working queue list '''
        if queueList.empty():
            return
        try:
            while not queueList.empty():
                self.__sendJob(queueList.get())
            self.__setSocketTimer() 
        except:
            self.logger.info("error in queue",exc_info=True)
            raise Exception        
    
    def __connectToClient(self):
        if self.__socketConnect:
            ''' client is connect '''
            return
        try:
            self.logger.debug("try connect to Core %s:%s"%(self.__arg.get('ip'),self.__arg.get('port')))
            self.__clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__clientSocket.connect((self.__arg.get('ip'),int(self.__arg.get('port'))))
            self.__socketConnect=True
            self.__setSocketTimer()
        except socket.error:
            self.__socketConnect=False
            self.logger.error("socket error, can not connect to Core %s:%s"%(self.__arg.get('ip'),self.__arg.get('port')))
            raise Exception
        except:
            self.__socketConnect=False
            self.logger.error("can not connect to Core %s:%s"%(self.__arg.get('ip'),self.__arg.get('port')),exc_info=True)
            raise Exception
     
    def __setSocketTimer(self):
        self.logger.debug("set socket timer")
        self._socketTimer=self.__arg.get("socketTimeout")+int(time.time())
     
            
    def __sendJob(self,syncJob):
        '''
        send a job to an other core
        syncJob={
                    deviceID: <<deviceId to sync>>,
                    calling: <<function to call>>,
                    arg: <<arguments>>
                }
        '''
        self.logger.debug("work job for deviceID %s calling %s"%(syncJob.get('deviceID'),syncJob.get('calling')))
        '''
        convert command to core protocol
        '''
        try:
            socketDataString="%s%s"%(self.__encodeCoreProtocol.decrypt(syncJob['calling'],syncJob['arg']),self.__ENDMARKER)
            '''  only for debug
            file = open('log/send.txt','a') 
            file.write('%i %s %s\n'%(self.sendNR,syncJob['calling'],syncJob['arg'])) 
            file.close() 
            self.sendNR=self.sendNR+1 
            self.logger.debug("send:%s"%(socketDataString))
            '''
            self.logger.debug("send message to core")
            self.__clientSocket.sendall(socketDataString)
        except:
            self.logger.error("can not send error message to core",exc_info=True)
            raise Exception
        '''
        wait for answer from core client 
        '''
        lastMSG=""
        while self.running:
            ''' read client data '''
            try:
                (data,lastMSG,finish) = self.__readClientData(self.__clientSocket,lastMSG)
                if not data and finish:
                    break
            except:
                self.logger.error("error while fetching data",exc_info=True)
                raise Exception
            ''' decode client data '''
            try:
                (user,password,calling,args)=self.__encodeCoreProtocol.uncrypt(data)
            except:
                self.logger.error("can not uncrypt data from core")
                raise Exception
            if args['result']=="success":
                self.logger.debug("result was success")
                return
            else:
                self.logger.info("result was not success") 
                raise Exception
            
            if finish:
                break                    
    
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
              
    def __socketClose(self):
        '''
        close the socket to the client
        
        fetch the exception
        '''
        self.logger.debug("close socket and socketconnect to false")
        try:
            self.__clientSocket.close()
        except:
            pass
        self.__socketTimer=0 
        self.__socketConnect=False  
                          
    def shutdown(self):
        '''
        shutdown client connection
        '''
        self.running=0 
        self.__socketClose() 
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
        try:
            self.__connectToClient()
        except:
            self.logger.error("can not sync to core %s, no connect"%(self.__arg['hostName']))
            self.__blockClient()  
            self.__socketClose()
            return
        self.__clearSyncQueue()
        self.__clearCoreQueue()
        self.__syncCoreProgram()
        self.__syncCoreDevices()
        self.__syncCoreGateways()
        self.__syncCoreClients()
        while not self.__isCoreSync:
            if self.__syncQueue.empty():
                self.logger.info("nothing to sync to core %s, finish"%(self.__arg['hostName']))
                self.__isCoreSync=True
                break
            try:
                self.__workingQueue(self.__syncQueue)
                self.__socketClose()
                self.__unblockClient()
            except:
                self.logger.error("can not sync to core %s"%(self.__arg['hostName']))
                self.__blockClient()  
                self.__socketClose()
                return
        
           
    
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
            args=(deviceID,device)
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
        for gatewayName in self.__core.gatewaysCFG:
            if not self.__core.eventHome(gatewayName):
                continue
            updateObj={
                    'deviceID':gatewayName,
                    'calling':'updateGateway',
                    'arg':(gatewayName,self.__core.gatewaysCFG[gatewayName])}
            self.__syncQueue.put(updateObj)
        
        
    def __syncCoreProgram(self):
        '''
        sync all program from this host
        '''
        self.logger.info("sync program to core %s"%(self.__arg['hostName']))
        for programName in self.__core.program:
            if not self.__core.eventHome(programName):
                continue
            args=(programName,self.__core.program[programName])
            updateObj={
                        'deviceID':programName,
                        'calling':'updateProgram',
                        'arg':args}
            self.__syncQueue.put(updateObj)
        
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
    
    def __blockClient(self,timer=False):
        '''
        block connection to client for x sec
        timer: sec to block
        if timer false, use time from configuration file
        and set sync to false
        ''' 
        if not timer:
            timer=self.__arg.get('timeout')
            self.__socketClose()
        self.logger.info("block core client to core %s for %i s"%(self.__arg.get('hostName'),timer))
        self.__blockedTime=int(time.time())+timer
        self.__isCoreSync=False
        
    def __unblockClient(self):
        '''
        unblock core client
        '''
        if self.__blockedTime==0:
            return
        self.logger.info("unblock core Client to client %s"%(self.__arg['hostName']))
        self.__blockedTime=0
        