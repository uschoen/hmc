'''
Created on 18.12.2016

@author: uschoen
'''
__version__ = "2.0"


from time import localtime, strftime,sleep
from datetime import datetime
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
        pass
  
            
            
            
            
if __name__ == "__main__":      