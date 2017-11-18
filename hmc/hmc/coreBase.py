'''
Created on 23.09.2017

@author: uschoen
'''
__version__=0.2


import json,os,sys,re,importlib
import logging

class coreBase():
    '''
    classdocs
    '''


    def __init__(self,params):
        '''
        Constructor
        '''
        self.logger=logging.getLogger(__name__)                    # logging instance
        self.args=params                      # configuration parameter
        '''
        all core vars
        '''
        self.gatewaysInstance={}                # hold all gateway threads
                                                # self.gatewaysIntance{
                                                #                        'name':<< name of the gateway >>
                                                #                        'instance':<< object/instance of the gateway >>
                                                #                     }
        self.gatewaysCFG={}                     # gateway threads configuration
        self.devices={}                         # Device objects
        self.eventHandler={}                    # hold the event handler object
        self.eventHandlerCFG={}                 # hold the event handler configuration
             
        self.defaultEventHandler={              #list with default event handler and event typs
                    "onboot_event": [], 
                    "onchange_event": [], 
                    "oncreate_event": [], 
                    "ondelete_event": [], 
                    "onrefresh_event": [], 
                    "onshutdown_event": []}
        
        self.coreClientsCFG={}                  # Core Connection Configuration
        self.ConnectorServer={}                 # Core Lissener Object
        self.CoreClientsConnections={}          # CoreConnection to other Cores
       
        self.onboot_event()
        
        self.logger.info("build %s instance version %s"%(__name__,__version__))
    def shutdown(self):
        self.logger.warning("shutdown core")
        self.onshutdown_event()
    
    def writeJSON(self,filename,data={}):
        self.logger.info("write configuration to %s"%(filename))
        try:
            with open(filename,'w') as outfile:
                json.dump(data, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            self.logger.error("can not find file: %s "%(os.path.normpath(filename)))
            raise
        except ValueError:
            e = sys.exc_info()[1]
            self.logger.error("error in find file: %s "%(os.path.normpath(filename)))
            self.logger.error("json: %s "%(e))
            raise
        except Exception,e:
            self.logger.error("unkown error:", exc_info=True)
            raise
                       
    def loadJSON(self,filename):
        '''
        loading configuration file
        '''
        try:
            with open(os.path.normpath(filename)) as jsonDataFile:
                dateFile = json.load(jsonDataFile)
            return dateFile 
        except IOError:
            self.logger.error("can not file: %s "%(os.path.normpath(filename)))
            raise
        except ValueError:
            e = sys.exc_info()[1]
            self.logger.error("error in file: %s "%(os.path.normpath(filename)))
            self.logger.error("json: %s "%(e))
            raise
        except Exception,e:
            self.logger.error("unkown error",exc_info=True)
            raise         
    
    def eventHome(self,pattern):
        try:
            if re.match('.*@.*\..*',pattern):
                self.logger.debug("find device pattern: %s"%(pattern))
                (event,gatewayHost)=pattern.split("@")
                (gateway,host)=gatewayHost.split(".")
                if host == self.args['global']['host']:
                    self.logger.debug("device %s is on gateway: %s host: %s"%(event,gateway,host))
                    return True
                else:
                    self.logger.debug("device %s is not on host: %s"%(event,host))
                    return False
            
            if re.match('.*@.*',pattern):
                self.logger.debug("find eventObject pattern: %s"%(pattern))
                (event,host)=pattern.split("@")
                if host == self.args['global']['host']:
                    self.logger.debug("event %s  is on host: %s"%(event,host))
                    return True
                else:
                    self.logger.debug("event %s is not on host: %s"%(event,host))
                    return False
            self.logger.error("unkown pattern:%s"%(pattern))       
            return False
        except Exception,e:
            self.loggger.error("can not format pattern %s"%(pattern),exc_info=True)
            return False
    def loadModul(self,pakage,modulName,modulCFG):
        """ load python pakage/module
        
        Keyword arguments:
        pakage -- pakage name 
        modulName -- the name of the gateway typ:strg
        modulCFG -- configuration of the gateway typ:direcorty as dic.
                    ['pakage'] -- pakage name
                    ['modul'] -- modul name
                    ['class'] -- class name
        
        return: class Object
        exception: yes 
        """
        
            
        try:
            pakage=pakage+"."+modulCFG['pakage']+"."+modulCFG['modul']
            self.logger.info("try to load event handler:%s with pakage: %s"%(modulName,pakage))
            ARGUMENTS = (modulCFG['config'],self)  
            module = importlib.import_module(pakage)
            CLASS_NAME = modulCFG['class']
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    self.logger.warning( "Version of %s is %s and can by to low"%(pakage,module.__version__))
                else:
                    self.logger.info( "Version of %s is %s"%(pakage,module.__version__))
            else:
                self.logger.warning( "pakage %s has no version Info"%(pakage))
            return getattr(module, CLASS_NAME)(*ARGUMENTS)
        except Exception,e:
            self.loggger.error("can no load module: %s"%(pakage),exc_info=True)  
            raise