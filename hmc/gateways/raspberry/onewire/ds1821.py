'''
Created on 21.10.2016

@author: uschoen

sudo apt-get install rrdtool python-rrdtool

'''
import threading,os,re
from time import sleep
import logging

__version__="2.0"

class sensor(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        self.__core=core
        self.__args={
                        "gateway": "unkown", 
                        "host": "unkown", 
                        "interval": 60, 
                        "package": "raspberry.onewire", 
                        "path": "/sys/bus/w1/devices/", 
                        "tempDiv": 1, 
                        "devicetype": "ds1820"
                        }
        self.__args.update(params)
        self.logger=logging.getLogger(__name__)
        self.__connectedSensors={}
        self.running=self.__checkoneWire()
        self.logger.debug("build  %s instance with version %s"%(__name__,__version__))
        
    def run(self):
        '''
        gateway main loop
        '''
        self.logger.info("%s start"%(__name__))
        sleep(5)
        while self.running:
            self.__checkConnectedSensors()
            for sensorID in self.__connectedSensors:
                    if  self.__connectedSensors[sensorID]['device']["connected"]['value']==False or self.__connectedSensors[sensorID]['device']["enable"]['value']==False:
                        self.logger.info("sensor id %s is disconnected or not enable"%(sensorID))
                        continue
                    self.logger.debug("read sensorID %s"%(sensorID))
                    path=self.__args["path"]+sensorID+"/w1_slave"
                    try:
                        value=self.__readSensor(path)
                        self.__updateSensorID(sensorID,value)
                    except:
                        self.logger.error("can not read/update sensorID %s"%(sensorID))
            self.logger.info("wait %i s for next scan"%(self.__args["interval"])) 
            sleep(self.__args["interval"])
        self.logger.info("%s stop:"%(__name__))
    
    def __updateSensorID(self,sensorID,value):
        '''
        read onewire sensor and compare old & new value
        update core device
        
        TODO: change configuration item "tempDiv" to "tolerance"
        '''
        try:
            deviceID=self.__connectedSensors[sensorID]['device']['deviceID']['value']   
            if not self.__core.ifDeviceChannelExist(deviceID,"temperature"):
                self.__addChannel(sensorID,deviceID,"temperature")
            
            lastValue=self.__connectedSensors[sensorID]["channels"]["temperature"]['value']
            tempDiv=float(self.__args["tempDiv"])
            self.logger.debug("sensorID:%s old value:%s new value:%s temp. tolerance:%s"%(sensorID,lastValue,value,tempDiv))
            
            if (lastValue < (value-tempDiv)) or (lastValue >(value+tempDiv)):
                self.logger.debug("temperature is change, update internal device") 
                self.__connectedSensors[sensorID]["channels"]["temperature"]['value']=value
                '''
                check if sensor in core as device
                '''
                if not self.__core.ifDeviceExists(deviceID):
                    try:
                        self.__addNewSensor(sensorID)
                    except:
                        self.logger.error("can not add and update sensorID %s"%(sensorID),exc_info=True)
                        return
                '''
                update device in core
                '''
                try:
                    self.__core.setDeviceChannelValue(deviceID,"temperature",value)
                    self.logger.debug("update for deviceID %s success"%(deviceID)) 
                except:    
                    self.logger.error("update for deviceID %s failed. DISABLE sensor"%(deviceID),exc_info=True) 
                    self.__connectedSensors[sensorID]['device']['enable']['value']=False                                  
            else:
                self.logger.debug("temperature is not change")
        except:    
            self.logger.error("can not update sensorID %s"%(sensorID),exc_info=True) 
    
    def __addChannel(self,sensorID,deviceID,channelName):
        self.logger.info("add channel:%s"%(channelName))
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
        self.logger.debug("check connected sensors")
        self.__disableAllSensor()
        self.logger.debug("read connected sensors in path %s"%(self.__args["path"]))
        sensorList =os.listdir(self.__args["path"])
        for sensorID in sensorList:
            if sensorID=="w1_bus_master1":
                continue
            if sensorID in self.__connectedSensors:
                self.logger.debug("find exiting sensor %s and enable"%(sensorID))
                self.__connectedSensors[sensorID]['device']["connected"]['value']=True
            else:
                try:
                    self.__addNewSensor(sensorID)
                except:
                    self.logger.error("can not add new sensorID %s"%(sensorID),exc_info=True)
                   
        self.__deleteDisconectedSensors()
    
    def __addNewSensor(self,sensorID):
        '''
        add a new sensor to core devices
        '''
        self.logger.info("add new sensorID %s"%(sensorID))
        try:
            device={
                "device":{
                    "gateway":{
                        "value":"%s"%(self.__args['gateway']),
                        "type":"string"},
                    "deviceID":{
                        "value":"%s@%s.%s"%(sensorID,self.__args['gateway'],self.__args['host']),
                        "type":"string"},
                    "enable":{
                        "value":True,
                        "type":"bool"},
                    "connected":{
                        "value":True,
                        "type":"bool"},
                    "devicetype":{
                        "value":"%s"%(self.__args['devicetype']),
                        "type":"string"},
                    "host":{
                        "value":self.__args['host'],
                        "type":"string"},
                    "package":{
                        "value":self.__args['package'],
                        "type":"string"},
                    },
                "channels":{
                    "temperature":{
                        "value":0}}
                }
            
            if self.__core.ifDeviceExists(device["device"]['deviceID']['value']):
                self.logger.info("deviceID %s is existing, update core"%(device["device"]['deviceID']['value']))
                self.__core.updateDevice(device)
                self.__connectedSensors[sensorID]=device
            else:
                self.logger.info("add deviceID %s to core"%(device["device"]['deviceID']['value']))
                self.__core.addDevice(device)
                self.__connectedSensors[sensorID]=device
        except:
            self.logger.error("can not add new deviceID %s to core"%(device["device"]['deviceID']['value']), exc_info=True)
            raise Exception
        
    def __deleteDisconectedSensors(self):
        '''
        delete disconnecd senors from gateways list
        '''
        self.logger.debug("clear up and delete disconnected sensor")
        for sensorID in self.__connectedSensors:
            if self.__connectedSensors[sensorID]['device']["connected"]['value']==False:
                del self.__connectedSensors[sensorID]
                self.logger.info("delete sensor %s"%(sensorID))
                   
    def __disableAllSensor(self):
        '''
        disable alle gateways sensors 
        '''
        self.logger.debug("set all sensor conected to false")
        for sensorID in self.__connectedSensors:
            self.__connectedSensors[sensorID]['device']["connected"]['value']=False
               
    def shutdown(self):
        self.running=0
        self.logger.critical("stop %s thread"%(__name__))
    
    def __checkoneWire(self):
        self.logger.info("check requirements for onewire")
        if not os.path.isdir(self.__args["path"]):
            self.logger.error("onewire path %s not exist"%(self.__args["path"]))
            return 0
        self.logger.info("onewire requirements ok")
        return 1
    
            
            