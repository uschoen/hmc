'''
Created on 23.12.2017

@author: uschoen
'''
__verion__=3.0
class fs20device(object):
    '''
    classdocs
    
    '''


    def decodeFS20(self,msg):
        self.log.debug("fs20 get code %s"%(msg))
        channelNameDevice="value"
        channelNameRSSI='rssi'
        try:
            FSID="%s"%(msg[0:6])
            deviceID="%s@%s.%s"%(msg[0:6],self.config['package'],self.config['host'])
            rssi=self.rssi(int(msg[8:9],16))
            value=str(msg[6:8])
            self.log.debug("fs20 deviceID is %s"%(deviceID))
            
            if not self.core.ifDeviceExists(deviceID):
                '''
                add device
                '''
                self.addNewDevice(deviceID,'fs20',FSID)
            
            if not self.core.ifDeviceChannelExist(deviceID,channelNameDevice):
                ''' 
                add channel value
                '''
                self.addChannel(deviceID,channelNameDevice,0)
            self.core.setDeviceChannelValue(deviceID,channelNameDevice,value)
            
            if not self.core.ifDeviceChannelExist(deviceID,channelNameRSSI):
                '''
                add channel RSSI
                '''
                self.addChannel(deviceID,channelNameRSSI,0) 
            self.core.setDeviceChannelValue(deviceID,channelNameRSSI,rssi)
        except :
            self.log.critical("can not add or update fs20 device", exc_info=True)

        