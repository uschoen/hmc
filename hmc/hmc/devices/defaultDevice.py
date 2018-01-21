'''
Created on 09.12.2017

@author: uschoen
'''

__version__="3.1"

import time
import json
import os
import logging

'''
TODO: check if all channel name convert to lower letters
'''

class device(object):
    
    def __init__ (self,arg,core,adding=False):
        
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
                             "name":{
                                 "value":"unknown",
                                 "type":"string"},
                             "devicegroupe":[],
                             "lastchange":{
                                 "value":"unknown",
                                 "type":"int"},
                             "create":{
                                 "value":int(time.time()),
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
                             "program":{
                                "onchange_event":[],
                                "onrefresh_event":[],
                                "onboot_event":[],
                                "oncreate_event":[],
                                "ondelete_event":[]}
                                }
                         
        
        self._channels={}       # list of all channels
        
        '''
        core objects
        '''
        self._core=core 
        '''
        logger object
        '''                            
        self.logger=logging.getLogger(__name__)             
        '''
        default parameter
        '''
        self.deviceID=arg["device"]['deviceID']["value"]         
        self._packageName=arg["device"]["package"]['value']
        
        if not self._name_()=="defaultDevice":
            self._configurationFile="gateways/%s/devices/%s.json"%(self._packageName.replace(".", "/"),self._name_())
        else:
            self._configurationFile="core/hmc/devices/defaultDevice.json"
        try:         
            packageConfiguration=self._loadJSON(self._configurationFile)
            self._channels.update(packageConfiguration.get('channels',{}))
            self._channels.update(arg.get('channels',{}))
            self._device.update(packageConfiguration.get('device',{}))
            self._device.update(arg.get('device',{}))
        except:
            self.logger.error("can not load channels, %s can not build"%(self._name_()))
            raise
        '''
        call a private init function of the child class, if exists 
        '''
        if  hasattr(self,"privateInit"):
            self.privateInit()
            
        self.logger.debug("build %s instance"%(self._name_()))
        
        '''
        call oncreation event, if add the device
        '''
        if adding:
            self._callEvent('oncreate_event', 'device')
    
    def _deviceGateway(self):
        gateway=self._core.getGatewaysInstance("%s@%s"%(self._device['gateway'],self._device['host']))
        if not gateway:
            pass
    
    def ifEnable(self):
        '''
        check if device enable
        
        return  true if enable
                false is disable
        '''
        return self._device['enable']['value']
    
    def enable(self):
        '''
        set device to enable
        '''
        self.logger.info("enable deviceID %s"%(self._device['deviceID']['value']))   
        self._device['enable']['value']=True
    
    def diable(self):
        '''
        set device to disable
        '''
        self.logger.info("disable deviceID %s"%(self._device['deviceID']['value']))   
        self._device['enable']['value']=False
        
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
        channelName=str(channelName)
        channelName=channelName.lower()
        self.logger.info("add channel %s"%(channelName))
        if channelName in self._channels:
            self.logger.error("channel: %s is exist"%(channelName))
        try:
            newChannel={}
            newChannel=self._channelDefaults()
            newChannel.update(channelValues[channelName])
            self._channels[channelName]=newChannel
            deviceConfiguration=self._loadJSON(self._configurationFile)
            deviceConfiguration['channels']=self._channels
            self._writeJSON(self._configurationFile,deviceConfiguration)
        except:
            self.logger.error("can not add new channel to devicID %s"%(self._device['deviceID']['value']), exc_info=True)
            raise   
        
    def getChannelKey(self,channelName,field):
        '''
        get value of channel
        public function
        '''    
        self.logger.debug("get value for channel:%s"%(channelName))
        try:
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            if not field in self._channels[channelName]:
                self.logger.error("field %s in channel %s is not exist"%(field,channelName))
                raise Exception
            return self._channels[channelName][field]['value']
        except:
            self.logger.error("unknown error in getChannelKey")
            raise 
    
    def getChannelValue(self,channelName):
        '''
        get value of channel
        public function
        '''    
        self.logger.debug("get value for channel:%s"%(channelName))
        try:
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            return self._channels[channelName]['value']['value']
        except:
            self.logger.error("unknown error in getChannelValue")
            raise 
    
       
    def setChannelValue(self,channelName,value):
        '''
        set value of channel
        ''' 
        channelName=str(channelName)
        channelName=channelName.lower()
        try:
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._channels[channelName]['value']['value']
            self._channels[channelName]['value']['value']=value
            try:
                if oldValue<>value:
                    self._callEvent('onchange_event',channelName)
                self._callEvent('onrefresh_event',channelName)
            except:
                self.logger.error("can not excequet events")
                raise Exception
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value))
            raise Exception
        
    def getConfiguration(self):
        '''
        return the configuration from the device
        '''
        configuration={}
        configuration['device']=self._device
        configuration['channels']=self._channels
        return configuration
    
    def addProgramEvent(self,eventTyp,programName,channelName):
        '''
        registerEventHandler old name
        register new event handler for channel or device
        '''
        self.logger.debug("register new program %s for event %s on channel %s"%(eventTyp,programName,channelName))
        if channelName=='device':
            '''
            for device events
            '''
            if programName in self._device['program'][eventTyp]:
                self.logger.warning("event handler %s for program %s is all ready registerd"%(eventTyp,programName))
                return
            self._device['program'][eventTyp].append(programName)
        else:
            '''
            for channel events
            ''' 
            if programName in  self._channels[channelName]['program'][eventTyp]:
                self.logger.warning("event handler %s for program %s is all ready registerd"%(eventTyp,programName))
                return
            self._channel[channelName]['program'].append(programName)
        
    
    def ifChannelExist(self,channelName):
        '''
        return true if channel exists
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        if channelName in self._channels:
            return True
        return False
    
    def _channelDefaults(self,channelName="unknown",varType="string"):
        '''
        return the channel default
        '''
        defaultVar=0
        if varType=="array":
            defaultVar={}
        channel={
            "value":{
                "value":defaultVar,
                "type":varType},
            "name":{        
                "value":channelName,
                "type":"string"},
            "channelID":{        
                "value":channelName,
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
                "value":int(time.time()),
                "type":"int"},
            "enable":{
                "value":True,
                "type":"bool"},
            "program":{
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
        try:
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
                self._runProgram(eventTyp,channel,self._channels[channel]['program'][eventTyp]) 
            '''
            update device
            '''
            self._runProgram(eventTyp,'device',self._device['program'][eventTyp])
        except:
            self.logger.error("can not excequed event",exc_info=True)
            raise Exception
        
    def _onchange_event(self,channel):
        self.logger.debug("onchange_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        self._channels[channel]['lastchange']['value']=int(time.time())
        self._device['lastchange']['value']=int(time.time())
    
    def _onrefresh_event(self,channel):
        self.logger.debug("onrefresh_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        self._channels[channel]['lastupdate']['value']=int(time.time())
        self._device['lastupdate']['value']=int(time.time())
        
    def _onboot_event(self,channel):
        self.logger.debug("onboot_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        
    def _oncreate_event(self,channel):
        self.logger.debug("oncreate_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        self._channels[channel]['create']['value']=int(time.time())
        
    def _ondelete_event(self,channel):
        self.logger.debug("ondelete_event: %s for channel: %s"%(self._device['deviceID']['value'],channel))
        
    def _runProgram(self,eventTyp,channelName,programList):
        for programName in programList:
            if programName not in self.program:
                self.logger.warning("can not found program: %s"%(programName))
                continue
            self.logger.debug("channel %s calling program: %s"%(channelName,programName))
            try:
                self.runProgram(self._device['deviceID']['value'],channelName,eventTyp,programName)
            except:
                self.logger.debug("error at calling: %s event handler"%(programName),exc_info=True)
    
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
            self.logger.error("can not find file: %s "%(os.path.normpath(filename)), exc_info=True)
            raise
        except ValueError:
            self.logger.error("error in file: %s "%(os.path.normpath(filename)), exc_info=True)
            raise
        except:
            self.logger.error("unknown error",exc_info=True)
            raise 
    