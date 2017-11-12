'''
Created on 23.09.2017

@author: uschoen
'''
__version__=0.2

from gateways import *
import importlib,sys,os

class coreGateways():
    '''
    classdocs
    '''
    def getGatewaysName(self):
        gateways=[]
        self.log("debug","give gateways names back")
        for gatewayName in self.gatewaysInstance:
            gateways.append(self.gatewaysInstance[gatewayName])
        self.log("debug","give %s gateways names back"%(len(gateways)))
        return gateways
    
    def getGatewaysInstance(self,gatewayName):
        '''
        return the Instance of a gateways
        getGatewaysInstance(<<Name of the Gateways >>)
        return: Object 
        '''
        if  gatewayName in  self.gatewaysInstance:
            return self.gatewaysInstance[gatewayName]['instance']
        else:
            self.log("error","gateway instance %s not found"%(gatewayName))
            return False
           
    def addGateway(self,gatewayName,config):
        self.log("info","add gateway %s"%(gatewayName))
        if self.eventHome(gatewayName): 
            pakage="gateways.%s.%s"%(config['pakage'],config['modul'])
            self.log("info","try to load gateway: %s  with pakage: %s"%(gatewayName,pakage))
            tempconfig=config['config']
            tempconfig.update(self.args['global'])
            ARGUMENTS = (tempconfig,self,self.logger)  
            try:
                module = importlib.import_module(pakage)
                CLASS_NAME = config['class']
                self.gatewaysInstance[gatewayName]={}
                self.gatewaysInstance[gatewayName]['name']=gatewayName
                self.gatewaysInstance[gatewayName]['status']="stop"
                self.gatewaysInstance[gatewayName]['instance'] = getattr(module, CLASS_NAME)(*ARGUMENTS)
                self.gatewaysInstance[gatewayName]['instance'].daemon = True
                self.gatewaysInstance[gatewayName]['enable']=config['enable']
                if config['enable']:
                    self.log("info","start gateway %s"%(gatewayName))
                    self.startGateway(gatewayName)
                else:
                    self.log("info","gateway %s is disable"%(gatewayName)) 
                self.updateRemoteCore(gatewayName,'addGateway',gatewayName,config)
                self.gatewaysCFG[gatewayName]=config 
            except :
                self.log("error",sys.exc_info())
                tb = sys.exc_info()
                for msg in tb:
                    self.log("error","Traceback Info:" + str(msg)) 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno)) 
                self.gatewaysCFG[gatewayName]=config
                raise Exception
        
    def startGateway(self,gatewayName):
        try:
            self.gatewaysInstance[gatewayName]['instance'].start()
            self.gatewaysInstance[gatewayName]['status']="start"
        except:
            self.log("error","can not start ateways%s "%(gatewayName))
            self.gatewaysInstance[gatewayName]['status']="stop"
    def shutdownAllGateways(self):
        for gatewayName in self.gatewaysInstance:   
                self.log("emergency","shutdown gateways %s"%(gatewayName))
                self.stopGateway(gatewayName)
    def stopGateway(self,gatewayName):
        self.gatewaysInstance[gatewayName]['instance'].running=0
        self.gatewaysInstance[gatewayName]['instance'].shutdown()
        self.gatewaysInstance[gatewayName]['status']="stop"
        pass
    
    
    
    