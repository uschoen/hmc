'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "3.0"



from hmc import socketServer
from hmc import socketClient

class coreConnector(object):
    
    def updateCoreClient(self,coreName,args):
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
        self.logger.info("try to update core sync server")
        syncStatus=False
        if coreName in self.coreClientsCFG:
            self.logger.info("%s core is exsiting,stopping end delte"%(coreName))
            if args['enable']:
                if args['hostName']==self.args['global']['host']:
                    self.ConnectorServer[coreName].shutdown() 
                    del self.ConnectorServer[coreName]
                else:
                    syncStatus=self.CoreClientsConnections[coreName].getSyncStatus()
                    self.CoreClientsConnections[coreName].shutdown()
                    del self.CoreClientsConnections[coreName]
            '''delte configuration'''
            del self.coreClientsCFG[coreName] 
        ''' add core client '''
        self.addCoreClient(coreName,args,syncStatus)    
        
    def addCoreClient(self,coreName,args,syncStatus=False):
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
        syncStatus true/fals if true it set the status to the core to is sync
        '''
        self.logger.info("try to add core sync server %s"%(coreName))
        try:
            if args['enable']:
                if args['hostName']==self.args['global']['host']:
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
            self.logger.error("can not start core %s"%(args['hostName']),exc_info=True)
        self.coreClientsCFG[coreName]=args  
        self.updateRemoteCore(False,coreName,'addCoreClient',args,syncStatus)
        
    def updateRemoteCore(self,force,deviceID,calling,*args): 
        if not force:
            if not self.eventHome(deviceID):
                return           
        for coreName in self.CoreClientsConnections:
            ("debug","try to update remote Core: %s"%(coreName))            
            try:
                self.CoreClientsConnections[coreName].updateCore(deviceID,calling,args)
                self.logger.debug("update remote Core: %s success"%(coreName))
            except:
                self.logger.error("can not update remote Core: %s"%(coreName),exc_info=True)          

