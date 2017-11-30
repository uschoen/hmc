'''
Created on 05.12.2016

@author: uschoen
'''
__version__="2.0"

from time import time
import json,os,logging
from email.policy import default
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
        self._channels={}
        
        try:
            packagePath=arg["package"]["value"]
            channel=self._loadJSON("hmc/devices/hmcDevices.json")
            self._channel.update(channel['channel'])
            self._jsonPath="gateways/%s/devices/%s.json"%(packagePath.replace(".", "/"),self._name_())
            channel=self._loadJSON( self._jsonPath)
            self._channel.update(channel['channel'])
            self._channel.update(arg)
        except:
            self.logger.error("can not load channels, %s can not build"%(self._name_()))
            raise
        self.logger.debug("build %s instance"%(self._name_()))
        if adding:
            self._oncreate_event()
             
    '''
     delete device
     public function
    '''
    def delete(self):
        self.logger.info("delete device %s"%(self._channel['deviceID']['value']))    
        self.logger.warning("delete device not implemnt")       
        self._ondelete_event()
    '''
    ####################
    channel section
    ####################
    '''
            
    '''
    get parameter
    public function
    '''    
    def getAllChannel(self):
        self.logger.debug("get all channel for device:%s"%(self._channel['deviceID']['value']))
        channel_list=[]
        for key in self._channel:
            if not "hidden" in self._channel[key]:
                channel_list.append(key)
        return channel_list
    '''
    add channel
    '''    
    def addChannel(self,channel):
        self.logger.info("add channel %s"%(channel))
        channelName=channel.keys()[0]
        if (channelName) in self._channel:
            self.logger.error("channel: %s is exist"%(channelName))
            raise
        newChannel={}
        newChannel[channelName]=self._channelDefaults()
        newChannel[channelName].update(channel[channelName])
        
        try:
            writeJsonVars={}
            oldJsonvar=self._loadJSON(self._jsonPath)
            newJsonVars=oldJsonvar['channel']
            newJsonVars.update(channel)
            writeJsonVars['channel']=newJsonVars
            self._writeJSON(self._jsonPath,writeJsonVars)
            self.__channel.update(channel)                  
        except:
            self.logger.error("can not write new channel to file %s"%(self._jsonPath), exc_info=True)
            raise
    
    def _channelDefaults(self):
        channel={
            "name":{        
                "value":"unkown",
                "typ":"string"},
            "lastchange":{
                "value":"0",
                "typ":"int",
                "hidden":False},
             "lastupdate":{
                "value":"0",
                "typ":"int",
                "hidden":False},
             "create":{
                "value":"0",
                "typ":"int"},
              "enable":{
                "value":True,
                "typ":"bool"},
             "events":{}
        }
        return channel
        
    def ifChannelExist(self,channel):
        if channel in self._channel:
            return True
        return False
    
    '''
    get value of channel
    public function
     '''    
    def getChannelValue(self,channel):
        self.logger.debug("get value for channel:%s"%(channel))
        try:
            if not channel in self._channel:
                self.logger.error("channel %s is not exist"%(channel))
                raise Exception
            return self._channel[channel]['value']
        except:
            self.logger.error("unknown error in getChannelValue")
            raise 
    
    '''
     set value of channel
     public function
     '''    
    def setChannelValue(self,channel,value):
        try:
            if not channel in self._channel:
                self.logger.error("channel %s is not exist"%(channel))
                raise 
            self.logger.debug("set channel %s to %s"%(channel,value))
            oldValue=self._channel[channel]['value']
            self._channel[channel]['value']=value
            if oldValue<>value:
                self._callEvent('on_change_event',channel)
            self._callEvent('on_refrech_event',channel)
        except:
            self.logger.error("can not set channel %s to %s"%(channel,value))
            raise 
    
    def getConfiguration(self):
        return self._channel
    '''
    ####################
    Events
    internel function
    ####################
    '''
    def registerEventHandler(self,eventTyp,eventName):
        self.logger.debug("register new event handler %s for event %s"%(eventTyp,eventName))
        if eventName in  self._channel[eventTyp]['value']:
            self.logger.warning("event handler %s for event %s is all reddy registerd"%(eventTyp,eventName))
            return
        self._channel[eventTyp]['value'].append(eventName)
    
    def _callEvent(self,eventTyp,channel):
        self.logger.debug("call event: %s for channel: %s for deviceID:%s"%(eventTyp,channel,self._channel['deviceID']['value']))
        self._channel[channel][eventTyp]['time']=int(time())
        
        
    def _onchange_event(self,channel):
        self.logger.debug("__onchange_event: %s for channel: %s"%(self._channel['deviceID']['value'],channel))
        self._channel['lastchange']['value']=int(time())
        for eventName in self._channel["onchange_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onrefresh_event(self,channel):
        self.logger.debug("__onrefresh_event: %s for channel: %s"%(self._channel['deviceID']['value'],channel))
        self._channel['lastupdate']['value']=int(time())
        for eventName in self._channel["onrefresh_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _onboot_event(self):
        self.logger.debug("__onboot_event: %s"%(self._channel['deviceID']['value']))
        for eventName in self._channel["onboot_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _oncreate_event(self):
        self.logger.debug("__oncreate_event: %s"%(self._channel['deviceID']['value']))
        self._channel['create']['value']=int(time())
        for eventName in self._channel["oncreate_event"]["value"]:
            self.logger.debug("calling: %s event handler"%(eventName))
            self.__eventHandlerList[eventName].callback(self)
    def _ondelete_event(self):
        self.logger.debug("__ondelete_event: %s"%(self._channel['deviceID']['value']))
        for eventName in self._channel["ondelete_event"]["value"]:
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
            self.logger.error("unknown error:", exc_info=True)
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
            self.logger.error("unknown error",exc_info=True)
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