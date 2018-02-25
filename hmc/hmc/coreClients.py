'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "3.0"



from hmc import socketClient
import threading

class coreClients(object):
    
    def updateCoreClient(self,coreName,coreCFG,forceUpdate=False):
        '''
        update a core connector as server or client. if the client
        exists it will be stop and delete. the sync status is save 
        and set to the new client
        corename=the corename of the client (name@hostname)
        args:{
                    "hostName":"raspberry1",
                    "enable":true,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        syncStatus true/fals if true it set the status to the core to is sync
        '''
        try:
            self.logger.info("try to update core sync server")
            threading.Thread(target=self.__updateClient,args = (coreName,coreCFG,forceUpdate)).start()
        except:
            self.logger.error("can not update core sync server",exc_info=True)
            raise 
        
    def __updateClient(self,coreName,coreCFG,forceUpdate=False):
        try:
            if self.coreClientsCFG.get(coreName,False)==coreCFG:
                self.logger.info("%s core have same config, nothing to do"%(coreName))
                return
            syncStatus=False
            if coreName in self.CoreClientsConnections:                    
                syncStatus=self.CoreClientsConnections[coreName]['instance'].getSyncStatus()
                self.CoreClientsConnections[coreName]['instance'].busyoutClient()
            self.__deleteCoreClient(coreName)
            self.__buildCoreClient(coreName, coreCFG, syncStatus)
            self.updateRemoteCore(forceUpdate,coreName,'updateCoreClient',coreName,coreCFG)   
        except:
            self.logger.error("can not update remote core %s"%(coreName))    
    
    def __deleteCoreClient(self,coreName):
        try:
            if coreName in self.CoreClientsConnections[coreName]:
                self.logger.error("delete core Client %s"%(coreName)) 
                coreClient= self.CoreClientsConnections[coreName]['instance']
                coreClient.shutdown()
                del self.CoreClientsConnections[coreName]
            if coreName in self.coreClientsCFG:
                del self.coreClientsCFG[coreName]
        except:
            self.logger.error("can not delete remote core %s"%(coreName))
        
    def deleteCoreClient(self,coreName,forceUpdate=False):
        try:
            self.__deleteCoreClient(coreName) 
            self.updateRemoteCore(forceUpdate,coreName,'deleteCoreClient',coreName)       
        except:
            self.logger.error("can not delete remote core %s"%(coreName))
        
    def restoreCoreClient(self,coreName,args,syncStatus=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        args:{
                    "hostName":"raspberry1",
                    "enable":true,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        syncStatus true/false if true it set the status to the core to is sync
        '''
        try:
            self.__buildCoreClient(coreName,args,syncStatus)
        except:
            self.logger.error("can not restore core sync server %s"%(coreName),exc_info=True)
            raise Exception
        
    def addCoreClient(self,coreName,args,forceUpdate=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        args:{
                    "hostName":"raspberry1",
                    "enable":true,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        syncStatus true/false if true it set the status to the core to is sync
        '''
        try:
            self.__buildCoreClient(coreName,args)
            self.updateRemoteCore(forceUpdate,coreName,'addCoreClient',args)
        except:
            self.logger.error("can not add core coreclient %s"%(coreName),exc_info=True)
            raise Exception             
        
    def __buildCoreClient(self,coreName,coreCFG,syncStatus=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        
        syncStatus true/false if true it set the status to the core to is sync
        '''
        gatewayConfig={
                    "hostName":self.args['global']['host'],
                    "socketTimeout":8,
                    "enable":False,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        self.logger.info("try to add core client %s"%(coreName))
        gatewayConfig.update(coreCFG)
        try:
            if gatewayConfig['enable']==True:
                if self.eventHome(coreName):
                    self.logger.info("core client %s is this server, ignore"%(coreName))      
                else:
                    '''
                    start core Client
                    '''
                    self.logger.info("core client %s is build"%(coreName))
                    coreClient={
                        "instance":None,
                        "running":False, 
                        "syncStatus":syncStatus
                        } 
                    coreClient['instance']=socketClient.CoreConnection(gatewayConfig,self)
                    if coreClient['syncStatus']:
                        coreClient['instance'].setSyncStatus(syncStatus)
                    coreClient['instance'].daemon=True
                    coreClient['instance'].start() 
                    coreClient['running']=True
                    self.CoreClientsConnections[coreName]=coreClient
                    
            else:
                self.logger.info("core Client %s is disable"%(gatewayConfig['hostName']))  
        except:
            self.logger.error("can not start core Client",exc_info=True)
        self.coreClientsCFG[coreName]=gatewayConfig  
        
    def updateRemoteCore(self,forceUpdate,deviceID,calling,*args): 
        if not forceUpdate:
            if not self.eventHome(deviceID):
                return           
        for coreName in self.CoreClientsConnections:
            try:
                if self.CoreClientsConnections[coreName]['running']:
                    coreClient=self.CoreClientsConnections[coreName]['instance']
                    coreClient.updateCore(deviceID,calling,args)
                    self.logger.debug("store in remote Core queue: %s success"%(coreName))
                else:
                    self.logger.error("core client %s is not running"%(coreName))
            except:
                self.logger.error("can not update core Client queue: %s"%(coreName),exc_info=True)          

