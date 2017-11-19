'''
Created on 05.12.2016

@author: uschoen
'''
from hmc.devices.hmcDevices import device


__version__="2.0"


class device(device):
    '''
    classdocs
    '''
    def _name_(self):
        return "ds1820"    

