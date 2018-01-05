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
        self.logger.debug("give gateways names back")
        for gatewayName in self.gatewaysInstance:
            gateways.append(self.gatewaysInstance[gatewayName])
        self.logger.debug("give %s gateways names back"%(len(gateways)))
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
            self.logger.error("gateway instance %s not found"%(gatewayName))
            return False
           
    def addGateway(self,gatewayName,config):
        self.logger.info("add gateway %s"%(gatewayName))
        if self.eventHome(gatewayName): 
            pakage="gateways.%s.%s"%(config['package'],config['modul'])
            self.logger.info("try to load gateway: %s  with package: %s"%(gatewayName,pakage))
            tempconfig=config['config']
            tempconfig['package']=config['package']
            tempconfig.update(self.args['global'])
            ARGUMENTS = (tempconfig,self)  
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
                    self.logger.info("start gateway %s"%(gatewayName))
                    self.startGateway(gatewayName)
                else:
                    self.logger.info("gateway %s is disable"%(gatewayName)) 
                self.updateRemoteCore(False,gatewayName,'addGateway',gatewayName,config)
                self.gatewaysCFG[gatewayName]=config 
            except :
                self.logger.critical("can not build gateways %s"%(gatewayName),exc_info=True)
                self.gatewaysCFG[gatewayName]=config
                raise Exception
        else:
            self.logger.error("no right pattern for Gateways %s"%(gatewayName))
            self.gatewaysCFG[gatewayName]=config 
            
    def startGateway(self,gatewayName):
        try:
            self.gatewaysInstance[gatewayName]['instance'].start()
            self.gatewaysInstance[gatewayName]['status']="start"
        except:
            self.logger.error("can not start gateways%s "%(gatewayName),exc_info=True)
            self.gatewaysInstance[gatewayName]['status']="stop"
    def shutdownAllGateways(self):
        for gatewayName in self.gatewaysInstance:   
                self.stopGateway(gatewayName)
    def stopGateway(self,gatewayName):
        self.logger.critical("shutdown gateways %s and wait 5 sec."%(gatewayName))
        self.gatewaysInstance[gatewayName]['instance'].shutdown()
        if self.gatewaysInstance[gatewayName]['instance'].isAlive():
            self.gatewaysInstance[gatewayName]['instance'].join(5)
        self.gatewaysInstance[gatewayName]['status']="stop"
        pass
    
    
    
    