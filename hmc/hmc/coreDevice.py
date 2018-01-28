'''
Created on 08.10.2017

@author: uschoen


'''
__version__ = 3.1

import importlib
import copy
import time
import os
import py_compile

class coreDevices ():
    '''
    classdocs
    
    device definition:
    
    
    '''
    def restoreDevice(self,deviceID,deviceCFG):
        '''
        retore a device
        ''' 
        adding=False
        try:
            if 'devicetype' not in deviceCFG:
                self.logger.error("deviceID %s has no deviceType use defaultdevice"%(deviceID))
                deviceCFG['devicetype']="defaultdevice"
            if deviceID in self.devices:
                self.logger.error("deviceID  exists :%s, old one will be delete"%(deviceID))
                self.deleteDevice(deviceID)
            self.logger.info("restore device with device id %s and deviceType:%s"%(deviceID,deviceCFG.get('devicetype')))
            self.__buildDevice(copy.deepcopy(deviceCFG),adding)
        except:
            self.logger.error("can not restore deviceID:%s"%(deviceID),exc_info=True)
            raise Exception
    
    def deleteDevice(self,deviceID,callEvents=True):
        '''
        delete a device
        '''
        if deviceID not in self.devices:
            self.logger.error("deviceID:%s is not exisit"%(deviceID))
            return
        self.devices[deviceID].delete(callEvents)
        del self.devices[deviceID]
            
    def addDeviceChannel(self,deviceID,channelName,channelValues,forceUpdate=False):
        '''
        add a new channel to a device
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        channelValuesCP=copy.deepcopy(channelValues)
        self.logger.info("add channel %s for device id %s"%(channelName,deviceID))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise Exception
            self.devices[deviceID].addChannel(channelName,channelValuesCP)
            self.updateRemoteCore(forceUpdate,deviceID,'addDeviceChannel',deviceID,channelName,channelValuesCP)
        except:
            self.logger.error("can not add channel %s for deviceID %s"%(channelName,deviceID))
            raise Exception
           
    def ifDeviceChannelExist(self,deviceID,channelName):
        '''
        check if a channel exist
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        self.logger.debug("check if channel %s for deviceID %s available"%(channelName,deviceID))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].ifChannelExist(channelName)
        except:
            self.logger.error("can not check if channel %s for device id %s available"%(channelName,deviceID),exc_info=True)
            raise
        
    def setDeviceChannelValue(self,deviceID,channelName,value,forceUpdate=False):
        '''
        set a channel value for a dive
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        self.logger.info("set channel %s for deviceID %s value %s"%(channelName,deviceID,value))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise Exception
            self.devices[deviceID].setChannelValue(channelName,value)
            self.updateRemoteCore(forceUpdate,deviceID,'setDeviceChannelValue',deviceID,channelName,value)
        except:
            self.logger.error("can not set channel %s for device id %s value %s"%(channelName,deviceID,value),exc_info=True)
            raise  
    
    def getDeviceChannelKey(self,deviceID,channelName,key):
        '''
        get a value for a device channel field
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        try: 
            if deviceID not in self.devices:
                self.logger.error("object id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getChannelKey(channelName,key)
        except:
            self.logger.error("can not get channel %s and key:%s for deviceID %s"%(channelName,key,deviceID),exc_info=True)
            raise 
    
    def changeDeviceChannel(self,deviceID,channelName,value):
        '''
        change a device channel
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        try: 
            if deviceID not in self.devices:
                self.logger.error("deviceID %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].changeChannelValue(channelName,value)
        except:
            self.logger.error("can not change channel %s for device id %s"%(channelName,deviceID),exc_info=True)
            raise 
       
    def getDeviceChannelValue(self,deviceID,channelName):
        '''
        get a value for a device channel value
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        try: 
            if deviceID not in self.devices:
                self.logger.error("deviceID %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getChannelValue(channelName)
        except:
            self.logger.error("can not get channel %s for device id %s"%(channelName,deviceID),exc_info=True)
            raise 
    
    def addDevice(self,deviceID,deviceCFG,forceUpdate=False):
        '''
        add a new device
        '''
        adding=True
        try:
            if deviceID  in self.devices:
                self.logger.error("deviceID  exists :%s"%(deviceID))
                raise Exception 
            if not 'devicetype' in deviceCFG:
                self.logger.error("device has no deviceType deviceID:%s use to defaultdevice"%(deviceID))
                deviceCFG['devicetype']="defaultdevice"   
            self.logger.info("add device with device id %s and typ:%s"%(deviceID,deviceCFG['devicetype']))
            self.__buildDevice(copy.deepcopy(deviceCFG),adding)
            self.updateRemoteCore(forceUpdate,deviceID,'addDevice',deviceID,deviceCFG)
            #todo: add the event on create
        except:
            self.logger.error("can not add device id %s"%(deviceID),exc_info=True)
            raise Exception
    
    def ifDeviceEnable(self,deviceID): 
        '''
        check if device enable
        
        return  true if enable
                false is disable
                
        exception is deviceID not existing
        '''
        if deviceID not in self.devices:
            self.logger.error("object id %s not existing"%(deviceID))
            raise Exception
        return self.devices[deviceID].ifEnable()
    
    def deviceDisable(self,deviceID,forceUpdate=False): 
        '''
        disable device
                
        exception is deviceID not existing
        update remote core
        '''
        if deviceID not in self.devices:
            self.logger.error("object id %s not existing"%(deviceID))
            raise Exception
        self.devices[deviceID].disable()
        self.updateRemoteCore(forceUpdate,deviceID,'deviceDisable',deviceID)
        
    def deviceEnable(self,deviceID,forceUpdate=False): 
        '''
        enable device
                
        exception is deviceID not existing
        update remote core
        '''
        if deviceID not in self.devices:
            self.logger.error("object id %s not existing"%(deviceID))
            raise Exception
        self.devices[deviceID].enable()
        self.updateRemoteCore(forceUpdate,deviceID,'deviceEnable',deviceID)
      
    def ifDeviceExists(self,deviceID): 
        '''
        check if device exist
        '''  
        if deviceID in self.devices:
            return True
        return False   
    
    def updateDevice(self,deviceID,deviceCFG,forceUpdate=False):
        '''
        update a exist device to a new one
        '''
        self.logger.debug("update device %s"%(deviceID))
        callEvents=False
        addDevice=True
        try:
            if deviceID in self.devices:
                if self.getDeviceConfiguration(deviceID)==deviceCFG:
                    self.logger.debug("nothing to update deviceID %s is up to date"%(deviceID))
                    return
                self.deleteDevice(deviceID,callEvents)
                addDevice=False
            self.__buildDevice(deviceCFG,addDevice)
            self.updateRemoteCore(forceUpdate,deviceID,'updateDevice',deviceID,deviceCFG)
        except:
            self.logger.error("can not update deviceID %s"%(deviceID),exc_info=True)  
            raise Exception
        
    def getDeviceConfiguration(self,deviceID) :
        '''
        get the device configuration back
        '''
        try:
            if deviceID not in self.devices:
                self.__log("error","deviceID %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getConfiguration()
        except:
            self.logger.error("can not get device configuration for deviceID %s"%(deviceID),exc_info=True)  
            raise Exception
        
           
    def getAllDeviceChannel(self,deviceID): 
        '''
        return a list with all available channel
        '''
        try:
            if deviceID not in self.devices:
                self.__log("error","deviceID %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getAllChannel()
        except:
            self.logger.error("can not get all channel for deviceID %s"%(deviceID),exc_info=True)  
            raise Exception
    
    def getAllDeviceId(self):
        '''
        return a array with all device Ids
        ''' 
        return self.devices.keys()
    
    def __buildDevice(self,deviceCFG,adding=False):
        '''
        build a new device object
        '''
        DEFAULTDEVICE="hmc.devices.defaultDevice"
        devicePackage=DEFAULTDEVICE
        if deviceCFG.get('package'):
            devicePackage="gateways.%s.devices.%s"%(deviceCFG.get('package'),deviceCFG.get('devicetype'))
        classModul=False
        argumente=(deviceCFG.get('deviceID'),deviceCFG,self,adding)
        className = "device"
        self.logger.debug("add new device type %s"%(deviceCFG.get('devicetype')))
        
        try:
            classModul = self.__loadPackage(devicePackage)  
        except:
            try:
                self.logger.info("can not load package %s, copy new device"%(devicePackage))
                devicePath="gateways/%s/devices/"%(devicePackage.replace('.','/'))
                self.__copyNewDevice(devicePath,deviceCFG.get('devicetype'))
                classModul = self.__loadPackage(devicePackage)
            except:
                self.logger.error("can not load package %s after copy"%(devicePackage),exc_info=True)
                try:
                    devicePackage=DEFAULTDEVICE
                    classModul = self.__loadPackage(devicePackage)
                except:
                    self.logger.error("can not load default package %s as fail over"%(devicePackage),exc_info=True)
                    raise
        try:
            self.devices[deviceCFG.get('deviceID')]= getattr(classModul, className)(*argumente)
            if hasattr(classModul, '__version__'):
                if classModul.__version__<__version__:
                    self.logger.warning("Version of %s is %s and can by to low"%(devicePackage,classModul.__version__))
                else:
                    self.logger.debug( "Version of %s is %s"%(devicePackage,classModul.__version__))
            else:
                self.logger.warning("package %s has no version Info"%(devicePackage))
        except:
            self.logger.error("can not add package %s as deviceID %s"%(devicePackage,deviceCFG.get('deviceID')),exc_info=True)
    
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
            if os.path.isfile(deviceJsonName):
                self.logger.error("json file for device type %s exists %s"%(deviceType,deviceJsonName))
            else:     
                self.writeJSON(deviceJsonName,temp)
            
            if os.path.isfile(devicefileName):
                self.logger.error("device file for device type %s exists %s"%(deviceType,devicefileName))
            else:
                pythonFile = open(os.path.normpath(devicefileName),"w") 
                pythonFile.write("\'\'\'\nCreated on %s\n"%(time.strftime("%d.%m.%Y")))
                pythonFile.write("@author: uschoen\n\n")
                pythonFile.write("\'\'\'\n")
                pythonFile.write("from hmc.devices.defaultDevice import device\n\n")
                pythonFile.write("__version__=\"%s\"\n\n"%(__version__))
                pythonFile.write("\n")
                pythonFile.write("class device(device):\n")
                pythonFile.write("    def _name_(self):\n")
                pythonFile.write("        return \"%s\"\n"%(deviceType))
                pythonFile.close()
                py_compile.compile(os.path.normpath(devicefileName))
        except:
            self.logger.error("can not copy device type %s"%(deviceType),exc_info=True)
        
        
        