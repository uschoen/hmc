'''
Created on 24.12.2017
@author: uschoen

'''
from hmc.devices.defaultDevice import device
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
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._channels[channelName]['value']['value']
            self._channels[channelName]['value']['value']=value
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
            sysChannels=['tempMin24h','tempMax24h','lasttemperature']
            for channelName in sysChannels:
                if not self.ifChannelExist(channelName):
                    self.logger.info("add new channel %s"%(channelName))
                    self.addChannel(channelName,self._defaultChannel(channelName))
        except:
            self.logger.error("can not add sys channel to temperature device")
            raise       
    
    def _defaultChannel(self,channelName):
        '''
        return a dic with sys channel values
        '''
        channelValues={}
        channelValues[channelName]={
                "value":{
                        "value":{},
                        "type":"array"},
                "name":{        
                        "value":channelName,
                        "type":"string"},
                    }
        return channelValues
    
    def calcTemperature(self,temperature):
        '''
        calc the temperature for last 24h
        last temperature
        min temperature 24h
        max temperature 24h
        '''
        return
        self.logger.debug("calc temperature data:%s"%(temperature))
        lastTemperature={}
        try:
            self._addSysChannels()
            self.__clearOldTemp()
            lastTemperature=self.getChannelValue('lasttemperature')
            lastTemperature[int(time())]=temperature
            self.setChannelValue('lasttemperature',lastTemperature)
            self.setChannelValue('tempMin24h', min(lastTemperature.values()))
            self.setChannelValue('tempMax24h', max(lastTemperature.values()))    
        except:
            self.logger.debug("can not calc temperature data",exc_info=True)        

    def __clearOldTemp(self):
        timebefor24=int(time())-86400
        lastTemperature={}
        lastTemperature=self.getChannelValue('lasttemperature')
        self.logger.debug("clear last 24h temperature data where older then %s"%(timebefor24))
        for rainTimeStamp in lastTemperature.copy():
            if rainTimeStamp<timebefor24:
                self.logger.debug("time temperature %s < %s befor"%(rainTimeStamp,timebefor24))
                del lastTemperature[rainTimeStamp]
        self.setChannelValue('lasttemperature',lastTemperature)    
                
                
                
                
                