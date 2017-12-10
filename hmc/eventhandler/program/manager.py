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
        Constructor
         '''
        self.__core=core
        self.__config=parms
        self.logger=logging.getLogger(__name__) 
        ("debug","build  %s instance"%(__name__))
    
    def callback(self,device):
        self.logger.debug("call program manager from deviceID:%s"%(device['deviceID']['value']))
    
    def shutdown(self):
        self.logger.critical("%s is shutdown"%(__name__))
        
               
if __name__ == "__main__":   
    pass   