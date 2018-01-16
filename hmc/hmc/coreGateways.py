'''
Created on 23.09.2017

@author: uschoen
'''
__version__=3.1

from gateways import *
import importlib


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
    
    def restoreGateway(self,gatewayName,config):
        ''' 
        restore a Gateway, the gateway name have to be unique and not exisitng,
        after restore its not update the other core server. This ist only
        a action for startup !!! 
        
        gatewayName: name of the gateway 
        config: configuration of the gateways
            {
            "enable": enable the gateway, if the gateway not enable it will not build only store in cfg file
            "package":package name of the gateways
            "modul": module name of the gateway
            "class": class of the module
            "config":configuration of the gateways class
            "host": host name on wich is running the gateway
            }
        
        raise no exception 
        '''
        self.logger.info("restore gateway %s"%(gatewayName))
        try:
            self.__buildGateway(gatewayName,config)
            self.startGateway(gatewayName)  
        except:
            pass
            
        
    def addGateway(self,gatewayName,config,forceUpdate=False):
        ''' 
        add a Gateway, the gateway name have to be unique an not exsisting
        after add its update the other core server
        
        gatewayName: name of the gateway 
        config: configuration of the gateways
            {
            "enable": enable the gateway, if the gateway not enable it will not build only store in cfg file
            "package":package name of the gateways
            "modul": module name of the gateway
            "class": class of the module
            "config":configuration of the gateways class
            "host": host name on wich is running the gateway
            }
        
        raise exception on failure
        '''
        self.logger.info("restore gateway %s"%(gatewayName))
        try:
            self.__buildGateway(gatewayName,config)  
            self.startGateway(gatewayName)      
            self.updateRemoteCore(forceUpdate,gatewayName,'addGateway',gatewayName,config)
        except:
            self.logger.info("can not add gateway %s"%(gatewayName))
            raise Exception
        
     
    def updateGateway(self,gatewayName,config,forceUpdate=False):
        ''' 
        update a Gateway, the gateway name have to be unique can be existing.
        If a Gateway existing it will be stop and delete.
        after update its update the other core server
        
        gatewayName: name of the gateway 
        config: configuration of the gateways
            {
            "enable": enable the gateway, if the gateway not enable it will not build only store in cfg file
            "package":package name of the gateways
            "modul": module name of the gateway
            "class": class of the module
            "config":configuration of the gateways class
            "host": host name on wich is running the gateway
            }
        
        raise exception on failure
        '''
        self.logger.info("update gateway %s"%(gatewayName))
        try:
            if config==self.gatewaysCFG.get(gatewayName,{}):
                self.logger.info("no update need, %s gateway have same setting"%(gatewayName))
                return
            self.deleteGateway(gatewayName)
            self.__buildGateway(gatewayName,config)
            try:
                self.startGateway(gatewayName)
            except:
                pass
            self.updateRemoteCore(forceUpdate,gatewayName,'updateGateway',gatewayName,config)
        except:
            self.logger.debug("can not update gateway %s"%(gatewayName),exc_info=True)
            raise Exception
    
    
    def deleteGateway(self,gatewayName):
        ''' 
        delete a gateway
        
        gatewaysName: the name of the gateway
        
        raise all exceptions
        '''
        self.logger.debug("delete gateway %s"%(gatewayName))
        if gatewayName in self.gatewaysInstance:
            self.logger.error("gateway %s existing, try to stop"%(gatewayName))
            if self.gatewaysInstance[gatewayName]['status']<>"stop":
                try:
                    self.stopGateway(gatewayName)
                except:
                    pass
            del self.gatewaysInstance[gatewayName]
        if  gatewayName in self.gatewaysCFG:  
            del self.gatewaysCFG[gatewayName]     
                  
    def __buildGateway(self,gatewayName,config):
        '''
        build a gateway
        
        gatewayName: name of the gateway 
        config: configuration of the gateways
            {
            "enable": enable the gateway, if the gateway not enable it will not build only store in cfg file
            "package":package name of the gateways
            "modul": module name of the gateway
            "class": class of the module
            "config":configuration of the gateways class
            "host": host name on wich is running the gateway
            }
            
        raise exception on failure
        '''
        if gatewayName in  self.gatewaysInstance or gatewayName in self.gatewaysCFG:
            self.logger.error("gateway %s exists as Instance or configuration "%(gatewayName))
            raise Exception
        self.logger.info("build gateway %s"%(gatewayName))
        ''' default configuration with update from gateways cfg (config) '''
        defaultGatewayCFG={
                    "enable":False,
                    "package":"unknown",
                    "modul":"unknown",
                    "class":"unkown",
                    "config":{},
                    "host":"unknown"
                    }
        defaultGatewayCFG.update(config)
        defaultGatewayCFG.update(self.args.get('global'))
        if not defaultGatewayCFG['enable']:
            defaultGatewayCFG['config']['enable']=False
        self.gatewaysCFG[gatewayName]=defaultGatewayCFG
        '''
        try to build the gateway instance '''         
        if self.eventHome(gatewayName): 
            try:
                if defaultGatewayCFG.get('enable'):
                    pakage="gateways.%s.%s"%(defaultGatewayCFG.get('package'),defaultGatewayCFG.get('modul'))
                    CLASS_NAME = defaultGatewayCFG.get('class')
                    ARGUMENTS = (defaultGatewayCFG.get('config'),self)
                    
                    self.logger.info("try to load gateway: %s  with package: %s"%(gatewayName,pakage))
                    self.gatewaysInstance[gatewayName]={
                                                'name':gatewayName,
                                                'status':"stop",
                                                'enable':False,
                                                'instance':False
                                                }
                    module = importlib.import_module(pakage)
                    self.gatewaysInstance[gatewayName]['instance'] = getattr(module, CLASS_NAME)(*ARGUMENTS)
                    self.gatewaysInstance[gatewayName]['instance'].daemon = True
                    self.gatewaysInstance[gatewayName]['enable']=True
                else:
                    self.logger.info("gateway %s is disable"%(gatewayName)) 
                    
            except :
                self.logger.critical("can not build gateways %s"%(gatewayName),exc_info=True)
                self.gatewaysInstance[gatewayName]['enable']=False
                raise Exception
        else:
            self.logger.info("gateways %s is not on this host"%(gatewayName))
            
    def startGateway(self,gatewayName):
        '''
        start a gateway, the gateway have to build before
        
        raise a exception
        '''
        if gatewayName not in self.gatewaysInstance:
            self.logger.error("gateways %s is not existing"%(gatewayName))
            raise Exception
        if not self.gatewaysInstance[gatewayName]['enable']:
            self.logger.error("gateways %s is not enable"%(gatewayName))
            raise Exception  
        try:
            self.gatewaysInstance[gatewayName]['instance'].start()
            self.gatewaysInstance[gatewayName]['status']="start"
        except:
            self.logger.error("can not start gateways %s"%(gatewayName),exc_info=True)
            self.gatewaysInstance[gatewayName]['status']="stop"
            self.gatewaysInstance[gatewayName]['enable']=False
            raise Exception
        
    def shutdownAllGateways(self):
        '''
        shutdown all gateways
        '''
        for gatewayName in self.gatewaysInstance:   
            try:
                self.logger.critical("shutdown gateways %s and wait 5 sec."%(gatewayName))
                self.stopGateway(gatewayName)
            except:
                self.logger.critical("get some error to stop gateway %s"%(gatewayName))
                
    
    def stopGateway(self,gatewayName):
        '''
        stop a gateway
        
        gatewayInstance: the gateway instance
        raise exceptions
        '''
        if gatewayName not in self.gatewaysInstance:
            self.logger.warning("gateway %s does not existing"%(gatewayName))
            raise Exception
        try:
            if self.gatewaysInstance[gatewayName].get('status')=="stop" and self.gatewaysInstance[gatewayName]['instance'].isAlive():
                self.logger.info("gateways %s is already stop"%(self.gatewaysInstance[gatewayName].get('name')))
                return
            self.logger.critical("call shutdown gateways %s"%(self.gatewaysInstance[gatewayName].get('name')))
            self.gatewaysInstance[gatewayName]['instance'].shutdown()
            if self.gatewaysInstance[gatewayName]['instance'].isAlive():
                self.gatewaysInstance[gatewayName]['instance'].join(5)
            self.gatewaysInstance[gatewayName]['status']="stop"
        except:
            self.logger.error("get some error to stop gateway %"%(self.gatewaysInstance[gatewayName]['name']),exc_info=True)
            raise
            
        
    
    
    
    