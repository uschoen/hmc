'''
Created on 24.12.2017
@author: uschoen

'''
from gateways.hmc.devices.defaultDevice import device
from time import time
 
__version__="3.0"


class device(device):
    def _name_(self):
        return "ks300_rain"
    
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
            if oldValue<>value:
                self._callEvent('onchange_event',channelName)
            self._callEvent('onrefresh_event',channelName)
            
        except:
            self.logger.error("can not set channel %s to %s"%(channelName,value))
            raise Exception
    
    def _caclRain(self,RAWvalue):
        self.logger.debug("calc rain")
        try:
            self._addSysChannels()
            self._clearOldRain()
            if self.getChannelValue('rain')==0:
                '''
                first start
                '''
                self.logger.info("first start of ks300_rain, need more data to calculate")
                return
        except:
            self.logger.error("can not calc rain",exc_info=True)
            
            
    def _addSysChannels(self):
        '''
        check if sys channel add, if channel not exists
        add channel to device
        
        raise exception
        '''
        try:
            sysChannels={
                        "rain24H":0,
                        "rain1h":0,
                        "lastrain":[]}
            for channelName in sysChannels:
                if not self.ifChannelExist(channelName):
                    channelValues={
                        'name':channelName,
                        'value':sysChannels[channelName]}
                    self._core.addDeviceChannel(self.deviceID,channelName,channelValues)
        except:
            self.logger.error("can not add sys channel to temperature device")
            raise 
    
    def oldsetValue(self,RAWvalue):
        '''
        check ist rain  value have change
        '''
        self.__rainMM=0.2469
        self.__clearOldRain()
        if self._attribute['firststart']['value']:
            self._attribute['lastrain']['value']=RAWvalue
            self._attribute['firststart']['value']=False
            self._log("debug","set  "+self._name_()+" firststart to false") 
            return
        
        if RAWvalue==self._attribute['lastrain']['value']:
            self._onrefresh_event()
            return
        
        rainDelta=RAWvalue-self._attribute['lastrain']['value']
        
        self._log("debug","RAWvalue:%s lastRAWvalue:%s delta:%s"%(RAWvalue,self._attribute['lastrain']['value'],rainDelta))
        
        if rainDelta<0:
            self._log("error","rain delta negativ") 
            
        self._attribute['lastrain']['value']=RAWvalue
        self._attribute['value']['value']=rainDelta*self.__rainMM 
        self._log("data", "rain set to %s"%(self._attribute['value']['value']))
        self._attribute['lastrain24']['value'][int(time())]=float(rainDelta*self.__rainMM)
        self._attribute['lastrain1h']['value'][int(time())]=float(rainDelta*self.__rainMM)
        self._attribute['rain24h']['value']=self.__calcRain24mm()
        self._attribute['rain1h']['value']=self.__calcRain1hmm()
        
        self._onrefresh_event()
        self._onchange_event()
    
    def _clearOldRain(self): 
        pass
    def old__clearOldRain(self):
        timebefor24=int(time())-86400
        timebefor1h=int(time())-3600
        self._attribute['lastrain1h']['value']={}
        temp_rain=self._attribute['lastrain24']['value']
        self._log("debug","clear rain data where older then %s"%(timebefor24))
        for rainTimeStamp in temp_rain:
            self._log("data","time rain %s < %s befor"%(rainTimeStamp,timebefor24))
            if rainTimeStamp>timebefor1h:
                self._attribute['lastrain1h']['value'][rainTimeStamp]= self._attribute['lastrain24']['value'][rainTimeStamp]
            if rainTimeStamp<timebefor24:
                del  self._attribute['lastrain24']['value'][rainTimeStamp]
                self._log("debug","delete rain data with time %s"%(rainTimeStamp))
               
    def __calcRain24mm(self):
        rain24=0
        for rainTimeStamp in self._attribute['lastrain24']['value']:
            rain24=rain24+(self._attribute['lastrain24']['value'][rainTimeStamp]*self.__rainMM)
        return rain24
    def __calcRain1hmm(self):
        rain1h=0
        for rainTimeStamp in self._attribute['lastrain1h']['value']:
            rain1h=rain1h+(self._attribute['lastrain1h']['value'][rainTimeStamp]*self.__rainMM)
        return rain1h