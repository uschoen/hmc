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
    self.gatewaysInstance:
    {
        "gatewayName":{                       # name of the gateways
                        "instance": class,    # class/object/instance of the gateway
                        "status": stop/start, # is thread running or not
                        "enable": True/False  # is gateway enable or not
                        "name": name          # name of the gateways
                     }
    }          
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
        self.gatewaysCFG[gatewayName]=config 
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
        '''
        shutdown all gateways
        '''
        for gatewayName in self.gatewaysInstance:   
            try:
                self.logger.critical("shutdown gateways %s and wait 5 sec."%(gatewayName))
                self.stopGateway(self.gatewaysInstance.get(gatewayName))
            except:
                self.logger.critical("get some error to stop gateway %s"%(gatewayName))
                
    
    def stopGateway(self,gatewaysInstance):
        '''
        stop a gateway
        
        gatewayInstance: the gateway instance
        raise exceptions
        '''
        try:
            if gatewaysInstance.get('status')=="stop" and gatewaysInstance.get('instance').isAlive():
                self.logger.info("gateways %s is already stop"%(gatewaysInstance.get('name')))
                return
            self.logger.critical("call shutdown gateways %s"%(gatewaysInstance.get('name')))
            gatewaysInstance.get('instance').shutdown()
            if gatewaysInstance.get('instance').isAlive():
                gatewaysInstance.get('instance').join(5)
            gatewaysInstance['status']="stop"
        except:
            self.logger.error("get some error to stop gateway %"%(gatewaysInstance.get('name')),exc_info=True)
            raise
            
        
    
    
    
    