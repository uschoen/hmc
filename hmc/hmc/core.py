'''
Created on 23.09.2017

@author: uschoen
'''
__version__ = 0.2

from coreBase import coreBase
from coreGateways import coreGateways
from coreEvents import coreEvents
from coreConfiguration import coreConfiguration
from coreDevice import coreDevices
from coreConnector import coreConnector
from coreEventHandler import coreEventHandler
from coreProgram import coreProgram

class manager(coreBase,coreGateways,coreEvents,coreConfiguration,coreDevices,coreConnector,coreEventHandler,coreProgram,object):
    '''
    classdocs
    '''
    pass


    
        