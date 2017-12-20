'''
Created on 21.10.2016

@author: uschoen



'''
import threading
from time import localtime, strftime
from datetime import datetime
import logging

__version__="2.0"

class sensor(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        self.__core=core
        self.__args=params
        self.logger=logging.getLogger(__name__) 
        self.running=1
        self.logger.debug("build  %s instance with version %s"%(__name__,__version__))
    
    def run(self):
        self.logger.info("%s start"%(__name__))
        while self.running:
            pass
        self.logger.info("%s stop:"%(__name__))   
    
    def shutdown(self):
        self.running=0
        self.logger.critical("stop %s thread"%(__name__))
        
               
    def __log (self,level="unkown",messages="no messages"):
        if self.__logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.__logger.write(conf)
    
    
            
            