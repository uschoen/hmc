'''
Created on 05.12.2016

@author: uschoen
'''
__version__="2.0"

from time import time
import json,os,copy
import logging
from _hashlib import new


class device(object):
    '''
    classdocs
    '''

    ''' 
        contructor
    '''
    def __init__(self,arg,eventHandlerList,adding=False):
        self.__eventHandlerList=eventHandlerList
        self.logger=logging.getLogger(__name__)
        self._attribute={}
        
        try:
            packagePath=arg["package"]["value"]
            attribute=self._loadJSON("hmc/devices/hmcDevices.json")
            self._attribute.update(attribute['attribute'])
            self._jsonPath="gateways/%s/devices/%s.json"%(packagePath.replace(".", "/"),self._name_())
            attribute=self._loadJSON( self._jsonPath)
            self._attribute.update(attribute['attribute'])
            self._attribute.update(arg)
        except:
            self.logger.error("can not load attribute, %s can not build"%(self._name_()))
            raise
        self.logger.debug("build %s instance"%(self._name_()))
        if adding:
            self._oncreate_event()
             
    '''
     delete device
     public function
    '''
    def delete(self):
        self.logger.info("delete device %s"%(self._attribute['deviceID']['value']))    
        self.logger.warning("delete device not implemnt")       
        self._ondelete_event()
    '''
    ####################
    Attribute section
    ####################
    '''
            
    '''
    get parameter
    public function
    '''    
    def getAllAttribute(self):
        self.logger.debug("get all attribute for device:%s"%(self._attribute['deviceID']['value']))
        attribute_list=[]
        for key in self._attribute:
            if not "hidden" in self._attribute[key]:
                attribute_list.append(key)
        return attribute_list
    '''
    add attribute
    '''    
    def addAttribute(self,attribute):
        self.logger.debug("set sensor data")
        if (attribute.keys()[0]) in self._attribute:
            self.logger.error("attribute: %s exist"%(attribute))
            raise
        self._attribute.update(attribute)   
        try:
            writeJsonVars={}
            oldJsonvar=self._loadJSON(self._jsonPath)
            newJsonVars=oldJsonvar['attribute']
            newJsonVars.update(attribute)
            writeJsonVars['attribute']=newJsonVars
            self._writeJSON(self._jsonPath,writeJsonVars)
                            
        except:
            self.logger.error("can not write new attribute file to %s"%(self._jsonPath), exc_info=True)
    def ifAttributeExist(self,attribute):
        if attribute in self._attribute:
            return True
        return False
    '''
    get value of attribute
    public function
     '''    
    def getAttributeValue(self,attribute):
        self.logger.debug("get attribute value for:%s"%(attribute))
        try:
            if not attribute in self._attribute:
                self.logger.error("can not find attribute:%s "%(attribute))
                raise Exception
            return self._attribute[attribute]['value']
        except:
            raise Exception
    
    '''
     set value of attribute
     public function
     '''    
    def setAttributeValue(self,attribute,value):
        try:
            if not attribute in self._attribute:
                self.logger.error("attribute %s to not exist"%(attribute))
                raise Exception
            self.logger.debug("set attribute %s to %s"%(attribute,value))
            oldValue=self._attribute[attribute]['value']
            self._attribute[attribute]['value']=value
            if oldValue<>value:
                self._onchange_event(attribute)
            self._onrefresh_event(attribute)
        except:
            self.logger.error("can not set attribute %s to %s"%(attribute,value))
            raise Exception
    
    def getConfiguration(self):
        return self._attribute
    '''
    ####################
    Events
    internel function
    ####################
    '''
    def registerEventHandler(self,eventTyp,eventName):
        self.logger.debug("register new event handler %s for event %s"%(eventTyp,eventName))
        if eventName in  self._attribute[eventTyp]['value']:
            self.logger.warning("event handler %s for event %s is all reddy registerd"%(eventTyp,eventName))
            return
        self._attribute[eventTyp]['value'].append(eventName)
        
    def _onchange_event(self,attribute):
        self.logger.debug("__onchange_event: %s for attribute: %s"%(self._attribute['deviceID']['value'],attribute))
        self._attribute['lastchange']['value']=int(time())
        for eventName in self._attribute["onchange_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onrefresh_event(self,attribute):
        self.logger.debug("__onrefresh_event: %s for attribute: %s"%(self._attribute['deviceID']['value'],attribute))
        self._attribute['lastupdate']['value']=int(time())
        for eventName in self._attribute["onrefresh_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onboot_event(self):
        self.logger.debug("__onboot_event: %s"%(self._attribute['deviceID']['value']))
        for eventName in self._attribute["onboot_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _oncreate_event(self):
        self.logger.debug("__oncreate_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['create']['value']=int(time())
        for eventName in self._attribute["oncreate_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _ondelete_event(self):
        self.logger.debug("__ondelete_event: %s"%(self._attribute['deviceID']['value']))
        for eventName in self._attribute["ondelete_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
            
    def _name_(self):
        return "hmcDevices"
    
    def _writeJSON(self,filename,data={}):
        self.logger.info("write configuration to %s"%(filename))
        try:
            with open(os.path.normpath(filename),'w') as outfile:
                json.dump(data, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            self.logger.error("can not find file: %s "%(os.path.normpath(filename)), exc_info=True)
            raise
        except ValueError:
            self.logger.error("error in find file: %s "%(os.path.normpath(filename)), exc_info=True)
            raise
        except:
            self.logger.error("unkown error:", exc_info=True)
            raise
                      
    def _loadJSON(self,filename):
        '''
        loading configuration file
        '''
        try:
            with open(os.path.normpath(filename)) as jsonDataFile:
                dateFile = json.load(jsonDataFile)
            return dateFile 
        except IOError:
            self.logger.error("can not file: %s "%(os.path.normpath(filename)), exc_info=True)
            raise
        except ValueError:
            self.logger.error("error in file: %s "%(os.path.normpath(filename)), exc_info=True)
            raise
        except:
            self.logger.error("unkown error",exc_info=True)
            raise 
    '''    
    
    
if __name__ == "__main__":

    
    class logger(object):
        def write(self,arg):
            print arg['messages']
    loging=logger()
    arg={'deviceID':{
                        "value":"test@test.test"
                        },
             'typ':{
                        "value":"hmcDevices"
                        }
            }
    hmcDevice = defaultDevice(arg,loging)
    print("build hmc object")
    print("start thread")
    hmcDevice.setValue(90)
    hmcDevice.setParameterValue("rssi", -98)
    while True:
        print("main wait 10 sec")
        sleep(10)    
'''