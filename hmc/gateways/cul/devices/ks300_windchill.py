'''
Created on 24.12.2017
@author: uschoen

'''
from hmc.devices.defaultDevice import device

__version__="3.0"


class device(device):
    def _name_(self):
        '''
        give the name of the device back
        
        return str name of the device
        '''
        return "ks300_windchill"
    
    def setChannelValue(self,channelName,value):
        '''
        set value of channel
        ''' 
        channelName=str(channelName)
        channelName=channelName.lower()
        try:
            if not self.ifChannelExist(channelName):
                channelValues={
                        'name':channelName
                        }
                self._core.addDeviceChannel(self.deviceID,channelName,channelValues)
            if channelName=='windchill':
                value=self.__WeatherWindChill(value)
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._device['channels'][channelName]['value']
            self._device['channels'][channelName]['value']=value
            if oldValue<>value:
                self._callEvent('onchange_event',channelName)
            self._callEvent('onrefresh_event',channelName)
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value),exc_info=True)
            raise Exception
        
    def __WeatherWindChill(self,wind):
        '''
        calculate windchill from value to index
        ''' 
        self.logger.debug("calc windchill, wind is:%s"%(wind))  
        if wind == 0:
            return "0"
        elif wind in range(1,6):
            return 1
        elif wind in range(6,12):
            return 2
        elif wind in range(12,20):
            return 3
        elif wind in range(20,29):
            return 4
        elif wind in range(29,39):
            return 5
        elif wind in range(39,50):
            return 6
        elif wind in range(50,62):
            return 7
        elif wind in range(62,75):
            return 8
        elif wind in range(75,89):
            return 9
        elif wind in range(89,103):
            return 10
        elif wind in range(103,117):
            return 11
        elif wind >116:
            return 12
        else:
            self.logger.error("wind  can not macht from 0 - >116 ")  
            return "0" 