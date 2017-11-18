'''
Created on 21.10.2016

@author: uschoen

sudo apt-get install rrdtool python-rrdtool

'''
import threading,os,re
from time import localtime, strftime,sleep
from datetime import datetime
import logging

__version__="2.0"

class sensor(threading.Thread): 
    def __init__(self, params,core):
        threading.Thread.__init__(self)
        self.__core=core
        self.__args=params
        self.logger=logging.getLogger(__name__)
        self.__connectedSensors={}
        self.running=self.__checkoneWire()
        self.logger.debug("build  %s instance with version %s"%(__name__,__version__))
        
    def run(self):
        self.logger.info("%s start"%(__name__))
        while self.running:
            self.__checkConnectedSensors()
            for sensorID in self.__connectedSensors:
                    if  self.__connectedSensors[sensorID]["connected"]['value']==False or self.__connectedSensors[sensorID]["enable"]['value']==False:
                        self.logger.info("sensor id %s is disconnected or not enable"%(sensorID))
                        continue
                    self.logger.debug("read sensorID %s"%(sensorID))
                    path=self.__args["path"]+sensorID+"/w1_slave"
                    try:
                        value=self.__readSensor(path)
                        self.__updateSensorID(sensorID,value)
                    except:
                        self.logger.error("can not read/update sensorID %s"%(sensorID))
            self.logger.info("wait %i s for next scan"%(self.__args["intervall"])) 
            sleep(self.__args["intervall"])
        self.logger.info("%s stop:"%(__name__))
    
    def __updateSensorID(self,sensorID,value):
        self.logger.debug("sensorID:%s old value:%s new value:%s temp div:%s"%(sensorID,self.__connectedSensors[sensorID]["value"]['value'],value,self.__args["tempDiv"]))
        lastValue=self.__connectedSensors[sensorID]["value"]['value']
        tempDiv=float(self.__args["tempDiv"])
        if (lastValue < (value-tempDiv)) or (lastValue >(value+tempDiv)):
            self.logger.debug("temperature is change, update Device") 
            self.__connectedSensors[sensorID]["value"]['value']=value
            '''
            check if Sensor in core as device
            '''
            if not self.__core.deviceExists(self.__connectedSensors[sensorID]["deviceID"]['value']):
                try:
                    self.__addNewSensor(sensorID)
                except:
                    self.logger.error("can not update sensorID %s"%(sensorID))
                    return
            '''
            update device in core
            '''
            try:
                
                self.__core.setValue(self.__connectedSensors[sensorID]['deviceID']['value'],value)
                self.logger.debug("update for deviceID %s success"%(self.__connectedSensors[sensorID]['deviceID']['value'])) 
            except:    
                self.logger.error("update for deviceID %s failed. DISABLE sensor"%(self.__connectedSensors[sensorID]['deviceID']['value'])) 
                self.__connectedSensors[sensorID]['enable']['value']=False                                  
        else:
            self.logger.debug("temperature is not change")
    def __readSensor(self,path):
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
                self.__connectedSensors[sensorID]["connected"]['value']=True
            else:
                try:
                    self.__addNewSensor(sensorID)
                except:
                    self.logger.error("can not add new sensorID %s"%(sensorID))
                   
        self.__deleteDisconectedSensors()
    
    def __addNewSensor(self,sensorID):
        self.logger.info("add new sensorID %s"%(sensorID))
        tempSensor={
                    "gateway":{
                               "value":"%s"%(self.__args['gateway'])
                              },
                    "sensorID":{
                               "value":"%s"%(sensorID)
                              },
                    "deviceID":{
                               "value":"%s@%s.%s"%(sensorID,self.__args['gateway'],self.__args['host'])
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
                               "value":"%s"%(self.__args['typ'])
                              },
                    "host":{
                                "value":self.__args['host']
                            }
                   }
        try:
            if self.__core.deviceExists(tempSensor["deviceID"]['value']):
                self.logger.info("deviceID %s is existing, update core"%(tempSensor["deviceID"]['value']))
                self.__core.updateDevice(tempSensor)
                self.__connectedSensors[sensorID]=tempSensor
            else:
                self.logger.info("add deviceID %s to core"%(tempSensor["deviceID"]['value']))
                self.__core.addDevice(tempSensor)
                self.__connectedSensors[sensorID]=tempSensor
        except:
            self.logger.error("can not add new deviceID %s to core"%(tempSensor["deviceID"]['value']))
            raise Exception
        
    def __deleteDisconectedSensors(self):
        self.logger.debug("clear up and delete disconnected sensor")
        for sensorID in self.__connectedSensors:
            if self.__connectedSensors[sensorID]["connected"]['value']==False:
                del self.__connectedSensors[sensorID]
                self.logger.info("delete sensor %s"%(sensorID))
                   
    def __disableAllSensor(self):
        self.logger.debug("set all sensor conected to false")
        for sensorID in self.__connectedSensors:
            self.__connectedSensors[sensorID]["connected"]['value']=False
               
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
    
            
            