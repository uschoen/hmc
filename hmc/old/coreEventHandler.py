'''
Created on 23.09.2017

@author: uschoen
'''

__version__ = "3.0"

class coreEventHandler():
    '''
    classdocs
    '''
 
    def addDefaultEventhandler(self,eventTyp,eventHandlerName,forceUpdate=False):
        if eventTyp not in self.defaultEventHandler:
            self.logger.error("can not find event type %s"%(eventTyp))
            return
        if eventHandlerName not in self.eventHandler:
            self.logger.error("can not find event Handler %s"%(eventHandlerName))
            return
        self.logger.info("add event Handler %s for event: %s"%(eventHandlerName,eventTyp))
        self.defaultEventHandler[eventTyp].append(eventHandlerName)
        self.updateRemoteCore(forceUpdate,eventHandlerName,'addDefaultEventhandler',eventTyp,eventHandlerName)
    
    def shutdownAllEventhadnler(self):
        self.logger.critical("shutdown all Eventhandler")
        for eventhandler in self.eventHandler:
            self.logger.critical("shutdown Eventhandler %s"%(eventhandler))
            self.eventHandler[eventhandler].shutdown()
    
    
    def updateEventHandler(self,eventhandlerName,eventhandlerCFG,forceUpdate=False):
        '''
         add a Event handler 
        
        Keyword arguments:
        event handler -- the name of the event handler typ:strg
        eventhandlerCFG -- configuration of the eventhandlerCFG typ:dictionary
        
        return: nothing
        exception: none
        '''
        if eventhandlerName in self.eventHandler:
            self.logger.info("eventHandler %s is existing, delte old eventhandler"%(eventhandlerName))
            del self.eventHandler[eventhandlerName]
        self.__addEventHandler(eventhandlerName,eventhandlerCFG)
        self.updateRemoteCore(forceUpdate,eventhandlerName,'updateEventHandler',eventhandlerName,eventhandlerCFG)
    
    def addEventHandler(self,eventhandlerName,eventhandlerCFG,forceUpdate=False):
        '''
        add a Event handler 
        
        Keyword arguments:
        event handler -- the name of the event handler typ:strg
        eventhandlerCFG -- configuration of the eventhandlerCFG typ:dictionary
        
        return: nothing
        exception: none
        '''
        if eventhandlerName in self.eventHandler:
            self.logger.error("eventHandler %s is existing"%(eventhandlerName))
            return
        self.__addEventHandler(eventhandlerName,eventhandlerCFG)
        self.updateRemoteCore(forceUpdate,eventhandlerName,'addEventHandler',eventhandlerName,eventhandlerCFG)
                
    def __addEventHandler(self,eventhandlerName,eventhandlerCFG):
        '''
         add a Event handler 
        
        Keyword arguments:
        event handler -- the name of the event handler typ:strg
        eventhandlerCFG -- configuration of the eventhandlerCFG typ:dictionary
        
        return: nothing
        exception: none
        '''
        self.eventHandlerCFG[eventhandlerName]=eventhandlerCFG
        if self.eventHome(eventhandlerName):
            self.logger.info("add new eventHandler: %s"%(eventhandlerName))
            try:
                self.eventHandler[eventhandlerName]=self.loadModul("eventhandler",eventhandlerName,eventhandlerCFG)
                self.logger.info("add new eventhandlerName: %s successful"%(eventhandlerName)) 
            except:
                self.logger.error("can not add event handler Name: %s"%(eventhandlerName),exc_info=True)  
        else:
            self.logger.info("eventHandler: %s not on this host"%(eventhandlerName))
            
    
    
    