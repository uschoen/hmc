'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "3.0"



from hmc import socketServer
from hmc import socketClient
import threading

class coreConnector(object):
    
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
            if coreName in self.coreClientsCFG:
                if self.coreClientsCFG.get(coreName)==coreCFG:
                    self.logger.info("%s core have same config, nothing to do"%(coreName))
                    return
                if coreCFG.get('enable',False):
                    threading.Thread(target=self.__stopAndDeleteClient,args = (coreName,coreCFG,forceUpdate)).start()
        except:
            self.logger.error("can not update core sync server",exc_info=True)
            raise     
    
    def __stopAndDeleteClient(self,coreName,coreCFG,forceUpdate=False):
        try:
            syncStatus=False
            if  self.eventHome(coreName):
                '''
                coreServer
                '''
                self.deleteCoreClient(coreName,forceUpdate)  
            else:
                '''
                coreClient
                '''
                syncStatus=self.CoreClientsConnections[coreName].getSyncStatus()
                self.CoreClientsConnections[coreName].busyoutClient()
                self.deleteCoreClient(coreName,forceUpdate)   
            self.__buildCoreClient(coreName,coreCFG,syncStatus)
            self.updateRemoteCore(forceUpdate,coreName,'updateCoreClient',coreName,coreCFG)
        except:
            self.logger.error("can not update remote core %s"%(coreName))    
    
    def deleteCoreClient(self,coreName,forceUpdate=False):
        try:
            self.logger.error("delete core %s"%(coreName)) 
            if  self.eventHome(coreName):
                self.ConnectorServer[coreName].shutdown() 
                del self.ConnectorServer[coreName] 
            else:
                self.CoreClientsConnections[coreName].shutdown()
                del self.CoreClientsConnections[coreName]
            del self.coreClientsCFG[coreName]
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
            self.__buildCoreClient(coreName,args)
        except:
            self.logger.error("can not restore core sync server %s"%(coreName),exc_info=True)
            raise Exception
    
    def addCoreClient(self,coreName,args):
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
            self.updateRemoteCore(False,coreName,'addCoreClient',args)
        except:
            self.logger.error("can not restore core sync server %s"%(coreName),exc_info=True)
            raise Exception          
        
    def __buildCoreClient(self,coreName,args,syncStatus=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        args:{
                    "hostName":"raspberry1",
                    "socketTimeout":8
                    "enable":true,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        syncStatus true/false if true it set the status to the core to is sync
        '''
        self.logger.info("try to add core sync server %s"%(coreName))
        args['hostName']=coreName
        try:
            if args['enable']==True:
                if self.eventHome(coreName):
                    '''
                    start core Server
                    '''
                    self.logger.info("core %s is sync server "%(coreName))
        
                    self.ConnectorServer[coreName]=socketServer.server(args,self)
                    self.ConnectorServer[coreName].daemon=True
                    self.ConnectorServer[coreName].start()        
                else:
                    '''
                    start core Client
                    '''
                    self.logger.info("core %s is sync client "%(coreName))  
                    self.CoreClientsConnections[coreName]=socketClient.CoreConnection(args,self)
                    if syncStatus:
                        self.CoreClientsConnections[coreName].setSyncStatus(syncStatus)
                    self.CoreClientsConnections[coreName].daemon=True
                    self.CoreClientsConnections[coreName].start()   
            else:
                self.logger.info("core Client %s is disable"%(args['hostName']))  
        except:
            self.logger.error("can not start core",exc_info=True)
        self.coreClientsCFG[coreName]=args  
        
        
    def updateRemoteCore(self,force,deviceID,calling,*args): 
        if not force:
            if not self.eventHome(deviceID):
                return           
        for coreName in self.CoreClientsConnections:
            try:
                self.CoreClientsConnections[coreName].updateCore(deviceID,calling,args)
                self.logger.debug("store in remote Core queue: %s success"%(coreName))
            except:
                self.logger.error("can not store remote Core queue: %s"%(coreName),exc_info=True)          

