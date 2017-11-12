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

    def addDefaultEventhandler(self,eventTyp,eventHandlerName):
        if eventTyp not in self.defaultEventHandler:
            self.log("error","can not find event type %s"%(eventTyp))
            return
        if eventHandlerName not in self.eventHandler:
            self.log("error","can not find event Handler %s"%(eventHandlerName))
            return
        self.log("info","add event Handler %s for event: %s"%(eventHandlerName,eventTyp))
        self.defaultEventHandler[eventTyp].append(eventHandlerName)
        
    
    def addEventHandler(self,eventhandlerName,eventhandlerCFG):
        '''
         add a Event handler 
        
        Keyword arguments:
        event handler -- the name of the event handler typ:strg
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
            self.log("info","add new eventhandlerName: %s successful"%(eventhandlerName)) 
            self.eventHandlerCFG[eventhandlerName]=eventhandlerCFG
            self.updateRemoteCore(eventhandlerName,'addEventHandler',eventhandlerName,eventhandlerCFG)
        
        except:
            self.log("error","can not add event handler Name: %s"%(eventhandlerName))  
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Trace back Info:%s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
    
    
    