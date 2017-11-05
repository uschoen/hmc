'''
Created on 21.10.2016

@author: uschoen

sudo apt-get install rrdtool python-rrdtool

'''
import threading,os,re
from time import localtime, strftime,sleep
from datetime import datetime



class sensor(threading.Thread): 
    def __init__(self, params,core,logger=False):
        threading.Thread.__init__(self)
        self.__core=core
        self.__config=params
        self.__logger=logger
        self.running=1
        self.__connected_senors={}
        self.__log("debug","build  "+__name__+" instance")
    def __log (self,level="unkown",messages="no messages"):
        if self.__logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.__logger.write(conf)
    def checkoneWire(self):
        self.__log("info","check requierments for onewire")
        if not os.path.isdir(self.__config["path"]):
            self.__log("error","onewire path %s not exist"%(self.__config["path"]))
            return False
        self.__log("info","onewire requierments ok")
        return True
    def run(self):
        self.__log("info %s start"%(__name__))
        while self.running:
            if self.checkoneWire():
                self.__check_connected_sensor()
                for sensor_id in self.__connected_senors:
                    if  self.__connected_senors[sensor_id]["connected"]['value']==False or self.__connected_senors[sensor_id]["enable"]['value']==False:
                        self.__log("info","sensor "+ sensor_id +" is disconnected and not enable")
                        continue
                    self.__log("debug","read sensor id "+ sensor_id)
                    path=self.__config["path"]+sensor_id+"/w1_slave"
                    self.__update_Sensor(sensor_id,round(float(self.__read_sensor(path)),2))
            self.__log("info","wait "+str(self.__config["intervall"])+" for next scan")  
            sleep(self.__config["intervall"])
        self.__log("info", __name__+" stop:")    
    def __update_Sensor(self,sensor_id,value):
        self.__log("debug","read sensor: "+sensor_id+" value:"+ str(value)) 
        self.__log("debug","old value: "+str(self.__connected_senors[sensor_id]["value"]['value'])+" new value:"+ str(value)+" temp div:"+str(self.__config["tempDiv"])) 
        if (float(self.__connected_senors[sensor_id]["value"]['value']) < (value-float(self.__config["tempDiv"]))) or (float(self.__connected_senors[sensor_id]["value"]['value']) >(value+float(self.__config["tempDiv"]))):
            self.__log("debug","temperatur is change, update") 
            self.__connected_senors[sensor_id]["value"]['value']=value
            if not self.__core.deviceExists(self.__connected_senors[sensor_id]["deviceID"]['value']):
                self.__add_new_Sensor(sensor_id)
            try:
                self.__core.setValue(self.__connected_senors[sensor_id]['deviceID']['value'],value)
                self.__log("debug","update for deviceID %s success"%(self.__connected_senors[sensor_id]['deviceID']['value'])) 
            except:    
                self.__log("error","update for deviceID %s fail to time. DISABLE sensor"%(self.__connected_senors[sensor_id]['deviceID']['value'])) 
                self.__connected_senors[sensor_id]['enable']['value']=False                                  
        else:
            self.__log("debug","temperatur is not change")
          
    def stop(self):
        self.running=0
        self.__log("emergency","stop %s thread"%(__name__))
        
    def __check_connected_sensor(self):
        self.__set_Sensors_connected_disable()
        self.__log("debug","read connected sensors "+ self.__config["path"])
        SensorList =os.listdir(self.__config["path"])
        for sensor_id in SensorList:
            if sensor_id=="w1_bus_master1":
                continue
            if sensor_id in self.__connected_senors:
                self.__log("debug","find exiting sensor "+ str(sensor_id))
                self.__connected_senors[sensor_id]["connected"]['value']=True
            else:
                self.__add_new_Sensor(sensor_id)      
        self.__delete_disconected_Sensors()
    '''
        adding new Sensor
    ''' 
    def __add_new_Sensor(self,sensor_id):
        self.__log("info","add new sensor id "+ str(sensor_id))
        tempSensor={
                    "gateway":{
                               "value":str (self.__config['gateway'])
                              },
                    "sensor_id":{
                               "value":str(sensor_id)
                              },
                    "deviceID":{
                               "value":str(sensor_id+"@"+str (self.__config['gateway'])+"."+str(self.__config['host']))
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
                               "value":str (self.__config['typ'])
                              },
                    "host":{
                                "value":self.__config['host']
                            }
                   }
        self.__connected_senors[sensor_id]=tempSensor
        try:
            self.__core.addDevice(tempSensor)
            self.__log("info","add new sensor %s"%(tempSensor["deviceID"]['value']))
            self.__connected_senors[sensor_id]['enable']['value']=True
        except:
            self.__log("error","can not add new sensor %s"%(tempSensor["deviceID"]['value']))
            self.__connected_senors[sensor_id]['enable']['value']=False
              
    '''
        Set all Sensor to disable
    '''        
    def __set_Sensors_connected_disable(self):
        self.__log("debug","set all sensor conected to false")
        for sensor_id in self.__connected_senors:
            self.__connected_senors[sensor_id]["connected"]['value']=False
    
    def __delete_disconected_Sensors(self):
        self.__log("debug","check to delete disable sensor")
        for sensor_id in self.__connected_senors:
            if self.__connected_senors[sensor_id]["connected"]['value']==False:
                del self.__connected_senors[sensor_id]
                self.__log("info","delete disconnected sensor "+str(sensor_id))
                           
    def __read_sensor(self,path):
        value = "U"
        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value = str(float(m.group(2)) / 1000.0)
                    f.close()
        except IOError:
            self.__log("error","can not read sensor id"+ str(path))
        return value
        
            
            