'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "2.0"



import sys,os
from hmc import socketServer
from hmc import socketClient

class coreConnector(object):
    
    def updateCoreClient(self,coreName,args):
        self.logger.info("try to update core sync server")
        if coreName in self.coreClientsCFG:
            self.logger.info("%s core is exsiting,stopping end delte"%(coreName))
            if args['enable']:
                if args['hostName']==self.args['global']['host']:
                    self.ConnectorServer[coreName].shutdown() 
                    del self.ConnectorServer[coreName]
                else:
                    self.CoreClientsConnections[coreName].shutdown()
                    del self.CoreClientsConnections[coreName]
            '''delte configuration'''
            del self.coreClientsCFG[coreName] 
        ''' add core client '''
        self.addCoreClient(coreName,args)    
        
    def addCoreClient(self,coreName,args):
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
                    self.CoreClientsConnections[coreName].daemon=True
                    self.CoreClientsConnections[coreName].start()   
            else:
                self.logger.info("core Client %s is disable"%(args['hostName']))  
        except:
            self.logger.error("can not start core %s"%(args['hostName']),exc_info=True)
        self.coreClientsCFG[coreName]=args  
        
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

