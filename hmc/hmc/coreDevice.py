'''
Created on 08.10.2017

@author: uschoen
'''
__version__ = "2.0"

from hmcDevices import *
import importlib,copy
import sys

class coreDevices ():
    '''
    classdocs
    
    device definition:
    
    self.device={
            "deviceID":strg 
            "deviceTyp":strg
            
            }
    
    '''
    
    def getValue(self,deviceID):
        return self.getDeviceAttributeValue(deviceID, 'value')
    
    def setValue(self,deviceID,value):
        self.setDeviceAttribute(deviceID,'value', value)
    
    def restoreDevice(self,device):
        try:
            if not 'deviceID' in device and not 'typ' in device:
                self.logger.error("device has no deviceID  or deviceTyp device:%s"%(device))
                raise Exception
            if device['deviceID']['value'] in self.devices:
                self.logger.error("deviceID  exists :%s"%(device['deviceID']['value']))
                raise Exception 
            self.logger.info("restore device with device id %s and typ:%s"%(device['deviceID']['value'],device['typ']['value']))
            self.__buildDevice(copy.deepcopy(device))
        except:
            self.logger.error("can not restore device:%s"%(device),exc_info=True)
            raise Exception

    def setDeviceAttribute(self,deviceID,attribute,value):
        self.logger.info("set attribute %s for device id %s value %s"%(attribute,deviceID,value))
        try:
            if not deviceID in self.devices:
                self.logger.error("device id %s not existing"%(deviceID))
                raise Exception
            self.devices[deviceID].setAttributeValue(attribute,value)
            self.updateRemoteCore(False,deviceID,'setDeviceAttribute',deviceID,attribute,value)
        except:
            self.logger.error("can not set attribute %s for device id %s value %s"%(attribute,deviceID,value),exc_info=True)
            raise  
    
    def getDeviceAttributeValue(self,deviceID,attribute):
        try: 
            if deviceID not in self.devices:
                self.logger.error("object id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getAttributeValue(attribute)
        except:
            self.logger.error("can not get attribute %s for device id %s"%(attribute,deviceID),exc_info=True)
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
            self.__buildDevice(copy.deepcopy(device))
            self.updateRemoteCore(False,device['deviceID']['value'],'addDevice',device)
            '''
            # on events
            #todo
            '''
        except:
            self.logger.error("can not add device id %s"%(device['deviceID']['value']),exc_info=True)
            raise Exception
       
    def deviceExists(self,deviceID):   
        if deviceID in self.devices:
            self.logger.debug("device %s is exists"%(deviceID))
            return True
        self.logger.debug("device %s is not exists"%(deviceID))
        return False
    
    def updateDevice(self,device):
        try:
            self.logger.debug("update device %s"%(device['deviceID']['value']))
            if device['deviceID']['value'] in self.devices:
                del self.devices[device['deviceID']['value']]
            self.__buildDevice(copy.deepcopy(device))
            self.updateRemoteCore(False,device['deviceID']['value'],'updateDevice',device)
        except:
            self.logger.error("can not update device %s"%(device['deviceID']['value']),exc_info=True)  
            raise Exception
        
    def getAllDeviceAttribute(self,deviceID): 
        '''
        return a list with all avaible attribute
        '''
        try:
            if deviceID not in self.devices:
                self.__log("error","object id %s not existing"%(deviceID))
                raise Exception
            return self.devices[deviceID].getAllAttribute()
        except:
            self.logger.error("can not get all attribute for deviceID %s"%(deviceID),exc_info=True)  
            raise Exception
    
    def getAllDeviceId(self):  
        object_list=list()
        for object_id in self.devices:
            object_list.append(object_id)
        return object_list
    
    def __buildDevice(self,device):
        self.logger.info("add new device %s"%(device['typ']['value']))
        pakageName="hmc.hmcDevices."+str(device['typ']['value'])
        self.logger.info("try to load %s"%(pakageName))
        argumente=(device,self.eventHandler)
        try:
            module = importlib.import_module(pakageName)
            className = "device"
            self.devices[device['deviceID']['value']] = getattr(module, className)(*argumente)
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    self.logger.warning("Version of %s is %s and can by to low"%(pakageName,module.__version__))
                else:
                    self.logger.info( "Version of %s is %s"%(pakageName,module.__version__))
            else:
                self.logger.warning("pakage %s has no version Info"%(pakageName))
        except ImportError:
            try:
                self.logger.warning("deviceTyp %s no found use hmcDefault typ"%(device['typ']['value']))
                pakageName="hmc.hmcDevices.hmcDevices"
                module = importlib.import_module(pakageName)
                className = "defaultDevice"
                self.devices[device['deviceID']['value']] = getattr(module, className)(*argumente)
                if hasattr(module, '__version__'):
                    if module.__version__<__version__:
                        self.logger.warning("Version of %s is %s and can by to low"%(pakageName,module.__version__))
                    else:
                        self.logger.info( "Version of %s is %s"%(pakageName,module.__version__))
                else:
                    self.logger.warning("pakage %s has no version Info"%(pakageName))
            except :
                self.logger.error("can not load default device",exc_info=True)
                raise Exception
        except :
            self.logger.critical("can not load device",exc_info=True)
            raise Exception