'''
Created on 24.12.2017
@author: uschoen

'''
from gateways.hmc.devices.defaultDevice import device

__version__="3.0"


class device(device):
    def _name_(self):
        return "ks300_wind"
