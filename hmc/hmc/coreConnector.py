'''
Created on 28.01.2017

@author: uschoen
'''
__version__ = "2.0"



import sys,os
from hmc import socketServer
from hmc import socketClient





class coreConnector(object):
    def startCoreConnector(self):
        self.log("info","try to start core lissener")
        if self.args['connector']['enable']:
            
            try:
                self.ConnectorServer= socketServer.server(self.args['connector'],self,self.logger)
                self.ConnectorServer.daemon=True
                self.ConnectorServer.start()
                self.log("info","start core socket server success full")
            except :
                self.log("error",sys.exc_info())
                tb = sys.exc_info()
                for msg in tb:
                    self.log("error","Traceback Info: %s"%(msg)) 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            '''
            building core connector
            '''
            for coreName in self.args['syncCore']:
                if not self.args['syncCore'][coreName]['enable']:
                    continue
                self.log("info","build core client %s"%(coreName))
                argsClient=self.args['syncCore'][coreName]
                argsClient['coreName']=coreName
                self.addCoreClient(coreName,argsClient)
        else:
            self.log("info","core server connector disable")      
    def addCoreClient(self,coreName,args):
        try: 
            self.CoreConnections[coreName]=socketClient.CoreConnection(args,self,self.logger)
        except:
            self.log("error","can not build coreClient %s"%(coreName))
            
    def updateRemoteCore(self,deviceID,calling,*args): 
        if not self.eventHome(deviceID):
            return               
        for CoreName in self.CoreConnections:
            try:
                self.CoreConnections[CoreName].updateCore(calling,*args)
            except:
                self.log("error","can not update remote Core: %s"%(CoreName)) 
                

