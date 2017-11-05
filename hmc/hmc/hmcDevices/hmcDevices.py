'''
Created on 05.12.2016

@author: uschoen
'''
__version__="2.0"

from time import localtime, strftime,time
from datetime import datetime
import json,re,socket


class defaultDevice(object):
    '''
    classdocs
    '''

    ''' 
        contructor
    '''
    def __init__(self,arg,logger,eventHandlerList,adding=False):
        self.__eventHandlerList=eventHandlerList
        self._logger=logger
        self._attribute={}
        self._attribute.update(self._load_attribute("hmc/hmcDevices/hmcDevices.json"))
        self._attribute.update(self._load_attribute("hmc/hmcDevices/"+self._name_()+".json"))
        self._attribute.update(arg)
        self.host=socket.gethostbyaddr(socket.gethostname())[0]
        self._log("debug","build %s instance"%(self._name_()))
        if adding:
            self._oncreate_event()
             
    '''
     delete device
     public function
    '''
    def delete(self):
        self._log("info","delete device %s"%(self._attribute['deviceID']['value']))       
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
        self._log("debug","get all attribute for device:%s"%(self._attribute['deviceID']['value']))
        attribute_list=[]
        for key in self._attribute:
            if not "hidden" in self._attribute[key]:
                attribute_list.append(key)
        return attribute_list
    '''
    add attribute
    internel function
    '''    
    def addAttribute(self,parameter,value):
        self._log("debug","set sensor data")
    '''
    get value of attribut
    public function
     '''    
    def getAttributeValue(self,attribute):
        self._log("debug","get attribut value for:%s"%(attribute))
        try:
            if not attribute in self._attribute:
                self._log("error","can not find attribut:%s "%(attribute))
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
                self._log("error","attribute %s to not exist"%(attribute))
                raise Exception
            self._log("debug","set attribute %s to %s"%(attribute,value))
            self._attribute[attribute]['value']=value
        except:
            self._log("error","can not set attribute %s to %s"%(attribute,value))
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
        self._log("debug","register new event handler %s for event %s"%(eventTyp,eventName))
        if eventName in  self._attribute[eventTyp]['value']:
            self._log("warning","event handler %s for event %s is all reddy registerd"%(eventTyp,eventName))
            return
        self._attribute[eventTyp]['value'].append(eventName)
        
    def _onchange_event(self):
        self._log("debug","__onchange_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['lastchange']['value']=int(time())
        for eventName in self._attribute["onchange_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onrefresh_event(self):
        self._log("debug","__onrefresh_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['lastupdate']['value']=int(time())
        for eventName in self._attribute["onrefresh_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onboot_event(self):
        self._log("debug","__onboot_event: %s"%(self._attribute['deviceID']['value']))
        for eventName in self._attribute["onboot_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _oncreate_event(self):
        self._log("debug","__oncreate_event: %s"%(self._attribute['deviceID']['value']))
        self._attribute['create']['value']=int(time())
        for eventName in self._attribute["oncreate_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _ondelete_event(self):
        self._log("debug","__ondelete_event: %s"%(self._attribute['deviceID']['value']))
        for eventName in self._attribute["ondelete_event"]["value"]:
            self._log("debug","calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
            
    '''
    ####################
    logging
    internel function
    ####################
    '''
    def _log (self,level="unkown",messages="no messages"):
        if self._logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=self._name_()+":%s"%(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self._logger.write(conf)
    def _name_(self):
        return "hmcDevices"
    
    def _load_attribute(self,file):
        self._log("debug","load attribute  "+file)  
        try:
            with open(file) as json_data_file:
                data = json.load(json_data_file)
                return data['attribute'] 
        except IOError:
            self._log("error","can not find "+self._name_()+".json file")   
            raise 
        except :
            self._log("error","can not load "+self._name_()+".json file") 
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