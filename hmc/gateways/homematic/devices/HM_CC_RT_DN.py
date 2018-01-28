'''
Created on 09.01.2018
@author: uschoen

'''
from hmc.devices.defaultDevice import device
from homematicParty import partyChannel


__version__="3.1"


class device(device,partyChannel):
    def _name_(self):
        return "HM_CC_RT_DN"
    
    def privateInit(self):
        self._partyFlag=0;
        self._partyTimer=0;
        self._partyChannels={
                "party_start_time":{
                    "flag":1,
                    "value":0},
                "party_start_day":{
                    "flag":2,
                    "value":0},
                "party_start_month":{
                    "flag":4,
                    "value":0},
                "party_start_year":{
                    "flag":8,
                    "value":0},
                "party_stop_time":{
                    "flag":16,
                    "value":0},
                "party_stop_day":{
                    "flag":32,
                    "value":0},
                "party_stop_month":{
                    "flag":64,
                    "value":0},
                "party_stop_year":{
                    "flag":128,
                    "value":0},
                }
    def setChannelValue(self,channelName,value):
        '''
        set value of channel
        ''' 
        channelName=str(channelName)
        channelName=channelName.lower()
        try:
            if channelName in self._partyChannels:
                self._addParty(channelName,value)
                return
            if not channelName in self._device['channels']:
                self.logger.error("channel %s is not exist"%(channelName))
                raise Exception
            self.logger.debug("set channel %s to %s"%(channelName,value))
            oldValue=self._device['channels'][channelName]['value']
            self._device['channels'][channelName]['value']=value           
            if oldValue<>value:
                self._callEvent('onchange_event',channelName)        
            self._callEvent('onrefresh_event',channelName)
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value),exc_info=True)
            raise Exception
    
    def _addSysChannels(self):
        '''
        check if sys channel add, if channel not exists
        add channel to device
        
        raise exception
        '''
        try:
            sysChannels={
                        "partystarttime":0,
                        "partystoptime":0}
            channelValues={}
            for channelName in sysChannels:
                if not self.ifChannelExist(channelName):
                    self.logger.info("add new channel %s"%(channelName))
                    channelValues[channelName]={
                        "value":sysChannels[channelName],
                        "name":channelName
                    }
                    self._core.addDeviceChannel(self.deviceID,channelName,channelValues)
        except:
            self.logger.error("can not add sys channel to temperature device")
            raise  
    
    