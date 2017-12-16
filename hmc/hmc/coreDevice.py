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
    
    
    '''
    
    def restoreDevice(self,device):
        '''
        retore a dive
        '''
        try:
            if not 'deviceID' in device['device'] and not 'devicetype' in device['device']:
                self.logger.error("device has no deviceID  or deviceType device:%s"%(device))
                raise Exception
            if device['device']['deviceID']['value'] in self.devices:
                self.logger.error("deviceID  exists :%s"%(device['device']['deviceID']['value']))
                raise Exception 
            self.logger.info("restore device with device id %s and deviceType:%s"%(device['device']['deviceID']['value'],device['device']['devicetype']['value']))
            self.__buildDevice(copy.deepcopy(device),False)
        except:
            self.logger.error("can not restore device:%s"%(device),exc_info=True)
            raise Exception
        
    def addDeviceChannel(self,deviceID,channelName,Values):
        '''
        add a new channel to a device
        '''
        channelValues=copy.deepcopy(Values)
        self.logger.info("add channel %s for device id %s"%(channelName,deviceID))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise
            self.devices[deviceID].addChannel(channelName,channelValues)
            self.updateRemoteCore(False,deviceID,'addDeviceChannel',deviceID,channelName,Values)
        except:
            self.logger.error("can not add channel %s for deviceID %s"%(channelName,deviceID))
            raise
           
    def ifDeviceChannelExist(self,deviceID,channelName):
        '''
        check if a channel exist
        '''
        channelName=channelName.lower()
        self.logger.info("check if channel %s for deviceID %s available"%(channelName,deviceID))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].ifChannelExist(channelName)
        except:
            self.logger.error("can not check if channel %s for device id %s available"%(channelName,deviceID),exc_info=True)
            raise
        
    def setDeviceChannelValue(self,deviceID,channelName,value):
        '''
        set a channel value for a dive
        '''
        channelName=channelName.lower()
        self.logger.info("set channel %s for device id %s value %s"%(channelName,deviceID,value))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise 
            self.devices[deviceID].setChannelValue(channelName,value)
            self.updateRemoteCore(False,deviceID,'setDeviceChannel',deviceID,channelName,value)
        except:
            self.logger.error("can not set channel %s for device id %s value %s"%(channelName,deviceID,value),exc_info=True)
            raise  
    
    def getDeviceChannelValue(self,deviceID,channelName):
        '''
        get a value for a device channel
        '''
        channelName=channelName.lower()
        try: 
            if deviceID not in self.devices:
                self.logger.error("object id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getChannelValue(channelName)
        except:
            self.logger.error("can not get channel %s for device id %s"%(channelName,deviceID),exc_info=True)
            raise 
    
    def addDevice(self,device):
        '''
        add a new device
        '''
        try:
            if not 'deviceID' in device['device'] and not 'devicetype' in device['device']:
                self.logger.error("device has no deviceID  or deviceType device:%s"%(device))
                raise Exception
            if device['device']['deviceID']['value']  in self.devices:
                self.logger.error("deviceID  exists :%s"%(device['device']['deviceID']['value']))
                raise Exception 
            self.logger.info("add device with device id %s and typ:%s"%(device['device']['deviceID']['value'] ,device['device']['devicetype']['value']))
            self.__buildDevice(copy.deepcopy(device),True)
            self.updateRemoteCore(False,device['device']['deviceID']['value'],'addDevice',device)
            #todo: add the event on create
        except:
            self.logger.error("can not add device id %s"%(device['device']['deviceID']['value']),exc_info=True)
            raise Exception
    
    def ifDeviceExists(self,deviceID): 
        '''
        check if device exist
        '''  
        if deviceID in self.devices:
            self.logger.debug("device %s is exists"%(deviceID))
            return True
        self.logger.debug("device %s is not exists"%(deviceID))
        return False   
    
    def updateDevice(self,device):
        '''
        update a exist device to a new one
        '''
        try:
            deviceID=device['device']['deviceID']['value']
            self.logger.debug("update device %s"%(deviceID))
            if deviceID in self.devices:
                del self.devices[deviceID]
            self.__buildDevice(copy.deepcopy(device),False)
            self.updateRemoteCore(False,deviceID,'updateDevice',device)
        except:
            self.logger.error("can not update device %s"%(deviceID),exc_info=True)  
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
        '''
        return a array with all device Ids
        ''' 
        object_list=list()
        for object_id in self.devices:
            object_list.append(object_id)
        return object_list
    
    def __buildDevice(self,device,adding=False):
        '''
        build a new device object
        '''
        self.logger.info("add new device type %s"%(device['device']['devicetype']['value']))
        classModul=False
        DEFAULTDEVICE="hmc.devices.defaultDevice"
        argumente=(device,self.eventHandler,adding)
        className = "device"
        devicePackage=DEFAULTDEVICE
        if "package" in device['device']:
            self.logger.debug("find package field:%s in device"%(device['device']['package']['value']))
            devicePackage="gateways.%s.devices.%s"%(device['device']['package']['value'],device['device']['devicetype']['value'])
        try:
            classModul = self.__loadPackage(devicePackage)
        except:
            self.logger.error("can not load package %s"%(devicePackage))
            devicePath="gateways/%s/devices/"%(device['device']['package']['value'])
            self.__copyNewDevice(devicePath,device['device']['devicetype']['value'])
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
            self.devices[device['device']['deviceID']['value']]= getattr(classModul, className)(*argumente)
            if hasattr(classModul, '__version__'):
                if classModul.__version__<__version__:
                    self.logger.warning("Version of %s is %s and can by to low"%(devicePackage,classModul.__version__))
                else:
                    self.logger.info( "Version of %s is %s"%(devicePackage,classModul.__version__))
            else:
                self.logger.warning("package %s has no version Info"%(devicePackage))
        except:
            self.logger.error("can not add package %s as deviceID %s"%(devicePackage,device['device']['deviceID']['value']),exc_info=True)
    
    def __loadPackage(self,devicePackage):
        '''
        load a package
        '''
        self.logger.info("try to load %s"%(devicePackage))
        try:
            classModul = importlib.import_module(devicePackage)
            return classModul  
        except:
            self.logger.error("can not load package %s"%(devicePackage))
            raise
            
    def __copyNewDevice(self,devicePath,deviceType):
        '''
        copy a new device type
        '''
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
            pythonFile.write("from hmc.devices.defaultDeviceimport device\n\n")
            pythonFile.write("__version__=\"%s\"\n\n"%(__version__))
            pythonFile.write("\n")
            pythonFile.write("class device(device):\n")
            pythonFile.write("    def _name_(self):\n")
            pythonFile.write("        return \"%s\"\n"%(deviceType))
            pythonFile.close()
        except:
            self.logger.error("can not copy device type %s"%(deviceType),exc_info=True)
        
        
        