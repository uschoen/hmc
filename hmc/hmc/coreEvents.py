'''
Created on 23.09.2017

@author: uschoen
'''

__version__ = "2.0"


class coreEvents():
    '''
    classdocs
    '''


    def onboot_event(self):
        self.logger.info("core onboot_event is calling")
        self.loadAllConfiguration()
        
    def onshutdown_event(self):
        self.logger.info("core onshutdown_event is calling")
        self.shutdownAllGateways()
        self.writeAllConfiguration()
    