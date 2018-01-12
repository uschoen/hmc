'''
Created on 21.01.2018

@author: uschoen

'''


import time
import threading
import logging

__version__="3.1"

class server(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        '''
         core instance
        '''
        self.__core=core
        '''
         configuration Items
        '''
        self.__args=params
        ''' 
        logger instance
        '''
        self.__log=logging.getLogger(__name__)
        '''
        running flag to stop the gateway
        '''
        self.running=1
        self.logger.debug("build  %s instance with version %s"%(__name__,__version__))
    
    def run(self):
        self.logger.info("%s start"%(__name__))
        while self.running:
            ''' do what you want, '''
            time.sleep(0.1)
        self.logger.info("%s stop:"%(__name__))   
    
    def shutdown(self):
        self.running=0
        self.logger.critical("stop %s thread"%(__name__))