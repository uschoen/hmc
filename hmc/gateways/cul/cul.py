'''
Created on 05.12.2016

@author: uschoen
'''
__version__ = 3.1

import logging
import serial                   #@UnresolvedImport
import threading
import time
from  fs20 import fs20device
from ws300 import ws300device

'''
TODO:
remove sleeping property from config file
'''
class sensor(threading.Thread,fs20device,ws300device):


    def __init__(self,parms,core):
        threading.Thread.__init__(self)
        self.core=core
        self.log=logging.getLogger(__name__) 
        self.config={
            'usbport':"/dev/ttyUSB0",
            'baudrate':"9600",
            'timeout':1
            }
        self.config.update(parms)

        self.__budget=0
        self.__pending_line=[]
        self.__read_queue=[]
        self.running=1
        self.__USBport=False
        self.log.info("build %s instance"%(__name__))
        
    def run(self):
        try:
            self.log.info("%s  start"%(__name__))
            self.__openUSB()
            self.__initCUL() 
            time.sleep(0.3)   
            self.log.info("init:%s"%(self.__readResult()))
            self.__sendCommand("V") 
            time.sleep(0.3)     
            self.log.info("version:%s"%(self.__readResult()))
            self.__sendCommand("VH") 
            time.sleep(0.3)   
            self.log.info("hadrware:%s"%(self.__readResult()))
            self.__readBudget()
            while self.running:
                if not self.__USBport:
                    self.log.error("can not open usb port")
                    try:
                        self.__USBport.close()
                        self.log.error("closing USB Port %s"%(self.config['usbport']))
                    except:
                        self.log.error("can not closing USB Port %s"%(self.config['usbport']))
                    while self.__USBport:
                        self.__openUSB()
                        self.log.info("wait 2 min and try again")
                        time.sleep(120)    
                        self.__initCUL()
                        self.__readBudget() 
                read_line = self.__readResult()
                if read_line is not None:
                    if read_line.startswith("21  "):
                        self._pending_budget = int(read_line[3:].strip()) * 10 or 1
                        self.log.info("get pending budget: %sms" %(self._pending_budget))
                    elif read_line.startswith("K"):
                        self.log.debug("get weather sensor response from CUL: '%s'" % read_line)
                        self.decodeWs300weather(read_line.lstrip("K"))
                    elif read_line.startswith("F"):
                        self.log.debug("get FS20 response from CUL: '%s'" % read_line)
                        self.decodeFS20((read_line.lstrip("F")))
                    else:
                        self.log.warning("get unknown response from CUL: '%s'" % read_line)
                time.sleep(0.1)
            self.log.warning("%s  stop"%(__name__))
        except:
            self.log.critical("cul is stopped", exc_info=True)
    
    def addChannel(self,deviceID,channelName):
        '''
        add new channel to device core
        '''
        self.log.info("add channel:%s"%(channelName))
        try:
            channelValues={}
            channelValues[channelName]={
                "value":{
                        "value":"unkown",
                        "type":"string"},
                "name":{        
                        "value":"unkown",
                        "type":"string"},
                    }
            self.core.addDeviceChannel(deviceID,channelName,channelValues)
        except:    
            self.log.error("can not add channel %s for deviceID %s "%(channelName,deviceID),exc_info=True) 
            raise
           
    def addNewDevice(self,deviceID,devicetype):
        '''
        add a new device to core
        
        deviceID: device ID of the new device
        type:     device type
        
        raise exception
        '''
        try:
            device={
                    "gateway":{
                        "value":"%s"%(self.config['gateway']),
                        "type":"string"},
                    "deviceID":{
                        "value":deviceID,
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
                        "value":self.config['host'],
                        "type":"string"},
                    "package":{
                        "value":self.config['package'],
                        "type":"string"},
                    }
            channel={}
            if self.core.ifDeviceExists(deviceID):
                self.log.info("deviceID %s is existing, update core"%(deviceID))
                self.core.updateDevice(device,channel)
            else:
                self.log.info("add deviceID %s to core"%(deviceID))
                self.core.addDevice(device,channel)
        except:
            self.log.error("can not add new deviceID %s to core"%(deviceID), exc_info=True)
            raise Exception
    
    def rssi(self,RAWvalue):
        '''
        calculate  RSSI Value
        '''
        rssi=RAWvalue
        if rssi>=128:
            rssi=((rssi-256)/2-74)
        else:
            rssi=rssi/2-74
        return rssi
    
    def shutdown(self):
        '''
        shutdown the cul gateway
        '''
        self.log.critical("shutdown cul")
        self.running=0
        self.__closeUSB()
        self.log.critical("shutdown cul finish")
        
    def __readBudget(self):
        '''
        send command read budget
        '''
        self.__sendCommand("X")
        
    def __openUSB(self):
        '''
        open usb port to cul stick
        
        return  true if usb open
                false is usb not open
        
        exception will be raise
        '''
        if not self.__USBport:
            try:
                self.log.info("open serial, port:%s baud:%s timeout:%s"%(self.config['usbport'],self.config['baudrate'],self.config['timeout']))
                self.__USBport=serial.Serial(
                              port='/dev/ttyACM0',
                              baudrate = self.config['baudrate'],
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              bytesize=serial.EIGHTBITS,
                              timeout=self.config['timeout']
                            )
                return self.__USBport.isOpen() 
            except:
                self.log.critical("can not open serial, port:%s baud:%s timeout:%s"%(self.config['usbport'],self.config['baudrate'],self.config['timeout']), exc_info=True)
                self.__USBport=False
                return False
        return False
    
    def __closeUSB(self):
        '''
        close usb port
        '''
        try:
            self.log.info("close serial, port:%s baud:%s timeout:%s"%(self.config['usbport'],self.config['baudrate'],self.config['timeout']))
            self.__USBport.close()
        except:
            self.log.info("serial is all ready close")
        
            
            
    def __initCUL(self):
        '''
        init command for cul stick
        exception will be raise
        '''
        self.log.info("initCUL")
        try:
            self.__sendCommand("X21")
            time.sleep(0.3)
        except:
            self.log.error("can not init cul stick")
            raise Exception        
         
    def __sendCommand(self, command):
        '''
        send a command
        
        raise Exception 
        '''
        self.log.debug("send command:%s"%(command))
        if not self.__USBport:
            self.log.error("usb is not open")
            if not self.__openUSB():
                raise Exception
            self.__initCUL()
            self.__readBudget()
        try:
            self.__USBport.write("%s\r\n"%(command))
            self.__budget = 0
        except:
            self.log.error("can not send command")
            raise Exception
    
    def __readResult(self):
        '''
        read usb port
        
        return string
        raise exception on error
        '''
        try:
            while self.__USBport.inWaiting():
                self.__pending_line.append(self.__USBport.read(1))
                if self.__pending_line[-1] == "\n":
                    completed_line = "".join(self.__pending_line[:-2])
                    self.log.debug("received: %s" %(completed_line))
                    self.__pending_line = []
                    if completed_line.startswith("Z"):
                        self.__read_queue.put(completed_line)
                    else:
                        return completed_line
        except:
            self.log.error("can not read usb port",exc_info=True)
            raise Exception

    

