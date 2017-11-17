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
        self.log("info","try to add core sync server")
        try:
            if args['enable']:
                if args['hostName']==self.args['global']['host']:
                    '''
                    start core Server
                    '''
                    self.ConnectorServer= socketServer.server(args,self,self.logger)
                    self.ConnectorServer.daemon=True
                    self.ConnectorServer.start()        
                else:
                    '''
                    start core Client
                    '''  
                    self.CoreClientsConnections[coreName]=socketClient.CoreConnection(args,self,self.logger)
                    self.CoreClientsConnections[coreName].daemon=True
                    self.CoreClientsConnections[coreName].start()   
            else:
                self.log("info","core Client %s is disable"%(args['hostName']))  
        except:
            self.log("error","can not start core %s"%(args['hostName']))
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Trace back Info: %s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
        self.coreClientsCFG[coreName]=args  
        
    def updateRemoteCore(self,force,deviceID,calling,*args): 
        if not force:
            if not self.eventHome(deviceID):
                return           
        for coreName in self.CoreClientsConnections:
            ("debug","try to update remote Core: %s"%(coreName))            
            try:
                self.CoreClientsConnections[coreName].updateCore(deviceID,calling,*args)
                self.log("debug","update remote Core: %s success"%(coreName))
            except:
                self.log("error","can not update remote Core: %s"%(coreName))          

