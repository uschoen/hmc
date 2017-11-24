'''
Created on 05.12.2016

@author: uschoen
'''
from hmc.devices.hmcDevices import device
from time import time,sleep

__version__="2.0"

class device(device):
    '''
    classdocs
    '''
    def _name_(self):
        return "ks300_temperatur"    
    
    def setValue(self,Value):
        self.logger.debug("set sensor data to %s"%(Value))
        self.__clearOldTemp()
        if Value==self._attribute['value']['value']:
            if len(self._attribute['lasttemp']['value'].keys()):
                self._attribute['tempMin24h']['value']=min(self._attribute['lasttemp']['value'].values())
                self._attribute['tempMax24h']['value']=max(self._attribute['lasttemp']['value'].values())
            self._onrefresh_event()
        else:
            self._attribute['value']['value']=Value
            self._attribute['lasttemp']['value'][int(time())]=Value
            if len(self._attribute['lasttemp']['value'].keys()):
                self._attribute['tempMin24h']['value']=min(self._attribute['lasttemp']['value'].values())
                self._attribute['tempMax24h']['value']=max(self._attribute['lasttemp']['value'].values())
            self._onrefresh_event()
            self._onchange_event() 
    
    def __clearOldTemp(self):
        timebefor24=int(time())-86400
        temp_temperature=self._attribute['lasttemp']['value']
        self.logger.debug("clear last 24h temperatur data where older then %s"%(timebefor24))
        for rainTimeStamp in temp_temperature.copy():
            self.logger.debug("time temperature %s < %s befor"%(rainTimeStamp,timebefor24))
            if rainTimeStamp<timebefor24:
                del self._attribute['lasttemp']['value'][rainTimeStamp]      
                  
if __name__ == "__main__":

    
    class logger(object):
        def write(self,arg):
            print arg['messages']
    loging=logger()
    hmcDevice = device(loging)
    print("build hmc object")
    print("start thread")
    hmcDevice.setValue(90)
    while True:
        print("main wait 10 sec")
        sleep(10)    