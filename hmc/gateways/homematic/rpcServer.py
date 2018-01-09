'''
Created on 22.10.2016

@author: uschoen
install :
sudo apt-get install python-xmltodict


'''

__version__= "3.1"

import threading
import logging
import time
from random import randint
import xmlrpclib                                            #@UnresolvedImport
from SimpleXMLRPCServer import SimpleXMLRPCServer           #@UnresolvedImport
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport


class hmcRPCcallback:
    '''
    call back function from the RPC Server
    to handle request
    '''
    def __init__(self,parms,core,resetTimer):
        ''' core instance '''
        self.__core=core
        ''' configuration parameter  '''
        self.__config={
                        "gateway":"unknown",
                        "host":"unknown"
                      }
        self.__config=parms
        ''' reset timer function '''
        self.__resetTimer=resetTimer
        ''' logging instance '''
        self.__log=logging.getLogger(__name__) 
    
    def event(self,interfaceID,deviceNumber,channelName,value,*unkown):
        '''
        only for logging
        '''
        self.__resetTimer()
        file = open('log/channels.txt','a') 
        file.write('%s %s %s %s\n'%(deviceNumber,channelName,value,unkown))
        file.close() 
        
        deviceID=("%s@%s.%s"%(deviceNumber,self.__config.get('gateway'),self.__config.get('host')))  
        channelName=channelName.lower()
        
        try:
            self.__log.debug("event: deviceID: %s, channel name = %s, value = %s" % (deviceID,channelName,value))
            if not self.__core.ifDeviceExists(deviceID):
                self.__log.error("deviceID %s is not exists"%(deviceID))
                return''
            if not self.__core.ifDeviceChannelExist(deviceID,channelName):
                self.__core.addDeviceChannel(deviceID,channelName,self.__defaultAttribute(channelName))
        except:
            self.__log.error("error to add channel %s for deviceID %s "%(channelName,deviceID), exc_info=True)
            return ''
        try:
            self.__core.setDeviceChannelValue(deviceID,channelName,value)
        except:
            self.__log.error("error can not  add value %s for channel %s for deviceID %s "%(value,channelName,deviceID), exc_info=True)
        return ''
    
    def newDevices(self, interfaceID,allDevices):
        self.__resetTimer()
        self.__log.debug("call newDevices for interfaceID:%s"%(interfaceID))
        for device in allDevices:
            '''
            only for debug
            '''
            file = open('log/devices.txt','a') 
            file.write('%s\n'%(device))
            file.close() 
            if not device['PARENT']=="":
                deviceID="%s@%s.%s"%(device['ADDRESS'],self.__config.get('gateway'),self.__config.get('host'))
                try:
                    if not self.__core.ifDeviceExists(deviceID):
                        self.__addNewDevice(device)
                    else:
                        self.__log.info("deviceID is exist: %s"%(deviceID))
                except:
                    self.__log.warning("can not add deviceID: %s"%(deviceID), exc_info=True) 
        return ''
    def listMethods(self,*args):
        self.__resetTimer()
        self.__log.info("call listMethods for interfaceID %s"%(args))
        return ''
    
    def listDevices(self,*args):
        self.__resetTimer()
        self.__log.info("call listDevices for interfaceID %s"%(args))
        return ''
    
    def __defaultAttribute(self,channelName):
        '''
        return a dic with default Attribute
        '''
        channelValues={}
        channelValues[channelName]={
                "value":{
                        "value":"unkown",
                        "type":"string"},
                "name":{        
                        "value":"unkown",
                        "type":"string"},
                    }
        return channelValues
    
    def __addNewDevice(self,device):
        '''
        add a new sensor to core devices
        '''
        try:
            deviceID="%s@%s.%s"%(device['ADDRESS'],self.__config['gateway'],self.__config['host'])
            self.__log.info("add  new devicesID:%s"%(deviceID))
            devicetype=device['PARENT_TYPE'].replace("-","_")
            device={
                    "gateway":{
                        "value":"%s"%(self.__config['gateway']),
                        "type":"string"},
                    "deviceID":{
                        "value":"%s"%(deviceID),
                        "type":"string"},
                    "enable":{
                        "value":True,
                        "type":"bool"},
                    "connected":{
                        "value":True,
                        "type":"bool"},
                    "devicetype":{
                        "value":"%s"%(devicetype),
                        "type":"string"},
                    "host":{
                        "value":self.__config['host'],
                        "type":"string"},
                    "package":{
                        "value":self.__config['package'],
                        "type":"string"},
                    }
                
            channel={}
            self.__core.addDevice(device,channel)
        except:
            self.__log.error("can not add deviceID: %s"%(deviceID), exc_info=True) 
                            
    
            



class server(threading.Thread):
    
    def __init__(self,params,core):
        threading.Thread.__init__(self)
        '''         configuration        '''
        self.__config={
                    "name":"hmc_rpc_rf_default",
                    "hm_ip":"127.0.0.1",
                    "hm_port":"2000",
                    "hm_interface_id":randint(100,999),
                    "rpc_port":5050+randint(0,49),
                    "rpc_ip":"127.0.0.0",
                    "gateway":"unknown",
                    "host":"unknown",
                    "blockRPCServer":60,
                    "MSGtimeout":60}
        self.__config.update(params)
        '''    logger instance    '''
        self.__log=logging.getLogger(__name__) 
        '''    running flag    '''
        self.running=1
        '''    core instance   '''
        self.__core=core
        '''    timeout         '''
        self.__lastMSG=0
        '''    timeout for server '''
        self.__blockTime=0
        '''    rpc Server Instance '''
        self.__rpcServer=False
        
        self.__log.debug("build  %s instance"%(__name__))
    
    def run(self):
        try:
            self.__log.info("%s start"%(__name__))
            while self.running:
                self.__buildRPCServer()
                if self.__blockTime<int(time.time()):
                    if self.__lastMSG<int(time.time()):
                        self.__log.warning("message timeout, get no message since %i sec."%(self.__config.get('MSGtimeout')))
                        try:
                            self.__startInitRequest()
                        except:
                            self.__log.warning("can not request a RPC INIT")
                            self.__blockServer() 
                time.sleep(0.1)    
            self.__log.critical("%s normally stop:"%(__name__))
        except:
            self.__log.critical("%s have a problem and stop"%(__name__),exc_info=True)
            self.__stopInitRequest()
        
    def shutdown(self):
        '''
        shutdown
        '''
        self.running=False
        self.__log.critical("RPC Server shutdown")
        try:
            self.__rpcServer=False
            self.__stopInitRequest()
        except:
            self.__log.critical("error stopping RPC connection")
        self.__log.critical("RPC Server is stop")
    
    def __startInitRequest(self):
        '''
        send a init Request to get data
        
        raise exception on failed
        '''
        try:
            proxy=self.__proxyInstance()
            self.__log.info("send a RPC INIT Request at:(http://%s:%s)"%(self.__config.get("rpc_ip"),self.__config.get("rpc_port")))
            proxy.init("http://%s:%s"%(self.__config.get("rpc_ip"), self.__config.get("rpc_port")),self.__config.get("hm_interface_id"))
            self.__log.debug("send a RPC INIT Request finish")
        except:
            self.__log.error("can not start send a start INIT request",exc_info=True)
            raise Exception
   
    def __stopInitRequest(self):
        '''
        send a stop Request to get no data
        
        raise exception on failed
        '''
        try:
            proxy=self.__proxyInstance()
            self.__log.info("stop RPC Request at:http://%s:%s"%(self.__config.get("rpc_ip"),self.__config.get("rpc_port")))
            proxy.init("http://%s:%s"%(self.__config["rpc_ip"], int(self.__config["rpc_port"])))
            self.__log.debug("stopped RPC data from homematic")
        except:
            self.__log.error("can not send a stop INIT request",exc_info=True)
            raise Exception
            
    def __proxyInstance(self):
        '''
        build a RPC proxy instance
        '''
        try:
            self.__log.info("RPC Init: init(http://%s:%s, '%s')" %(self.__config.get("rpc_ip"),int(self.__config.get("rpc_port")), self.__config.get("hm_interface_id")) )
            proxy = xmlrpclib.ServerProxy("http://%s:%i" %(self.__config.get("hm_ip"), int(self.__config.get("hm_port"))))
            self.__log.debug("proxy initialized")
            return proxy
        except:
            self.__log.error("can not build a RPC proxy server",exc_info=True)
            raise Exception
            
    def __buildRPCServer(self):
        '''
        build a RPC Server
        '''
        if self.__blockTime>int(time.time()):
            ''' server is block '''
            return
        try:
            if self.__rpcServer:
                if self.__rpcServer.isAlive():
                    ''' server is running '''
                    return
                else:
                    ''' server is exciting but not running '''
                    self.__log.warning("RPC Server %s:%s is stop,starting server"%(self.__config.get("rpc_ip"),self.__config.get("rpc_port")))
                    try:
                        self.__rpcServer.start()
                        self.__unblockServer() 
                        return
                    except:
                        self.__blockServer()
                        self.__rpcServer=False
                        self.__log.warning("can not start RPC Server %s:%s"%(self.__config.get("rpc_ip"),self.__config.get("rpc_port")))
                        return
            self.__log.info("RPC Server %s:%s start"%(self.__config.get("rpc_ip"),self.__config.get("rpc_port")))
            server = SimpleXMLRPCServer((self.__config.get("rpc_ip"),int(self.__config.get("rpc_port"))))
            server.logRequests=False
            server.register_introspection_functions() 
            server.register_multicall_functions() 
            server.register_instance(hmcRPCcallback(self.__config,self.__core,self.__resetTimer))
            self.__rpcServer = threading.Thread(target=server.serve_forever)
            self.__rpcServer.start()
            self.__log.info("RPC Server Start")
            self.__unblockServer()
        except:
            self.__log.error("can not start RPC server", exc_info=True)
            self.__rpcServer=False
            self.__blockServer() 
    
    def __resetTimer(self):
        ''' reset timer '''
        self.__log.debug("reset MSG timeout")
        self.__lastMSG=self.__config.get('MSGtimeout')+int(time.time())  
        
    def __unblockServer(self):
        '''
        unblock the server for new connections
        '''
        self.__log.info("unblock server in 2 sec.")
        self.__blockTime=2+int(time.time()) 
        
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        self.__log.error("block server for %i sec"%(self.__config.get('blockRPCServer')))
        self.__blockTime=self.__config.get('blockRPCServer')+int(time.time())    
        
        
        
       
           
