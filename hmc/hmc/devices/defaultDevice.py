'''
Created on 09.12.2017

@author: uschoen
'''

__version__="2.0"

from time import time
import json,os,logging


class device(object):
    
    def __init__ (self,arg,eventHandlerList,adding=False):
        
        '''
        class vars
        '''
        # list of device configuration
        self._device={
                        
                            "deviceID":{
                                "value":"unknown@unknown.unknown",
                                "type":"string"},
                             "devicetype":{
                                "value":"defaultDevice",
                                "type":"string"},
                             "package":{
                                "value":"hmc.devices",
                                "type":"string"},
                             "rssi":{        
                                 "value":"0",
                                "type":"int"},
                             "name":{
                                 "value":"unknown",
                                 "type":"string"},
                             "devicegroupe":[],
                             "lastchange":{
                                 "value":"unknown",
                                 "type":"int"},
                             "create":{
                                 "value":"unknown",
                                 "type":"int"},
                             "lastupdate":{
                                 "value":"unknown",
                                 "type":"int"},
                             "gateway":{
                                 "value":"unknown",
                                 "type":"string"},
                             "enable":{
                                 "value":"unknown",
                                 "type":"string"},
                             "events":{
                                "onchange_event":[],
                                "onrefresh_event":[],
                                "onboot_event":[],
                                "oncreate_event":[],
                                "ondelete_event":[]}
                                }
                         
        
        self._channels={}       # list of all channels
        
        '''
        objects
        '''
        self.logger=logging.getLogger(__name__) # logger object
        self._eventHandlerList=eventHandlerList # event handler
        self._packageName=arg["device"]["package"]['value']
        self._configurationFile="gateways/%s/devices/%s.json"%(self._packageName.replace(".", "/"),self._name_())
        
        try:         
            packageConfiguration=self._loadJSON(self._configurationFile)
            
            if 'device' in packageConfiguration:
                self._device.update(packageConfiguration['device'])
            else:
                self.logger.info("configuration file: %s has no device attribute"%(self._configurationFile))
            
            if 'channels' in packageConfiguration:
                self._channels.update(packageConfiguration['channels'])
            else:
                self.logger.info("configuration file: %s has no channels attribute"%(self._configurationFile))
            
            if 'channels' in arg:
                self._channels.update(arg['channels'])
            
            if 'device' in arg:   
                self._device.update(arg['device'])
        except:
            self.logger.error("can not load channels, %s can not build"%(self._name_()))
            raise
        
        self.logger.debug("build %s instance"%(self._name_()))
        if adding:
            self._callEvent('oncreate_event', 'device')
    
    def delete(self):
        '''
        delete function of the device
        '''
        
        self.logger.info("delete device %s"%(self._device['deviceID']['value']))    
        self.logger.warning("delete device not implemented")       
        self._callEvent('ondelete_event','device')
    
    def getAllChannel(self):
        '''
        return all channels of the device as array
        '''
        self.logger.debug("get all channel for deviceID:%s"%(self._device['deviceID']['value']))
        channel_list=[]
        
        for channelName in self._channels:
            if not "hidden" in self._channels[channelName]:
                channel_list.append(channelName)
            elif self._channels[channelName]['hidden']==False:
                self._channels.append(channelName)
        return channel_list
    
    def addChannel(self,channelName,channelValues):
        '''
        add a new channel
        '''
        channelName=channelName.lower()
        self.logger.info("add channel %s"%(channelName))
        if channelName in self._channels:
            self.logger.error("channel: %s is exist"%(channelName))
        try:
            newChannel={}
            newChannel=self._channelDefaults()
            newChannel.update(channelValues[channelName])
            self._channels[channelName]=newChannel 
        except:
            self.logger.error("can not add new channel to devicID %s"%(self._device['deviceID']['value']), exc_info=True)
            raise   
    
    def getChannelValue(self,channel):
        '''
        get value of channel
        public function
        '''    
    
        self.logger.debug("get value for channel:%s"%(channel))
        try:
            if not channel in self._channels:
                self.logger.error("channel %s is not exist"%(channel))
                raise Exception
            return self._channels[channel]['value']
        except:
            self.logger.error("unknown error in getChannelValue")
            raise 
    
       
    def setChannelValue(self,channelName,value):
        '''
        set value of channel
        ''' 
        channelName=channelName.lower()
        try:
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise 
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._channels[channelName]['value']
            self._channels[channelName]['value']=value
            if oldValue<>value:
                self._callEvent('onchange_event',channelName)
            self._callEvent('onrefresh_event',channelName)
            
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value))
            raise 
        
    def getConfiguration(self):
        '''
        return the configuration from the device
        '''
        configuration={}
        configuration['device']=self._device
        configuration['channels']=self._channels
        return configuration
    
    def registerEventHandler(self,eventTyp,eventName,channelName):
        '''
        register new event handler for channel or device
        '''
        self.logger.debug("register new event handler %s for event %s on channel %s"%(eventTyp,eventName,channelName))
        if channelName=='device':
            '''
            for device events
            '''
            if eventName in self._deviece['events'][eventTyp]:
                self.logger.warning("event handler %s for event %s is all ready registerd"%(eventTyp,eventName))
                return
            self._device['events'][eventTyp].append(eventName)
        else:
            '''
            for channel events
            ''' 
            if eventName in  self._channels[channelName]['event'][eventTyp]:
                self.logger.warning("event handler %s for event %s is all ready registerd"%(eventTyp,eventName))
                return
            self._channel[channelName]['events'].append(eventName)
        
    
    def ifChannelExist(self,channelName):
        '''
        return true if channel exists
        '''
        channelName=channelName.lower()
        if channelName in self._channels:
            return True
        return False
    
    def _channelDefaults(self):
        '''
        return the channel default
        '''
        channel={
            "value":{
                "value":"unkown",
                "type":"string"
                },
            "name":{        
                "value":"unkown",
                "type":"string"},
            "lastchange":{
                "value":"0",
                "type":"int",
                "hidden":False},
            "lastupdate":{
                "value":"0",
                "type":"int",
                "hidden":False},
            "create":{
                "value":"0",
                "type":"int"},
            "enable":{
                "value":True,
                "type":"bool"},
            "events":{
                        "onchange_event":[],
                        "onrefresh_event":[],
                        "onboot_event":[],
                        "oncreate_event":[],
                        "ondelete_event":[]}
        }
        return channel
    
    def _callEvent(self,eventTyp,channel):
        '''
        eventTyps:
        onchange_event
        onrefresh_event
        onboot_event
        oncreate_event
        ondelete_event
        '''
        self.logger.debug("call event: %s for channel: %s, for deviceID:%s"%(eventTyp,channel,self._device['deviceID']['value']))
        if channel not in self._channels and not channel=='device':
            '''
            check if channel exist
            '''
            self.logger.warning("channel %s not exists in deviceID %s"%(channel,self._device['deviceID']['value']))
            return 
        
        if not channel=='device':
            '''
            select event type
            '''
            if eventTyp=='onchange_event':
                self._onchange_event(channel)
            elif eventTyp=='onrefresh_event':
                self._onrefresh_event(channel)
            elif eventTyp=='onboot_event':
                self._onboot_event(channel)
            elif eventTyp=='oncreate_event':
                self._oncreate_event(channel)
            elif eventTyp=='ondelete_event':   
                self._ondelete_event(channel)
            else:
                self.logger.warning("event type %s is unknown"%(eventTyp))
                return     
        
        if not channel=='device':
            '''
            update channel
            '''
            self._runEvent(eventTyp,channel,self._channels[channel]['events'][eventTyp]) 
        '''
        update device
        '''
        self._runEvent(eventTyp,'device',self._device['events'][eventTyp])
        
        
    def _onchange_event(self,channel):
        self.logger.debug("onchange_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        self._channels[channel]['lastchange']['value']=int(time())
        self._device['lastchange']['value']=int(time())
    
    def _onrefresh_event(self,channel):
        self.logger.debug("onrefresh_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        self._channels[channel]['lastupdate']['value']=int(time())
        self._device['lastupdate']['value']=int(time())
        
    def _onboot_event(self,channel):
        self.logger.debug("onboot_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        
    def _oncreate_event(self,channel):
        self.logger.debug("oncreate_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        self._channels[channel]['create']['value']=int(time())
        
    def _ondelete_event(self,channel):
        self.logger.debug("ondelete_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        
    def _runEvent(self,eventTyp,channel,eventList):
        for eventName in eventList:
            self.logger.debug("channel %s calling: %s event handler"%(channel,eventName))
            self._eventHandlerList[eventName].callback(self,eventTyp,channel)
    
    def _name_(self):
        return "defaultDevice"
    
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
    