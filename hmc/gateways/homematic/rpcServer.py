'''
Created on 22.10.2016

@author: uschoen
install :
apt-get install python-xmltodict

'''

__version__= "1.9"

import threading

import xmlrpclib,socket
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import urllib2,xmltodict
from random import randint
import logging



from time import sleep, time




class hmc_rpc_callback:
    def __init__(self,parms,core,timer):
        self.__core=core
        self.__config=parms
        self.__timer=timer
        self.logger=logging.getLogger(__name__) 
    
    def event(self, interfaceID, device, attribute, value,*unkown):
        deviceID=unkown
        attribute=attribute.lower()
        self.__timer()
        try:
            self.logger.debug("event: interfaceID = %s, device: %s, attribute = %s, value = %s" % ( interfaceID,device, attribute, str(value) ))
            deviceID=("%s@%s.%s"%(device,self.__config['gateway'],self.__config['host']))  
            self.logger.debug("deviceID %s"%(deviceID))
        except:
            self.logger.error("error can not add event", exc_info=True)
            return''
        if not self.__core.ifDeviceExists(deviceID):
            self.logger.error("deviceID %s is not exists"%(deviceID))
            return''
        try:
            if self.__config['autoAttribut']:
                if not self.__core.ifDeviceAttributeExist(deviceID,attribute):
                    attributeItem=self.__defaultAttribute(attribute)
                    self.__core.addDeviceAttribute(deviceID,attributeItem)
        except:
            self.logger.error("error to add attribute %s for deviceID %s "%(attribute,deviceID), exc_info=True)
            return ''
        try:
            self.__core.setDeviceAttribute(deviceID,attribute,value)
        except:
            self.logger.error("error can not  add value %s for attribute %s for deviceID %s "%(value,attribute,deviceID), exc_info=True)
        return ''
    def listMethods(self,*args):
        self.__timer()
        self.logger.info("call listMethods for interfaceID %s"%(args))
        return ''
    
    def listDevices(self,*args):
        self.__timer()
        self.logger.info("call listDevices for interfaceID %s"%(args))
        return ''
    
    def newDevices(self, interfaceID, allDevices):
        self.__timer()
        self.logger.debug("call newDevices for interfaceID:%s"%(interfaceID))
        for device in allDevices:
            self.__timer()
            if device['PARENT']=="":
                self.logger.debug("ignore type is parent")
                continue
            deviceID="%s@%s.%s"%(device['ADDRESS'],self.__config['gateway'],self.__config['host'])
            try:
                if not self.__core.ifDeviceExists(deviceID):
                    self.__addDevice(device)
                else:
                    self.logger.info("deviceID is exist: %s"%(deviceID)) 
            except:
                self.logger.warning("can not add deviceID: %s"%(deviceID), exc_info=True) 
        return ''
     
    def __defaultAttribute(self,attribute):
        attribute=attribute.lower()
        tmpAttribute={
                    attribute:{
                        'value':"",
                        'type':"var"}
                   }
        return tmpAttribute
    
    def __addAttribute(self,attribute):
        if self.__config['autoAttribut']:
            try:
                pass
            except:
                pass
            
    def __addDevice(self,device):
        try:
            deviceID="%s@%s.%s"%(device['ADDRESS'],self.__config['gateway'],self.__config['host'])
            self.logger.info("add  newDevices:%s"%(deviceID))
            hmcDevice={
                    "gateway":{
                               "value":"%s"%(self.__config['gateway'])
                              },
                    "deviceID":{
                               "value":deviceID
                              },
                    "enable":{
                               "value":True
                              },
                    "connected":{
                               "value":True
                              },
                    "value":{
                               "value":0
                              },
                    "typ":{
                               "value":"%s"%(device['PARENT_TYPE'])
                              },
                    "host":{
                                "value":self.__config['host']
                            },
                    "package":{
                                "value":self.__config['package']
                            }
                   }  
            self.logger.info("add deviceID %s to core"%(hmcDevice["deviceID"]['value']))
            self.__core.addDevice(hmcDevice)
        except:
            self.logger.warning("can not add deviceID: %s"%(deviceID), exc_info=True) 
        

class server(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self,params,core):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.running=1
        self.__core=core
        self.__timer=int(time())
        self.__timeoutnow=False
        self.__config=self.__defaultConfig()
        self.__config.update(params)
        self.__config['host']=str(socket.gethostbyaddr(socket.gethostname())[0])
        self.logger=logging.getLogger(__name__) 
        self.logger.debug("build  %s instance"%(__name__))
    
    def run(self):
        self.logger.info( "start thread")
        while not self.__adding_server():
            self.logger.error("can not start RPC server wait 120 sec. and try again")
            sleep(120)
        self.logger.info("wait 2 sec to INIT RPC Connect")
        sleep(2)
        self.__RPC_connect()
        self.__RPC_Init()
        while self.running:
            if (self.__timer+self.__config['timeout'] < int(time())):
                self.logger.error("timeout, no messages from homematic")
                if not self.__timeoutnow:
                    self.__sendcommand()
                    self.__timer=int(time())
                    self.__timeoutnow=True
                else:
                    self.__RPC_stop()
                    sleep(1)
                    self.__RPC_Init()
                    self.resetTimer()
            sleep(1) 
        self.logger.warning("thread %s stop"%(__name__))
    
    def __defaultConfig(self):
        attribute={
            "autoAttribut":True,
            "name":"hmc_rpc_rf_default",
            "hm_ip":"127.0.0.1",
            "hm_port":"2000",
            "hm_interface_id":randint(100,999),
            "rpc_port":5050+randint(0,100),
            "rpc_ip":"127.0.0.0",
            "gateway":"hmc_rpc_rf",
            "timeout":280}
        
        return attribute
       
    def __sendcommand(self):
        self.logger.error("send messages to homematic")
        HMurl=self.__config['hmXmlUrl']
        iseID=self.__config['iseID']
        value=self.__config['iseIDValue']
        url=("%s?ise_id=%s&new_value=%s"%(HMurl,iseID,value))
        self.logger.debug("url is %s "%(url))
        try:
            response = urllib2.urlopen(url)
            httcode=response.getcode()
            self.logger.debug("http response code %s"%(httcode))
            if  httcode<>200:
                self.logger.error("can not send request to url") 
                return
            xml=response.read()
            self.logger.debug("xml response %s"%(xml))
            HMresponse=xmltodict.parse(xml)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    self.logger.debug("value successful change")
                elif "not_found" in HMresponse['result']: 
                    self.logger.error("can not found iseID %s"%(iseID))
                else:
                    self.logger.warning("get some unkown answer %s"%(xml))
            else:
                self.logger.warning("get some unkown answer %s"%(xml)) 
        except urllib2.URLError:
            self.logger.error("get some error at url request", exc_info=True)
        except ValueError:
            self.logger.error("some error at request, check configuration", exc_info=True)
        except :
            self.logger.critical("somthing going wrong !!!", exc_info=True)    
        
    def __adding_server(self):
        try:
            self.logger.info("rpc Server %s:%s start"%(self.__config["rpc_ip"],self.__config["rpc_port"]))
            server = SimpleXMLRPCServer((self.__config["rpc_ip"],int(self.__config["rpc_port"])))
            server.logRequests=False
            server.register_introspection_functions() 
            server.register_multicall_functions() 
            server.register_instance(hmc_rpc_callback(self.__config,self.__core,self.resetTimer))
            self.__rpc_server = threading.Thread(target=server.serve_forever)
            self.__rpc_server.start()
            self.logger.info("rpc Server Start")
            return True
        except Exception as e:
            self.logger.error("can not start rpc server", exc_info=True)
            server=False
            return False
    '''
    shutdown
    '''
    def shutdown(self):
        self.logger.critical("rpc Server stop")
        self.__RPC_connect()
        self.__RPC_stop()
        self.logger.critical("rpc Server is stop")
    '''
    Logging Intance
    ''' 
    def __RPC_Init(self):
        self.logger.info("RPC Init: init(http://%s:%i, '%s')" % (self.__config["rpc_ip"],int(self.__config["rpc_port"]), self.__config["hm_interface_id"]) )
        try:
            self.proxy.init("http://%s:%i" % (self.__config["rpc_ip"], int(self.__config["rpc_port"])), self.__config["hm_interface_id"])
            self.logger.debug("Proxy initialized")
        except:
            self.logger.error("Failed to initialize proxy", exc_info=True)
            raise Exception
    def __RPC_connect(self):
        self.logger.debug("Creating proxy. Connecting to http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
        try:
            self.proxy = xmlrpclib.ServerProxy("http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
            self.logger.debug("start rpc data from homematic")
        except:
            self.logger.warning("Failed connecting to proxy at http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])), exc_info=True)
            raise Exception
    def __RPC_stop(self):
        self.logger.debug("stopping RPC data from Homematic. Connecting to http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
        self.logger.info("RPC Init STOP: init(http://%s:%i)" % (self.__config["rpc_ip"],int(self.__config["rpc_port"])) )
        try:
            self.proxy.init("http://%s:%i" % (self.__config["rpc_ip"], int(self.__config["rpc_port"])))
            self.logger.debug("stopped rpc data from homematic")
        except:
            self.logger.error("Failed to stop RPC ", exc_info=True)
            raise Exception
    def resetTimer(self):
        self.logger.debug("reset timeout timer")
        self.__timer=int(time())
        self.__timeoutnow=False