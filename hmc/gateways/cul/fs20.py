'''
Created on 23.12.2017

@author: uschoen
'''

class fs20device(object):
    '''
    classdocs
    TODO: change all changes on device over the core, not himself
    '''


    def decodeFS20(self,msg):
        self.log.debug("fs20 get code %s"%(msg))
        try:
            deviceID="%s@%s.%s"%(msg[0:6],self.config['gateway'],self.config['host'])
            rssi=self.rssi(int(msg[8:9],16))
            value=str(msg[6:8])
            self.log.debug("fs20 device code is %s"%(deviceID))
            if not self.core.ifDeviceExists(deviceID):
                self.log.debug("add new fs20 device: %s"%(deviceID))
                self.addNewDevice(deviceID,'fs20')
            if not self.core.ifDeviceChannelExist(deviceID,'value'):
                self.addChannel(deviceID,'value')
            self.core.setDeviceChannelValue(deviceID,'value',value)
            if not self.core.ifDeviceChannelExist(deviceID,'rssi'):
                self.addChannel(deviceID,'rssi') 
            self.core.setDeviceChannelValue(deviceID,"rssi",rssi)
        except :
            self.log.critical("can not add or update fs20 device", exc_info=True)

        