'''
Created on 23.12.2017

@author: uschoen
'''

class fs20device(object):
    '''
    classdocs
    '''


    def decodeFS20(self,msg):
        self.__log.debug("fs20 get code %s"%(msg))
        try:
            deviceID="%s@%s.%s"%(msg[0:6],self.__config['gateway'],self.__config['host'])
            rssi=self.__rssi(int(msg[8:9],16))
            self.__log.debug("fs20 device code is %s"%(deviceID))
            if not deviceID in  self.__core.ifDeviceChannelExist(deviceID):
                self.__log.debug("add new fs20 device: %s"%(deviceID))
                self.__addNewDevice(deviceID,'fs20')
            if not self.__core.ifDeviceChannelExist('value'):
                self.__addChannel(deviceID,'value')
            self.__core.setDeviceChannelValue(deviceID,'value',msg[6:8])
            if not self.__core.ifDeviceChannelExist('rssi'):
                self.__addChannel(deviceID,'rssi') 
            self.__core.setDeviceChannelValue(deviceID,"rssi",rssi)
        except :
            self.logger.critical("can not add or update fs20 device", exc_info=True)

        