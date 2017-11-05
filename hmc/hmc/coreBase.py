'''
Created on 23.09.2017

@author: uschoen
'''
__version__=0.2

from time import localtime, strftime
from datetime import datetime
import json,os,sys,re,importlib



class coreBase():
    '''
    classdocs
    '''


    def __init__(self,params,logger=False):
        '''
        Constructor
        '''
        self.logger=logger                    # logging instance
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
        self.eventHandler={}
        self.eventHandlerCFG={}
        self.ConnectorServer={}             
        self.CoreConnections={}                  # CoreConnection to other Cores
        
        self.onboot_event()
        
        self.log("info","build %s instance version %s"%(__name__,__version__))
    def shutdown(self):
        self.log("warning","shutdown core")
        self.onshutdown_event()
    
    def writeJSON(self,filename,data={}):
        self.log("info","write configuration to %s"%(filename))
        try:
            with open(filename,'w') as outfile:
                json.dump(data, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            self.log("error","can not find file: %s "%(os.path.normpath(filename)))
            raise
        except ValueError:
            e = sys.exc_info()[1]
            self.log("error","error in find file: %s "%(os.path.normpath(filename)))
            self.log("error","json: %s "%(e))
            raise
        except :
            self.log("error","unkown error: %s "%(sys.exc_info()))
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","traceback:"%(msg))
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
            self.log("error","can not find file: %s "%(os.path.normpath(filename)))
            raise
        except ValueError:
            e = sys.exc_info()[1]
            self.log("error","error in find file: %s "%(os.path.normpath(filename)))
            self.log("error","json: %s "%(e))
            raise
        except :
            self.log("error","unkown error: %s "%(sys.exc_info()))
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","traceback:"%(msg))
            raise         
    
    def eventHome(self,pattern):
        try:
            if re.match('.*@.*\..*',pattern):
                self.log("debug","find device pattern: %s"%(pattern))
                (event,gatewayHost)=pattern.split("@")
                (gateway,host)=gatewayHost.split(".")
                if host == self.args['global']['host']:
                    self.log("debug","device %s is on gateway: %s host: %s"%(event,gateway,host))
                    return True
                else:
                    self.log("debug","device %s is not on host: %s"%(event,host))
                    return False
            
            if re.match('.*@.*',pattern):
                self.log("debug","find eventObject pattern: %s"%(pattern))
                (event,host)=pattern.split("@")
                if host == self.args['global']['host']:
                    self.log("debug","event %s  is on host: %s"%(event,host))
                    return True
                else:
                    self.log("debug","event %s is not on host: %s"%(event,host))
                    return False
            self.log("error","unkown pattern:%s"%(pattern))       
            return False
        except Exception as ex:
            self.log("error","can not format pattern %s"%(pattern))
            self.log("error",sys.exc_info())
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:" + str(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
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
            self.log("info","try to load event handler:%s with pakage: %s"%(modulName,pakage))
            ARGUMENTS = (modulCFG['config'],self,self.logger)  
            module = importlib.import_module(pakage)
            CLASS_NAME = modulCFG['class']
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    self.log("warning", "Version of %s is %s and can by to low"%(pakage,module.__version__))
                else:
                    self.log("info", "Version of %s is %s"%(pakage,module.__version__))
            else:
                self.log("warning", "pakage %s has no version Info"%(pakage))
            return getattr(module, CLASS_NAME)(*ARGUMENTS)
        except :
            self.log("error","can not add eventhandlerName: %s"%(pakage))  
            tb = sys.exc_info()
            for msg in tb:
                self.log("error","Traceback Info:%s"%(msg)) 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
            raise
            
            
    def log (self,level="unkown",messages="no messages"):
        if self.logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.logger.write(conf)        