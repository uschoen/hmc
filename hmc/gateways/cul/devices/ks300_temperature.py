'''
Created on 24.12.2017
@author: uschoen

'''
from gateways.hmc.devices.defaultDevice import device
from time import time

__version__="3.0"


class device(device):
    def _name_(self):
        return "ks300_temperature"
    
    def setChannelValue(self,channelName,value):
        '''
        set value of channel
        ''' 
        channelName=str(channelName)
        channelName=channelName.lower()
        try:
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._device['channels'][channelName]['value']
            self._device['channels'][channelName]['value']=value
            if channelName=='lasttemperature':
                return
            if oldValue<>value:
                self._callEvent('onchange_event',channelName)
                if channelName=='temperature':
                    self.calcTemperature(value)
            self._callEvent('onrefresh_event',channelName)
            
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value))
            raise Exception
         
     
    def _addSysChannels(self):
        '''
        check if sys channel add, if channel not exists
        add channel to device
        
        raise exception
        '''
        try:
            sysChannels={
                        "tempmin24h":"0",
                        "tempmax24h":"0",
                        "lasttemperature":{}}
            for channelName in sysChannels:
                if not self._core.ifDeviceChannelExist(self.deviceID,channelName):
                    self.logger.info("add new channel %s"%(channelName))
                    channelValues={
                        'name':channelName,
                        'value':sysChannels[channelName]}
                    self._core.addDeviceChannel(self.deviceID,channelName,channelValues)
        except:
            self.logger.error("can not add sys channel to temperature device")
            raise 
    
    def calcTemperature(self,temperature):
        '''
        calc the temperature for last 24h
        last temperature
        min temperature 24h
        max temperature 24h
        '''
        self.logger.debug("calc temperature data:%s"%(temperature))
        lastTemperature={}
        try:
            self._addSysChannels()
            self.__clearOldTemp()
            lastTemperature=self._core.getDeviceChannelValue(self.deviceID,'lasttemperature')
            if not lastTemperature:
                lastTemperature={}
            lastTemperature[int(time())]=temperature
            self._core.setDeviceChannelValue(self.deviceID,'lasttemperature',lastTemperature)
            self._core.setDeviceChannelValue(self.deviceID,'tempmin24h', min(lastTemperature.values()))
            self._core.setDeviceChannelValue(self.deviceID,'tempmax24h', max(lastTemperature.values()))    
        except:
            self.logger.debug("can not calc temperature data",exc_info=True)        

    def __clearOldTemp(self):
        timebefor24=int(time())-86400
        lastTemperature={}
        lastTemperature=self.getChannelValue('lasttemperature')
        if not lastTemperature:
            return
        self.logger.info("clear last 24h temperature data where older then %s"%(timebefor24))
        for rainTimeStamp in lastTemperature.copy():
            if rainTimeStamp<timebefor24:
                self.logger.debug("time temperature %s < %s befor"%(rainTimeStamp,timebefor24))
                del lastTemperature[rainTimeStamp]
        self._core.setDeviceChannelValue(self.deviceID,'lasttemperature',lastTemperature)    
                
                
                
                
                