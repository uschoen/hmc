'''
Created on 22.10.2016

@author: uschoen
install :
apt-get install python-xmltodict

TODO:
rebuild script and class
'''

__version__= "3.0"

import threading
import xmlrpclib                                            #@UnresolvedImport
from SimpleXMLRPCServer import SimpleXMLRPCServer           #@UnresolvedImport
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport
import urllib2                                              #@UnresolvedImport
import xmltodict                                            #@UnresolvedImport
from random import randint
import logging



from time import sleep, time




class hmc_rpc_callback:
    def __init__(self,parms,core,timer):
        self.__core=core
        self.__config=parms
        self.__timer=timer
        self.__log=logging.getLogger(__name__) 
    
    def event(self, interfaceID, device, channelName, value,*unkown):
        file = open('log/channels.txt','a') 
        file.write('%s %s %s %s\n'%(device, channelName, value,unkown))
        file.close() 
        (device,channelNumber)=device.split(":")
        deviceID=("%s@%s.%s"%(device,self.__config['gateway'],self.__config['host']))  
        channelName=channelName.lower()
        self.__timer()
        try:
            self.__log.debug("event: interfaceID = %s, device: %s, channel name = %s, value = %s" % ( interfaceID,device,channelName,value))
            self.__log.debug("deviceID %s"%(deviceID))
        
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
    def listMethods(self,*args):
        self.__timer()
        self.__log.info("call listMethods for interfaceID %s"%(args))
        return ''
    
    def listDevices(self,*args):
        self.__timer()
        self.__log.info("call listDevices for interfaceID %s"%(args))
        return ''
    
    def newDevices(self, interfaceID, allDevices):
        self.__timer()
        self.__log.debug("call newDevices for interfaceID:%s"%(interfaceID))
        for device in allDevices:
            file = open('log/devices.txt','a') 
            file.write('%s\n'%(device))
            file.close() 
            if device['PARENT']=="":
                deviceID="%s@%s.%s"%(device['ADDRESS'],self.__config['gateway'],self.__config['host'])
                try:
                    if not self.__core.ifDeviceExists(deviceID):
                        self.__addNewDevice(device)
                    else:
                        self.__log.info("deviceID is exist: %s"%(deviceID))
                except:
                    self.__log.warning("can not add deviceID: %s"%(deviceID), exc_info=True) 
        return ''
     
    def __defaultAttribute(self,channelName):
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
            devicetype=device['TYPE'].replace("-","_")
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
        self.__config={}
        self.__config.update(params)
        self.__log=logging.getLogger(__name__) 
        self.__log.debug("build  %s instance"%(__name__))
    
    def run(self):
        self.__log.info( "start %s thread"%(__name__))
        while self.running:
            sleep(0.1) 
        self.__log.warning("thread %s stop"%(__name__))
       
    def __sendcommand(self):
        self.__log.error("send messages to homematic")
        HMurl=self.__config['hmXmlUrl']
        iseID=self.__config['iseID']
        value=self.__config['iseIDValue']
        url=("%s?ise_id=%s&new_value=%s"%(HMurl,iseID,value))
        self.__log.debug("url is %s "%(url))
        try:
            response = urllib2.urlopen(url)
            httcode=response.getcode()
            self.__log.debug("http response code %s"%(httcode))
            if  httcode<>200:
                self.__log.error("can not send request to url") 
                return
            xml=response.read()
            self.__log.debug("xml response %s"%(xml))
            HMresponse=xmltodict.parse(xml)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    self.__log.debug("value successful change")
                elif "not_found" in HMresponse['result']: 
                    self.__log.error("can not found iseID %s"%(iseID))
                else:
                    self.__log.warning("get some unkown answer %s"%(xml))
            else:
                self.__log.warning("get some unkown answer %s"%(xml)) 
        except urllib2.URLError:
            self.__log.error("get some error at url request", exc_info=True)
        except ValueError:
            self.__log.error("some error at request, check configuration", exc_info=True)
        except :
            self.__log.critical("somthing going wrong !!!", exc_info=True)    
        
    
    '''
    shutdown
    '''
    def shutdown(self):
        self.running=False
        self.__log.critical("%s server stop"%(__name__))
      
    