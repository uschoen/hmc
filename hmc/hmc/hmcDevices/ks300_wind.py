'''
Created on 05.12.2016

@author: uschoen
'''
from hmcDevices import defaultDevice
from time import sleep

__version__="2.0"

class device(defaultDevice):
    '''
    classdocs
    '''
    def _name_(self):
        return "ks300_wind"    

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