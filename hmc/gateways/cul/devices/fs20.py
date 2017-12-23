'''
Created on 23.12.2017
@author: uschoen

'''
from hmc.devices.defaultDevice import device

__version__="2.0"


class device(device):
    def _name_(self):
        return "fs20"
