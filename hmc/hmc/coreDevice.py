'''
Created on 08.10.2017

@author: uschoen


'''
__version__ = "2.0"

import importlib,copy,time,os


class coreDevices ():
    '''
    classdocs
    
    device definition:
    
    self.device={
            "deviceID":strg 
            "deviceTyp":strg
            
            }
    
    '''
    
    def restoreDevice(self,device):
        try:
            if not 'deviceID' in device and not 'typ' in device:
                self.logger.error("device has no deviceID  or deviceTyp device:%s"%(device))
                raise Exception
            if device['deviceID']['value'] in self.devices:
                self.logger.error("deviceID  exists :%s"%(device['deviceID']['value']))
                raise Exception 
            self.logger.info("restore device with device id %s and typ:%s"%(device['deviceID']['value'],device['typ']['value']))
            self.__buildDevice(copy.deepcopy(device),False)
        except:
            self.logger.error("can not restore device:%s"%(device),exc_info=True)
            raise Exception
        
    def addDeviceChannel(self,deviceID,channel):
        self.logger.info("add channel %s for device id %s"%(channel,deviceID))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise
            self.devices[deviceID].addchannel(channel)
            self.updateRemoteCore(False,deviceID,'addDeviceChannel',deviceID,channel)
        except:
            self.logger.error("can not add channel %s for deviceID %s"%(channel,deviceID))
            raise
           
    def ifDeviceChannelExist(self,deviceID,channel):
        channel=channel.lower()
        self.logger.info("if channel %s for device id %s available"%(channel,deviceID))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].ifChannelExist(channel)
        except:
            self.logger.error("can not check if channel %s for device id %s available"%(channel,deviceID),exc_info=True)
            raise
        
    def setDeviceChannel(self,deviceID,channel,value):
        channel=channel.lower()
        self.logger.info("set channel %s for device id %s value %s"%(channel,deviceID,value))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise 
            self.devices[deviceID].setChannelValue(channel,value)
            self.updateRemoteCore(False,deviceID,'setDeviceChannel',deviceID,channel,value)
        except:
            self.logger.error("can not set channel %s for device id %s value %s"%(channel,deviceID,value),exc_info=True)
            raise  
    
    def getDeviceChannelValue(self,deviceID,channel):
        channel=channel.lower()
        try: 
            if deviceID not in self.devices:
                self.logger.error("object id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getChannelValue(channel)
        except:
            self.logger.error("can not get channel %s for device id %s"%(channel,deviceID),exc_info=True)
            raise 
    
    def addDevice(self,device):
        try:
            if not 'deviceID' in device and not 'typ' in device:
                self.logger.error("device has no deviceID  or deviceTyp device:%s"%(device))
                raise Exception
            if device['deviceID']['value'] in self.devices:
                self.logger.error("deviceID  exists :%s"%(device['deviceID']['value']))
                raise Exception 
            self.logger.info("add device with device id %s and typ:%s"%(device['deviceID']['value'],device['typ']['value']))
            self.__buildDevice(copy.deepcopy(device),True)
            self.updateRemoteCore(False,device['deviceID']['value'],'addDevice',device)
            '''
            # on events
            #todo
            '''
        except:
            self.logger.error("can not add device id %s"%(device['deviceID']['value']),exc_info=True)
            raise Exception
    
    def ifDeviceExists(self,deviceID):   
        if deviceID in self.devices:
            self.logger.debug("device %s is exists"%(deviceID))
            return True
        self.logger.debug("device %s is not exists"%(deviceID))
        return False   
    
    def deviceExists(self,deviceID):   
        self.logger.warning("deviceExists is a old function, use ifDeviceExists")
        return self.ifDeviceExists(deviceID)
    
    def updateDevice(self,device):
        try:
            self.logger.debug("update device %s"%(device['deviceID']['value']))
            if device['deviceID']['value'] in self.devices:
                del self.devices[device['deviceID']['value']]
            self.__buildDevice(copy.deepcopy(device),False)
            self.updateRemoteCore(False,device['deviceID']['value'],'updateDevice',device)
        except:
            self.logger.error("can not update device %s"%(device['deviceID']['value']),exc_info=True)  
            raise Exception
        
    def getAllDeviceChannel(self,deviceID): 
        '''
        return a list with all available channel
        '''
        try:
            if deviceID not in self.devices:
                self.__log("error","object id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getAllChannel()
        except:
            self.logger.error("can not get all channel for deviceID %s"%(deviceID),exc_info=True)  
            raise Exception
    
    def getAllDeviceId(self):  
        object_list=list()
        for object_id in self.devices:
            object_list.append(object_id)
        return object_list
    
    def __buildDevice(self,device,adding=False):
        self.logger.info("add new device type %s"%(device['typ']['value']))
        classModul=False
        DEFAULTDEVICE="hmc.devices.hmcDevices"
        argumente=(device,self.eventHandler,adding)
        className = "device"
        devicePackage=DEFAULTDEVICE
        if "package" in device:
            self.logger.debug("find package field:%s in device"%(device['package']['value']))
            devicePackage="gateways.%s.devices.%s"%(device['package']['value'],device['typ']['value'])
        try:
            classModul = self.__loadPackage(devicePackage)
        except:
            self.logger.error("can not load package %s"%(devicePackage))
            devicePath="gateways/%s/devices/"%(device['package']['value'])
            self.__copyNewDevice(devicePath,device['typ']['value'])
            try:
                classModul = self.__loadPackage(devicePackage)
            except:
                self.logger.error("can not load package %s after copy"%(devicePackage))
                try:
                    devicePackage=DEFAULTDEVICE
                    classModul = self.__loadPackage(devicePackage)
                except:
                    self.logger.error("can not load default package %s as fail over"%(devicePackage),exc_info=True)
                    raise
        try:
            self.devices[device['deviceID']['value']] = getattr(classModul, className)(*argumente)
            if hasattr(classModul, '__version__'):
                if classModul.__version__<__version__:
                    self.logger.warning("Version of %s is %s and can by to low"%(devicePackage,classModul.__version__))
                else:
                    self.logger.info( "Version of %s is %s"%(devicePackage,classModul.__version__))
            else:
                self.logger.warning("package %s has no version Info"%(devicePackage))
        except:
            self.logger.error("can not add package %s as deviceID %s"%(devicePackage,device['deviceID']['value']),exc_info=True)
    
    def __loadPackage(self,devicePackage):
        self.logger.info("try to load %s"%(devicePackage))
        try:
            classModul = importlib.import_module(devicePackage)
            return classModul  
        except:
            self.logger.error("can not load package %s"%(devicePackage))
            raise
            
    def __copyNewDevice(self,devicePath,deviceType):
        self.logger.info("copy new device type %s from default path: %s"%(deviceType,devicePath))
        try:
            deviceJsonName="%s%s.json"%(devicePath,deviceType)
            devicefileName="%s%s.py"%(devicePath,deviceType)
            temp={}
            temp['channel']={}
            self.writeJSON(deviceJsonName,temp)
            
            pythonFile = open(os.path.normpath(devicefileName),"w") 
            pythonFile.write("\'\'\'\nCreated on %s\n"%(time.strftime("%d.%m.%Y")))
            pythonFile.write("@author: uschoen\n\n")
            pythonFile.write("\'\'\'\n")
            pythonFile.write("from hmc.devices.hmcDevices import device\n\n")
            pythonFile.write("__version__=\"%s\"\n\n"%(__version__))
            pythonFile.write("\n")
            pythonFile.write("class device(device):\n")
            pythonFile.write("    def _name_(self):\n")
            pythonFile.write("        return \"%s\"\n"%(deviceType))
            pythonFile.close()
        except:
            self.logger.error("can not copy device type %s"%(deviceType),exc_info=True)
        
        
        