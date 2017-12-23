'''
Created on 23.12.2017
@author: uschoen

'''
from hmc.devices.defaultDevice import device

__version__="2.0"


class device(device):
    def _name_(self):
        return "HMW_IO_12_Sw7_DR"
