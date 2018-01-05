'''
Created on 23.09.2017

@author: uschoen
'''
__version__=2.1


class coreConfiguration():
    
    def loadAllConfiguration(self):
        self.logger.info("load core configuration file")
        path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
        '''
        event handler
        '''
        self.loadEventHandlerFile(path+self.args['confFile']['eventHandler'])
        '''
        default events
        '''
        self.loadDefaultEventFile(path+self.args['confFile']['defaultEvent'])
        ''' 
        devices
        '''
        self.loadDeviceFile(path+self.args['confFile']['devices'])  
        '''
        gateways
        '''
        self.loadGatewayFile(path+self.args['confFile']['gateways'])
        '''
        coreClients
        '''
        self.loadCoreClientsFile(path+self.args['confFile']['remoteCore'])
            
    def loadGatewayFile(self,filename): 
        self.logger.info("reading configuration database gateways %s"%(filename))      
        try:
            gatewaysCFG=self.loadJSON(filename)
            for gatewayName in gatewaysCFG:
                try:
                    self.addGateway(gatewayName,gatewaysCFG[gatewayName])
                except:
                    self.logger.error("can not add gateway: %s"%(gatewayName), exc_info=True)
        except:
            self.logger.error("can not reading configuration database gateways, no gateways add", exc_info=True)
            
            
    def loadCoreClientsFile(self,filename):
        '''
        ' load the core Clients file
        '''
        self.logger.info("reading configuration database devices %s"%(filename)) 
        try:
            coreClientsCFG=self.loadJSON(filename)
        except IOError:
            self.logger.warning("no core clients file: %s , add new one"%(filename), exc_info=True)
            return
        except:
            self.logger.error("can not reading core clients file", exc_info=True)
            return
        if len(coreClientsCFG)>0:
            for coreClient in coreClientsCFG:
                self.logger.info("restore core sync client: %s"%(coreClientsCFG[coreClient]['hostName']))
                self.restoreCoreClient(coreClient,coreClientsCFG[coreClient])
        else:
            self.logger.info("coreClient file is empty")
        self.logger.info("restore coreClient success")
        
    def loadDeviceFile(self,filename):
        self.logger.info("reading configuration database devices %s"%(filename)) 
        try:
            devicesCFG=self.loadJSON(filename)
        except IOError:
            self.logger.warning("no Device file: %s , add new one"%(filename), exc_info=True)
            return
        except:
            self.logger.error("can not reading device configuration file", exc_info=True)
            return
        if len(devicesCFG)>0:
            for deviceID in devicesCFG:
                try:
                    self.logger.info("restore deviceID: %s with typ %s  "%(deviceID,devicesCFG[deviceID]['device']['devicetype']['value']))
                    newDevice=devicesCFG[deviceID]
                    device=newDevice['device']
                    channel=newDevice['channels']
                    self.restoreDevice(device,channel)
                except:
                    self.logger.error("can not import deviceID %s"%(deviceID), exc_info=True)
        else:
            self.logger.info("device file is empty")
        self.logger.info("restore devices success")
                   
    def loadDefaultEventFile(self,filename):
        self.logger.info("reading configuration database default event handler %s"%(filename))
        try:    
            self.defaultEventHandlerCFG=self.loadJSON(filename)
            for eventTyp in self.defaultEventHandlerCFG:
                for eventHandlerName in self.defaultEventHandlerCFG[eventTyp]:
                    self.logger.info("try to add default event handler %s for event %s"%(eventHandlerName,eventTyp))
                    self.addDefaultEventhandler(eventTyp,eventHandlerName)
        except:
            self.logger.error("can not reading configuration database eventHandler, no eventHandler add")  
            return

    def loadEventHandlerFile(self,filename):
        self.logger.info("reading configuration database event handler %s"%(filename))
        try:
            eventHandlerCFG=self.loadJSON(filename)
            for eventhandler in eventHandlerCFG:
                self.addEventHandler(eventhandler,eventHandlerCFG[eventhandler]) 
        except:
            self.logger.error("can not reading configuration database eventHandler, no eventHandler add",exc_info=True)
    '''
    writing Configuration
    '''
    def writeAllConfiguration(self):
        path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
        self.logger.info("write configuration")
        self.writeEventHandlerFile(path+self.args['confFile']['eventHandler'])
        if self.args['confFile']['gatewaysWrite']:
            self.writeGatewayFile(path+self.args['confFile']['gateways'])
        self.writeDefaultEventHandlerFile(path+self.args['confFile']['defaultEvent'])
        self.writeDevicesFile(path+self.args['confFile']['devices'])
        self.CoreClientsFile(path+self.args['confFile']['remoteCore'])
        
    def writeEventHandlerFile(self,filename=False):
        if len(self.eventHandlerCFG)==0:
            self.logger.warning("can not write event handler, lenght is 0")
            return
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['eventHandler']
        self.logger.info("write event handler configuration to %s"%(filename))
        self.writeJSON(filename,self.eventHandlerCFG)
        
    
    def writeGatewayFile(self,filename=False):
        if len(self.gatewaysCFG)==0:
            self.logger.warning("can not write gateways, lenght is 0")
            return
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['gateways']
        self.logger.info("write gateway configuration to %s"%(filename))
        self.writeJSON(filename,self.gatewaysCFG)
        
    def CoreClientsFile(self,filename=False):
        if len(self.coreClientsCFG)==0:
            self.logger.warning("can not write core Clients, lenght is 0")
            return
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['remoteCore']
        self.logger.info("write gateway configuration to %s"%(filename))
        self.writeJSON(filename,self.coreClientsCFG)
    
    def writeDefaultEventHandlerFile(self,filename=False):
        if len(self.defaultEventHandler)==0:
            self.logger.warning("can not write default event handler, lenght is 0")
            return
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['defaultEvent']
        self.logger.info("write default event handler configuration to %s"%(filename))
        self.writeJSON(filename,self.defaultEventHandler)
        
    
    def writeDevicesFile(self,filename=False):
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['devices']
        self.logger.info("write device configuration to %s"%(filename))
        configuration={}
        for deviceID in self.getAllDeviceId():
            self.logger.debug("find object in CORE:%s"%(deviceID))
            configuration[deviceID]=self.devices[deviceID].getConfiguration()
        self.writeJSON(filename,configuration)
    
    
        
        
    
              
            