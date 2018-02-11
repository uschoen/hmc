'''
Created on 23.09.2017

@author: uschoen
'''
__version__ = 0.2

from coreBase import coreBase
from coreGateways import coreGateways
from coreConfiguration import coreConfiguration
from coreEvents import coreEvents
from coreDevice import coreDevices
from coreClients import coreClients
from coreProgram import coreProgram

class manager(coreBase,coreGateways,coreEvents,coreConfiguration,coreDevices,coreClients,coreProgram,object):
    '''
    classdocs
    '''
    pass


    
        