'''
Created on 23.09.2017

@author: uschoen
'''
__version__=0.2

import sys,os

class coreConfiguration():
    
    
    def saveCoreConfiguration(self):
        self.log("warning","not implement")
        return
    def loadAllConfiguration(self):
        self.log("info","load core configuration file")
        path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
        '''
        coreClients
        '''
        self.loadCoreClientsFile(path+self.args['confFile']['remoteCore'])
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
        
            
    def loadGatewayFile(self,filename): 
        self.log("info","reading configuration database gateways %s"%(filename))      
        try:
            gatewaysCFG=self.loadJSON(filename)
            for gatewayName in gatewaysCFG:
                try:
                    self.addGateway(gatewayName,gatewaysCFG[gatewayName])
                except:
                    self.log("error","can not add gateway: %s"%(gatewayName))
        except:
            self.log("error","can not reading configuration database gateways, no gateways add")  
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:%s" %(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            
    def loadCoreClientsFile(self,filename):
        self.log("info","reading configuration database devices %s"%(filename)) 
        try:
            coreClientsCFG=self.loadJSON(filename)
        except IOError:
            self.log("warning","no Device file: %s , add new one"%(filename))
            return
        if len(coreClientsCFG)>0:
            for coreClient in coreClientsCFG:
                self.log("info","restore core sync client: %s"%(coreClientsCFG[coreClient]['hostName']))
                self.addCoreClient(coreClient,coreClientsCFG[coreClient])
        else:
            self.log("info","coreClient file is empty")
        self.log("info","restore coreClient success")
    def loadDeviceFile(self,filename):
        self.log("info","reading configuration database devices %s"%(filename)) 
        try:
            devicesCFG=self.loadJSON(filename)
        except IOError:
            self.log("warning","no Device file: %s , add new one"%(filename))
            return
        
        if len(devicesCFG)>0:
            for deviceID in devicesCFG:
                try:
                    self.log("info","restore deviceID: %s with typ %s  "%(deviceID,devicesCFG[deviceID]['typ']['value']))
                    self.restoreDevice(devicesCFG[deviceID])
                except:
                    self.log("error","can not import deviceID %s"%(deviceID))
        else:
            self.log("info","device file is empty")
        self.log("info","restore devices success")
                   
    def loadDefaultEventFile(self,filename):
        self.log("info","reading configuration database default event handler %s"%(filename))
        try:    
            self.defaultEventHandlerCFG=self.loadJSON(filename)
            for eventTyp in self.defaultEventHandlerCFG:
                for eventHandlerName in self.defaultEventHandlerCFG[eventTyp]:
                    self.log("info","try to add default event handler %s for event %s"%(eventHandlerName,eventTyp))
                    self.addDefaultEventhandler(eventTyp,eventHandlerName)
        except:
            self.log("error","can not reading configuration database eventHandler, no eventHandler add")  
            return

    def loadEventHandlerFile(self,filename):
        self.log("info","reading configuration database event handler %s"%(filename))
        try:
            eventHandlerCFG=self.loadJSON(filename)
            for eventhandler in eventHandlerCFG:
                self.addEventHandler(eventhandler,eventHandlerCFG[eventhandler]) 
        except:
            self.log("error","can not reading configuration database eventHandler, no eventHandler add")  
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Trace back Info:%s" %(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
    '''
    writing Configuration
    '''
    def writeAllConfiguration(self):
        path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
        self.log("info","write configuration")
        self.writeEventHandlerFile(path+self.args['confFile']['eventHandler'])
        self.writeGatewayFile(path+self.args['confFile']['gateways'])
        self.writeDefaultEventHandlerFile(path+self.args['confFile']['defaultEvent'])
        self.writeDevicesFile(path+self.args['confFile']['devices'])
        self.CoreClientsFile(path+self.args['confFile']['remoteCore'])
        
    def writeEventHandlerFile(self,filename=False):
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['eventHandler']
        self.log("info","write event handler configuration to %s"%(filename))
        self.writeJSON(filename,self.eventHandlerCFG)
    
    def writeGatewayFile(self,filename=False):
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['gateways']
        self.log("info","write gateway configuration to %s"%(filename))
        self.writeJSON(filename,self.gatewaysCFG)
    
    def CoreClientsFile(self,filename=False):
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['remoteCore']
        self.log("info","write gateway configuration to %s"%(filename))
        self.writeJSON(filename,self.coreClientsCFG)
    
    def writeDefaultEventHandlerFile(self,filename=False):
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['defaultEvent']
        self.log("info","write default event hadnler configuration to %s"%(filename))
        self.writeJSON(filename,self.defaultEventHandler)
    
    def writeDevicesFile(self,filename=False):
        if not filename:
            path="%s%s/%s"%(self.args['confFile']['basePath'],self.args['global']['host'],self.args['confFile']['filePath'])
            filename=path+self.args['confFile']['devices']
        self.log("info","write device configuration to %s"%(filename))
        configuration={}
        for deviceID in self.getAllDeviceId():
            self.log("data","find object in CORE:%s"%(deviceID))
            configuration[deviceID]=self.devices[deviceID].getConfiguration()
        self.writeJSON(filename,configuration)
    
    
              
            