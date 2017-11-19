'''
Created on 19.11.2017
@author: uschoen

'''
from hmc.devices.hmcDevices import device

__version__="2.0"


class device(device):
    def _name_(self):
        return "HM-CC-RT-DN"
