'''
Created on 09.01.2018
@author: uschoen

'''
from hmc.devices.defaultDevice import device

__version__="3.0"


class device(device):
    def _name_(self):
        return "HMW_IO_12_Sw7_DR"
