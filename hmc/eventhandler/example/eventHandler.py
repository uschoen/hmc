'''
Created on 18.12.2016

@author: uschoen
'''
__version__ = "2.0"

import logging

class server(object):
    '''
    classdocs
    '''


    def __init__(self,parms,core):
        '''
        self.__core=reference to the core object and functions 
         '''
        self.__core=core
        '''
        self.__config=    all parameter from the configuration file 
                          in the config section.
        '''
        self.__config=parms
        '''
        logging intance
        
        use:
        self.logger.LEVEL(MSG)
        ->LEVEL are the default python debug level
        ->MSG are the message
        '''
        
        self.logger=logging.getLogger(__name__)     
        ("debug","build  %s instance"%(__name__))
    
    def callback(self,device):
        pass
        ''''
        function is calling from the devices for selcted events 
        like __onchange, __onrefrech etc
        '''
    def shutdown(self):
        self.logger.critical("%s is shutdown"%(__name__))
              
if __name__ == "__main__":      