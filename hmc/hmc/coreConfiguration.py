'''
Created on 23.09.2017

@author: uschoen
'''
__version__=3.1

'''
TODO:
write config only if entry exist
'''
class coreConfiguration():
    
    def loadAllConfiguration(self):
        self.logger.info("load all configuration file")
        path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
        if not self.ifPathExists(path):
            self.makeDir(path)
        '''
        program 
        '''
        self.loadProgramFile(path+self.args['confFile']['program'])
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
            if not self.ifFileExists(filename):
                self.logger.info("no file %s, create new one"%(filename))  
                self.writeJSON(filename,{}) 
            gatewaysCFG=self.loadJSON(filename)
            for gatewayName in gatewaysCFG:
                try:
                    self.restoreGateway(gatewayName,gatewaysCFG[gatewayName])
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
            if not self.ifFileExists(filename):
                self.logger.info("no file %s, create new one"%(filename))  
                self.writeJSON(filename,{}) 
            coreClientsCFG=self.loadJSON(filename)
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
        self.logger.info("reading configuration devices %s"%(filename)) 
        try:
            if not self.ifFileExists(filename):
                self.logger.info("no file %s, create new one"%(filename))  
                self.writeJSON(filename,{}) 
            devicesCFG=self.loadJSON(filename)
        except:
            self.logger.error("can not reading device configuration  file", exc_info=True)
            return
        if len(devicesCFG)>0:
            self.logger.info("start to restore %s devices"%(len(devicesCFG)))
            for deviceID in devicesCFG:
                try:
                    self.logger.debug("restore deviceID: %s with typ %s  "%(deviceID,devicesCFG[deviceID]['devicetype']))
                    deviceCFG=devicesCFG[deviceID]
                    self.restoreDevice(deviceID,deviceCFG)
                except:
                    self.logger.error("can not import deviceID %s"%(deviceID), exc_info=True)
        else:
            self.logger.info("device file is empty")
        self.logger.info("restore devices success")
                   
    def loadProgramFile(self,filename):
        self.logger.info("load programs from file %s"%(filename))
        try:    
            if not self.ifFileExists(filename):
                self.logger.info("no file %s, create new one"%(filename))  
                self.writeJSON(filename,{}) 
            self.program=self.loadJSON(filename)
            for programName in self.program:
                self.logger.info("try to add program %s"%(programName))
                self.restoreProgram(programName,self.program[programName])
        except:
            self.logger.error("can not add program",exc_info=True)  
            return
    '''
    writing Configuration
    '''
    def writeAllConfiguration(self):
        path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
        self.logger.info("write configuration")
        if not self.ifPathExists(path):
            self.makeDir(path)
        self.writeProgramFile(path+self.args['confFile']['program'])
        self.writeGatewayFile(path+self.args['confFile']['gateways'])
        self.writeDevicesFile(path+self.args['confFile']['devices'])
        self.CoreClientsFile(path+self.args['confFile']['remoteCore'])
        
    def writeProgramFile(self,filename=False):
        if len(self.program)==0:
            self.logger.warning("can not write program, lenght is 0")
            return
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['program']
        self.logger.info("write program configuration to %s"%(filename))
        self.writeJSON(filename,self.program)
        
    
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
    
    
        
        
    
              
            