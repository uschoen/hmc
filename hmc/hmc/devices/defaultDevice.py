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
        self._device={      "deviceID":"unknown@unknown.unknown",
                            "devicetype":"defaultDevice",
                            "package":"hmc.devices",
                            "name":"unknown",
                            "devicegroupe":[],
                            "lastchange":0,
                            "create":int(time.time()),
                            "lastupdate":0,
                            "gateway":"unknown",
                            "enable":True,
                            "program":{
                                "onchange_event":[],
                                "onrefresh_event":[],
                                "onboot_event":[],
                                "oncreate_event":[],
                                "ondelete_event":[]},
                            "channels":{}
                        }
        
        self._defaultChannel={
                            "value":0,
                            "name":"unknown",
                            "devicegroupe":[],
                            "lastchange":0,
                            "create":int(time.time()),
                            "lastupdate":0,
                            "gateway":"unknown",
                            "enable":True,
                            "program":{
                                "onchange_event":[],
                                "onrefresh_event":[],
                                "onboot_event":[],
                                "oncreate_event":[],
                                "ondelete_event":[]
                                        }
                            }
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
        self.deviceID=arg.get('deviceID',"unknown@unknown.unknown")        
        self.packageName=arg.get('package')
        
        
        deviceConfigPath="gateways/%s/devices/%s.json"%(self._packageName.replace(".", "/"),self._name_())
        if self._name_()=="defaultDevice":
            deviceConfigPath="core/hmc/devices/defaultDevice.json"
        try:         
            deviceConfiguration=self._loadJSON(deviceConfigPath)
            self._device.update(deviceConfiguration,{})
        except:
            self.logger.error("can not load device configuration, %s can not build"%(self._name_()))
            raise Exception
        '''
        call a private init function of the child class, if exists 
        '''
        if  hasattr(self,"privateInit"):
            self.privateInit()
        
        self.gateway=self._core.getGatewaysInstance(self._device.get('gateway',None))  
        
        self.logger.debug("build %s instance"%(self._name_()))
        
        '''
        call oncreation event, if add the device
        '''
        if adding:
            self._callEvent('oncreate_event', 'device')
    
    def ifEnable(self):
        '''
        check if device enable
        
        return  true if enable
                false is disable
        '''
        return self._device.get('enable',False)
    
    def changeChannelValue(self,channelName,value):
        channelName=str(channelName)
        channelName=channelName.lower()
        try:
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            self.logger.info("device has no change channel function") 
        except:
            self.logger.error("can not change deviceID %s channel:%s to value %s"%(self.deviceID,channelName,value)) 
                 
    def enable(self):
        '''
        set device to enable
        '''
        self.logger.info("enable deviceID %s"%(self.deviceID))   
        self._device['enable']=True
    
    def diable(self):
        '''
        set device to disable
        '''
        self.logger.info("disable deviceID %s"%(self.deviceID))   
        self._device['enable']=False
        
    def delete(self):
        '''
        delete function of the device
        '''
        
        self.logger.info("delete device %s"%(self.deviceID))    
        self.logger.warning("delete device not implemented")       
        self._callEvent('ondelete_event','device')
    
    def getAllChannel(self):
        '''
        return all channels of the device as array
        '''
        self.logger.debug("get all channel for deviceID:%s"%(self.deviceID))
        return self._device.get('channels',{}).keys()
    
    def addChannel(self,channelName,channelValues):
        '''
        add a new channel
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        self.logger.info("add channel %s"%(channelName))
        if channelName in self._channels:
            self.logger.error("channel: %s is exist"%(channelName))
            raise Exception
        try:
            newChannel=self._defaultChannel
            newChannel.update(channelValues.get(channelName,{}))
            self._device['channels'][channelName]=newChannel
            self._writeJSON(self._configurationFile,self._device)
        except:
            self.logger.error("can not add new channel to devicID %s"%(self.deviceID), exc_info=True)
            raise   
    
    def getChannelKey(self,channelName,key):
        '''
        get value of channel
        public function
        '''    
        self.logger.debug("get value for channel:%s"%(channelName))
        try:
            if not channelName in self._device['channels']:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            if not key in self._device['channels'][channelName]:
                self.logger.error("field %s in channel %s is not exist"%(key,channelName))
                raise Exception
            return self._device['channels'][channelName][key]
        except:
            self.logger.error("unknown error in getChannelKey")
            raise Exception
    
    def getChannelValue(self,channelName):
        '''
        get value of channel
        public function
        '''    
        self.logger.debug("get value for channel:%s"%(channelName))
        try:
            if not channelName in self._devices['channels']:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            return self._devices['channels'][channelName]['value']
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
            if not channelName in self._device['channels']:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._device['channels'][channelName]['value']
            self._device['channels'][channelName]['value']=value
            try:
                if oldValue<>value:
                    self._callEvent('onchange_event',channelName)
                self._callEvent('onrefresh_event',channelName)
            except:
                self.logger.error("can not excequet events")
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value))
            raise Exception
        
    def getConfiguration(self):
        '''
        return the configuration from the device
        '''
        return self._device
    
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
            if programName in  self._device['channels'][channelName]['program'][eventTyp]:
                self.logger.warning("event handler %s for program %s is all ready registerd"%(eventTyp,programName))
                return
            self._device['channels'][channelName]['program'].append(programName)
        
    def ifChannelExist(self,channelName):
        '''
        return true if channel exists
        '''
        channelName=str(channelName)
        channelName=channelName.lower()
        if channelName in self._device['channels']:
            return True
        return False
    
    def _callEvent(self,eventTyp,channelName):
        '''
        eventTyps:
        onchange_event
        onrefresh_event
        onboot_event
        oncreate_event
        ondelete_event
        '''
        try:
            self.logger.debug("call event: %s for channel: %s, for deviceID:%s"%(eventTyp,channelName,self.deviceID))
            if channelName not in self._device['channels'] and not channelName=='device':
                '''
                check if channel exist
                '''
                self.logger.warning("channel %s not exists in deviceID %s"%(channelName,self.deviceID))
                return 
            
            if not channelName=='device':
                '''
                select event type
                '''
                if eventTyp=='onchange_event':
                    self._onchange_event(channelName)
                elif eventTyp=='onrefresh_event':
                    self._onrefresh_event(channelName)
                elif eventTyp=='onboot_event':
                    self._onboot_event(channelName)
                elif eventTyp=='oncreate_event':
                    self._oncreate_event(channelName)
                elif eventTyp=='ondelete_event':   
                    self._ondelete_event(channelName)
                else:
                    self.logger.warning("event type %s is unknown"%(eventTyp))
                    return     
            
            if not channelName=='device':
                '''
                update channel
                '''
                self._runProgram(eventTyp,channelName,self._device['channels'][channelName]['program'][eventTyp]) 
            '''
            update device
            '''
            self._runProgram(eventTyp,'device',self._device['program'][eventTyp])
        except:
            self.logger.error("can not excequed event",exc_info=True)
            raise Exception
       
    def _onchange_event(self,channelName):
        self.logger.debug("onchange_event: %s for channel: %s"%(self.deviceID,channelName))
        self._device['channels'][channelName]['lastchange']=int(time.time())
        self._device['lastchange']=int(time.time())
    
    def _onrefresh_event(self,channelName):
        self.logger.debug("onrefresh_event: %s for channel: %s"%(self.deviceID,channelName))
        self._device['channels'][channelName]['lastupdate']=int(time.time())
        self._device['lastupdate']=int(time.time())
        
    def _onboot_event(self,channelName):
        self.logger.debug("onboot_event: %s for channel: %s"%(self.deviceID,channelName))
        
    def _oncreate_event(self,channelName):
        self.logger.debug("oncreate_event: %s for channel: %s"%(self.deviceID,channelName))
        self._device['channels'][channelName]['create']['value']=int(time.time())
        
    def _ondelete_event(self,channelName):
        self.logger.debug("ondelete_event: %s for channel: %s"%(self.deviceID,channelName))
        
    def _runProgram(self,eventTyp,channelName,programList):
        for programName in programList:
            if programName not in self._core.program:
                self.logger.warning("can not found program: %s"%(programName))
                continue
            self.logger.debug("channel %s calling program: %s"%(channelName,programName))
            try:
                self._core.runProgram(self.deviceID,channelName,eventTyp,programName)
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
    