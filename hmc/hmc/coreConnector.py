'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "2.0"



import sys,os
from hmc import socketServer
from hmc import socketClient

class coreConnector(object):
    
    
    
    
    def addCoreClient(self,coreName,args):
        self.logger.info("try to add core sync server")
        try:
            if args['enable']:
                if args['hostName']==self.args['global']['host']:
                    '''
                    start core Server
                    '''
                    self.ConnectorServer= socketServer.server(args,self)
                    self.ConnectorServer.daemon=True
                    self.ConnectorServer.start()        
                else:
                    '''
                    start core Client
                    '''  
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

