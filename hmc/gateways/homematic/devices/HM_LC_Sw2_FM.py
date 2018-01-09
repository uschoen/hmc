'''
Created on 09.01.2018
@author: uschoen

'''
from hmc.devices.defaultDevice import device

__version__="3.0"


class device(device):
    def _name_(self):
        return "HM_LC_Sw2_FM"
