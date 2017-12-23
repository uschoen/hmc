'''
Created on 23.12.2017

@author: uschoen
'''

class ws300device(object):
    '''
    classdocs
    '''
    def decodeWs300weather(self,msg):
        try:
            self.log.debug("weather decode: %s length %i" %(msg,len(msg)))
            split_msg=list(msg)
            if int(split_msg[1])==0:
                self.log.debug("typ is AS3:%s"%(split_msg[1]))
            elif int(split_msg[1])==1:
                self.log.debug("typ is AS2000, ASH2000, S2000, S2001A, S2001IA, ASH2200, S300IA:%s"%(split_msg[1]))
            elif int(split_msg[1])==2:
                self.log.debug("typ is S2000R:%s"%(split_msg[1]))
            elif int(split_msg[1])==3:
                self.log.debug("typ is S2000W:%s"%(split_msg[1]))
            elif int(split_msg[1])==4:
                self.log.debug("typ is S2001I, S2001ID:%s"%(split_msg[1]))
            elif int(split_msg[1])==5:
                self.log.debug("typ is S2500H:%s"%(split_msg[1]))
            elif int(split_msg[1])==6:
                self.log.debug("typ is Pyrano (Strahlungsleistung):%s"%(split_msg[1]))
            elif int(split_msg[1])==7 and len(msg)==16:
                self.log.debug("typ is ks300:%s"%(split_msg[1]))
                self.__ks300Device(msg)
            else:
                self.log.info("typ is unknown:%s length %i"%(split_msg[1],len(msg)))
        except:
            self.log.error("can not decode weather data", exc_info=True)
    
    def __ks300Device(self,msg):
        self.log.debug("ks300 get code %s"%(msg))
        try:
            if len(msg)<>16:
                self.log.error( "incorrect message lenght: %s"%(len(msg)))
                return
            splitMsg=list(msg)
            rssi=self.rssi(int(splitMsg[14]+splitMsg[15],16))
    
            ''' 
            temperature 
            '''
            deviceID="ks300_temperature@%s.%s"%(self.config['gateway'],self.config['host'])
            value=float(splitMsg[5]+splitMsg[2]+"."+splitMsg[3])
            if splitMsg[0] >="8":
                value=value*(-1)
            self._addWS300(deviceID,'ks300_temperature','temperature',value,rssi)
            '''
            humidity
            '''
            deviceID="ks300_humidity@%s.%s"%(self.config['gateway'],self.config['host'])
            value=int(splitMsg[7]+splitMsg[4])
            self._addWS300(deviceID,'ks300_humidity','humidity',value,rssi)
                
            ''' wind '''
            deviceID="ks300_wind@%s.%s"%(self.config['gateway'],self.config['host'])
            value=int(splitMsg[8]+splitMsg[9]+splitMsg[6])/10
            self._addWS300(deviceID,'ks300_wind','wind',value,rssi)
            
            ''' windchill '''
            deviceID="ks300_windchill@%s.%s"%(self.config['gateway'],self.config['host'])
            value=int(splitMsg[8]+splitMsg[9]+splitMsg[6])/10
            self._addWS300(deviceID,'ks300_windchill','windchill',value,rssi)
            
            ''' rain '''
            deviceID="ks300_rain@%s.%s"%(self.config['gateway'],self.config['host'])
            value=int(splitMsg[13]+splitMsg[10]+splitMsg[11],16)
            self._addWS300(deviceID,'ks300_rain','rain',value,rssi)
            
        except :
            self.log.critical("can not update ks300", exc_info=True)

    def _addWS300(self,deviceID,deviceTyp,channelName,value,rssi):
        try:
            '''
            if device exists
            '''
            if not self.core.ifDeviceExists(deviceID):
                self.log.info("add new deviceID: %s"%(deviceID))    
                self.addNewDevice(deviceID,deviceTyp)
            
            '''
            if channel exists
            '''
            if not self.core.ifDeviceChannelExist(deviceID,channelName):
                self.log.info("add new channel %s for deviceID: %s"%(channelName,deviceID)) 
                self.addChannel(deviceID,channelName)
            '''
            set channel
            '''
            self.log.info("set channel %s to value: %s"%(channelName,value)) 
            self.core.setDeviceChannelValue(deviceID,channelName,value)
            '''
            if channel rssi exists
            '''
            if not self.core.ifDeviceChannelExist(deviceID,rssi):
                self.log.info("add new channel rssi to deviceID: %s"%(deviceID)) 
                self.addChannel(deviceID,rssi)
            '''
            set rssi value
            '''
            self.log.info("add set channel rssi to value: %s"%(value)) 
            self.core.setDeviceChannelValue(deviceID,"rssi",rssi)
        except:
            self.log.error("can not add ws300 deviceID %s"%(deviceID),exc_info=True)