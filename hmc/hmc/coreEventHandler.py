'''
Created on 23.09.2017

@author: uschoen
'''

__version__ = "2.0"

import re,os,sys

class coreEventHandler():
    '''
    classdocs
    '''


    def addEventHandler(self,eventhandlerName,eventhandlerCFG):
        self.log("info","addEventHandler")
        '''
         add a Eventhandler 
        
        Keyword arguments:
        eventhandler -- the name of the eventhandler typ:strg
        eventhandlerCFG -- configuration of the eventhandlerCFG typ:dictionary
        
        return: nothing
        exception: none
        '''
        if not re.match('.*@.*',eventhandlerName):
            self.log("error","eventHandler %s have wrong format"%(eventhandlerName))    
            return
        #if not self.eventHome(eventhandlerName):
        #    self.log("error","eventHandler %s is not at this core home"%(eventhandlerName))    
        #    return
        if eventhandlerName in self.eventHandler:
            self.log("error","eventHandler %s is existing"%(eventhandlerName))
            return
        self.log("info","add new eventHandler: %s"%(eventhandlerName))
        
        try:  
            self.eventHandler[eventhandlerName]=self.loadModul("eventhandler",eventhandlerName,eventhandlerCFG)
            self.log("info","add new eventhandlerName: %s suscesful"%(eventhandlerName)) 
            self.eventHandlerCFG[eventhandlerName]=eventhandlerCFG
            self.updateRemoteCore(eventhandlerName,'addEventHandler',eventhandlerName,eventhandlerCFG)
        
        except:
            self.log("error","can not add eventhandlerName: %s"%(eventhandlerName))  
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:%s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
    
    
    