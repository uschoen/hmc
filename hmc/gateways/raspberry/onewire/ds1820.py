'''
Created on 21.10.2016

@author: uschoen

sudo apt-get install rrdtool python-rrdtool

'''
import threading
import os
import re
import time
import logging

__version__=3.0

class sensor(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        self.__core=core
        ''' configuration '''
        self.__args={
                        "gateway": "unkown", 
                        "host": "unkown", 
                        "interval": 360, 
                        "package": "raspberry.onewire", 
                        "path": "/sys/bus/w1/devices/", 
                        "tolerance": 1, 
                        "devicetype": "ds1820"
                        }
        self.__args.update(params)
        ''' waiting time for next scann '''
        self.__waiting=0
        ''' logger instance '''
        self.logger=logging.getLogger(__name__)
        self.__connectedSensors={}
        ''' running flag '''
        self.__running=self.__checkoneWire()
        self.logger.debug("build  %s instance with version %s"%(__name__,__version__))
        
    def run(self):
        '''
        gateway main loop
        '''
        self.logger.info("%s start in 5 sec."%(__name__))
        time.sleep(5)
        while self.__running:
            if self.__waiting<int(time.time()):
                self.__waiting=int(time.time())+self.__args['interval']
                if not self.__checkoneWire():
                    self.__running=0
                    self.logger.info("stopping %s, no onewire path"%(__name__))
                    break 
                self.__checkConnectedSensors()
                for sensorID in self.__connectedSensors:
                    try:
                        deviceID=self.__deviceID(sensorID)
                        '''
                        check if sensor connected to onewire bus
                        '''                    
                        if  self.__connectedSensors[sensorID]["connected"]==False:
                            self.logger.info("sensor id %s is disconnected"%(sensorID))
                            continue
                        '''
                        check if sensor enable in core
                        '''
                        if not self.__core.ifDeviceEnable(deviceID):
                            self.logger.info("sensor id %s is disconnected"%(sensorID))
                            continue 
                        '''
                        check if sensor in core exists
                        '''
                        if not self.__core.ifDeviceExists(deviceID):
                            self.__addNewSensor(sensorID)
                        '''
                        check if channel temperature exists
                        '''
                        if not self.__core.ifDeviceChannelExist(deviceID,"temperature"):
                            self.__addChannel(sensorID,"temperature")
                        '''
                        read temperature from sensor
                        '''   
                        self.logger.debug("read sensorID %s"%(sensorID))
                        path=self.__args["path"]+sensorID+"/w1_slave"
                        self.__updateSensorID(sensorID,self.__readSensor(path))
                    except:
                        self.logger.error("can not read/update sensorID %s"%(sensorID))
            time.sleep(0.1)
        self.logger.info("%s stop:"%(__name__))
    
    def __updateSensorID(self,sensorID,value):
        '''
        read onewire sensor and compare old & new value
        update core device
        '''
        try:
            deviceID=self.__deviceID(sensorID)
            lastValue=self.__core.getDeviceChannelValue(deviceID,'temperature')
            
            tempDiv=float(self.__args["tolerance"])
            self.logger.debug("sensorID:%s old value:%s new value:%s tolerance:%s"%(sensorID,lastValue,value,tempDiv))
            
            if (lastValue < (value-tempDiv)) or (lastValue >(value+tempDiv)):
                self.logger.debug("temperature is change, update device channel temperature") 
                self.__core.setDeviceChannelValue(deviceID,"temperature",value)
                self.logger.debug("update for deviceID %s success"%(deviceID))                                   
            else:
                self.logger.debug("temperature is not change")
        except:    
            self.logger.error("can not update sensorID %s"%(sensorID),exc_info=True) 
    
    def __addChannel(self,sensorID,channelName):
        '''
        add new channel to device core
        '''
        deviceID=self.__deviceID(sensorID)
        self.logger.info("add channel:%s"%(channelName))
        try:
            channelValues={}
            channelValues[channelName]={
                "value":0,
                "name":sensorID
                }
            self.__core.addDeviceChannel(deviceID,channelName,channelValues)
            self.__connectedSensors[sensorID]["channels"]=channelValues
        except:    
            self.logger.error("can not add channel %s for deviceID %s "%(channelName,deviceID),exc_info=True) 
            raise
           
    def __readSensor(self,path):
        '''
        read Sensor
        '''
        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value =str(float(m.group(2)) / 1000.0)
                    f.close()
                    value=round(float(value),2)
                    return value
                else:
                    self.logger.error("value error at sensor path"%(path))
                    raise Exception    
            else:
                self.logger.error("crc error at sensor path"%(path))
                raise Exception
        except:
            self.logger.error("can not read sensor path %s"%(path))
            raise Exception
        
               
    def __checkConnectedSensors(self):
        '''
        check if new onewire sensor connect to bus and 
        add them to core
        '''
        self.logger.debug("check connected sensors")
        self.__disableAllSensor()
        sensorList =os.listdir(self.__args["path"])
        self.logger.debug("read connected sensors in path %s"%(sensorList))
        for sensorID in sensorList:
            if sensorID=="w1_bus_master1":
                continue
            if sensorID in self.__connectedSensors:
                self.logger.debug("find exiting sensor %s and enable"%(sensorID))
                self.__connectedSensors[sensorID]["connected"]=True
            else:
                try:
                    self.__addNewSensor(sensorID)
                except:
                    self.logger.error("can not add new sensorID %s"%(sensorID),exc_info=True)
        self.__deleteDisconectedSensors()
    
    def __addNewSensor(self,sensorID):
        '''
        add a new sensor to core core devices
        '''
        deviceID=self.__deviceID(sensorID)
        self.logger.info("add new sensorID %s with deviceID %s"%(sensorID,deviceID))
        try:
            device={
                
                    "gateway":"%s"%(self.__args['gateway']),
                    "name":sensorID,
                    "deviceID":deviceID,
                    "enable":True,
                    "create":int(time.time()),
                    "connected":True,
                    "devicetype":"%s"%(self.__args['devicetype']),
                    "host":self.__args['host'],
                    "package":self.__args['package']
                    }
            self.__connectedSensors[sensorID]={}
            if self.__core.ifDeviceExists(deviceID):
                self.logger.info("deviceID %s is existing, update core"%(deviceID))
                self.__core.updateDevice(deviceID,device)
            else:
                self.logger.info("add deviceID %s to core"%(deviceID))
                self.__core.addDevice(deviceID,device)
            self.__connectedSensors[sensorID]["connected"]=True
        except:
            self.logger.error("can not add new deviceID %s to core"%(deviceID), exc_info=True)
            raise Exception
        
    def __deleteDisconectedSensors(self):
        '''
        delete disconnected sensor from gateways list
        '''
        self.logger.debug("clear up and delete disconnected sensor")
        for sensorID in self.__connectedSensors:
            if self.__connectedSensors[sensorID]["connected"]==False:
                del self.__connectedSensors[sensorID]
                self.__core.deviceDisable(self.__deviceID(sensorID))
                self.logger.info("delete sensor %s"%(sensorID))
                   
    def __disableAllSensor(self):
        '''
        disable all gateways sensors 
        '''
        self.logger.debug("set all sensor value connect to false")
        for sensorID in self.__connectedSensors:
            self.__connectedSensors[sensorID]["connected"]=False
               
    def shutdown(self):
        '''
        shutdown the gateway
        '''
        self.__running=0
        self.logger.critical("stop %s thread"%(__name__))
    
    def __checkoneWire(self):
        '''
        check if onewire path on host exists and one wire install
        '''
        self.logger.info("check requirements for onewire")
        if not os.path.isdir(self.__args["path"]):
            self.logger.error("onewire path %s not exist"%(self.__args["path"]))
            return 0
        self.logger.info("onewire requirements ok")
        return 1
    
    def __deviceID(self,sensorID):
        '''
        convert the senor id to a dvice id
        '''
        deviceID="%s@%s.%s"%(sensorID,self.__args['gateway'],self.__args['host'])
        return deviceID
        
            
            