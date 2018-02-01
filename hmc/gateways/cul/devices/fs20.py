'''
Created on 24.12.2017
@author: uschoen

'''
from gateways.hmc.devices.defaultDevice import device

__version__="3.0"


class device(device):
    def _name_(self):
        return "fs20"
    
    def changeChannelValue(self,channelName,value):
        channelName=str(channelName)
        channelName=channelName.lower()
        try:
            if not channelName in self._channels:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            self.logger.info("device has no change channel function") 
            #self.gateway.send("")
        except:
            self.logger.error("can not change deviceID %s channel:%s to value %s"%(self._device['deviceID']['value'],channelName,value)) 