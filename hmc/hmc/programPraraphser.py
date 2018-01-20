'''
Created on 20.01.2018

@author: uschoen
'''

__version__ = 3.1

import logging
import time
import threading


class praraphser(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self,core):
        threading.Thread.__init__(self)
        self.__scheduleJobs={}
        self.__conf={
            'maxProgramDeep':10
            }
        self.__core=core
        self.__CMD={
                    "condition":self.__condition,
                    "role":self.__role,
                    "value":self.__value,
                    "dateTimeNow":self.__dateTimeNow,
                    "callerValue":self.__callerValue,
                    "=":self.__isEqual,
                    "<":self.__isLess,
                    ">":self.__isGrater,
                    "<>":self.__isUnequal,
                    "<=":self.__isLessOrEqual,
                    ">=":self.__isGraderOrEqual,
                    "setDeviceChannel":self.__setDeviceChannel,
                    "getDeviceChannel":self.__getDeviceChannel
                    
                    }
        self.__allowedCMD={
                    "build":['role','setDeviceChannel'],
                    "role":['condition'],
                    "condition":['sourceA','sourceB','comparison','true','false'],
                    "sourceAB":['value','condition','callerValue','getDeviceValue','dateTimeNow'],
                    "comparison":["=","<",">","<>","<=",">="],
                    "truefalse":["setDeviceChannel"],
                    "setDeviceChannel":["deviceID","channelName","value"],
                    "getDeviceChannel":["deviceID","channelName"],
                    "callerValue":["deviceID","channelName","eventTyp","programName","programDeep"]
                 }   
        self.__log=logging.getLogger(__name__)
        
    def parsingProgram(self,deviceID,channelName,eventTyp,programName,program,programDeep=0):
        self.__log.debug("start programm %s for deviceID %s channel %s eventTyp %s"%(programName,deviceID,channelName,eventTyp))
        self.__callerValues={
                'deviceID':deviceID,
                'channelName':channelName,
                'eventTyp':eventTyp,
                'programName':programName,
                'programDeep':programDeep
                }
        if programDeep>self.__conf.get('maxProgramDeep',10):
            self.__log.error("maximum program deep (%s) is reached"%(programDeep)) 
            raise Exception
        try:
            threading.Thread(target=self.__run,args = (program)).start()
        except:
            self.__log.error("can not start program")                 
     
    def __run(self,program):
        try:
            self.__build(program)
        except:
            self.__log.error("some error in program %s"%(self.__callerValues.get('programName')))
            raise Exception        
    
    def __build(self,prog):
        for field in prog:
            (field,value)=(field.keys()[0],field.values()[0])
            if field not in self.__allowedCMD['build']:
                self.__log.error("function %s is not supported in build"%(field))
                raise Exception 
            self.__log.debug("call function %s value:%s"%(field,value))
            value=self.__CMD[field](value)
    
    def __role(self,strg):
        '''
        role function
        '''
        self.__log.debug("call role function")
        for role in strg:
            if role not in self.__allowedCMD['role']:
                self.__log.error("function %s is not supported in role"%(role))
                raise Exception
            (field,value)=(strg.keys()[0],strg.values()[0])
            self.__log.debug("call function %s value:%s"%(field,value))
            value=self.__CMD[field](value)
                
            
    def __condition(self,strg):        
        self.__log.debug("call condition function") 
        if not set(self.__allowedCMD['condition']) <= set(strg):
            self.__log.error("role function miss some atribute %s"%(strg.keys()))
            raise Exception
        if strg['comparison'] not in self.__allowedCMD['comparison']:
            self.__log.error("comparison: %s not allowed"%(strg['comparison']))
            raise Exception
        valueA=self.__sourceAB(strg['sourceA'])
        valueB=self.__sourceAB(strg['sourceB'])
        self.__log.debug("A is: %s B is: %s"%(valueA,valueB))
        value=self.__CMD[strg['comparison']](valueA,valueB)
        self.__log.debug("comparison A and B is: %s"%(value))
        if value:
            strg=strg['true'] 
        else:
            strg=strg['false'] 
        self.__isTrueFalse(strg)
        
    def __isTrueFalse(self,strg):
        '''
        is true ore false
        ''' 
        self.__log.debug("call truefalse function")
        for job in strg:
            (field,value)=(job.keys()[0],job.values()[0])
            if field not in self.__allowedCMD['truefalse']:
                self.__log.error("function %s is not supported in role"%(field))
                raise Exception
            self.__log.debug("call function %s value:%s"%(field,value))
            value=self.__CMD[field](value)
            
    def __sourceAB(self,strg): 
        '''
        source AB Function
        '''   
        self.__log.debug("call sourceA/B function")
        (field,value)=(strg.keys()[0],strg.values()[0])
        if field not in self.__allowedCMD['sourceAB']:
            self.__log.error("function %s is not supported in sourceAB"%(field))
            raise Exception 
        value=self.__CMD[field](value)
        return value 
            
    def __isLessOrEqual(self,valueA,valueB):
        '''
                check if <=
                
        return true or false
        '''        
        self.__log.debug("call isLessOrEqual function")
        try:
            if valueA<=valueB:
                return True
            return False
        except:
            self.__log.debug("can not compare isLessOrEqual")
            raise Exception
    
    def __isGraderOrEqual(self,valueA,valueB):
        '''
                check if >=
                
        return true or false
        '''
        self.__log.debug("call isGraderOrEqual function")
        try:
            if valueA>=valueB:
                return True
            return False
        except:
            self.__log.debug("can not compare isGraderOrEqual")
            raise Exception
    
    def __isEqual(self,valueA,valueB):
        '''
                check if =
                
        return true or false
        '''
        self.__log.debug("call isEqual function")
        try:
            if valueA==valueB:
                return True
            return False
        except:
            self.__log.debug("can not compare isEqual")
            raise Exception
        
    def __isGrater(self,valueA,valueB):
        '''
                check if >
                
        return true or false
        '''
        self.__log.debug("call isGrater function")
        try:
            if valueA>valueB:
                return True
            return False
        except:
            self.__log.debug("can not compare isGrater")
            raise Exception
        
    def __isLess(self,valueA,valueB):
        '''
                check if <
                
        return true or false
        '''
        self.__log.debug("call isLess function")
        try:
            if valueA<valueB:
                return True
            return False
        except:
            self.__log.debug("can not compare isLess")
            raise Exception
        
    def __isUnequal(self,valueA,valueB):
        '''
                check if <>
                
        return true or false
        '''
        self.__log.debug("call isUnequal function")
        try:
            if valueA<>valueB:
                return True
            return False
        except:
            self.__log.debug("can not compare isUnequal")
            raise Exception
        
    def __value(self,strg):
        '''
        return a value
        '''
        self.__log.debug("call value function") 
        return strg
    
    def __setDeviceChannel(self,strg):
        '''
        set a device Channel
        '''
        self.__log.debug("call setDeviceChannel function")
        if not set(self.__allowedCMD['setDeviceChannel']) <= set(strg):
            self.__log.error("setDeviceChannel function miss some atribute %s"%(strg.keys()))
            raise Exception
        (deviceID,channelName,value)=(strg.get('deviceID'),strg.get('channelName'),strg.get('value'))
        self.__log.debug("call function setDeviceChannel %s and channelName %s to value: %s"%(deviceID,channelName,value))
        try:
            self.__core.setDeviceChannel(deviceID,channelName,value)
        except:
            self.__log.error("can not set deviceID %s and channelName %s to value: %s"%(deviceID,channelName,value),exc_info=True)
            raise Exception
        
    def __callerValue(self,strg):
        '''
        strg= Caller field
        raise all Exception   
        '''  
        self.__log.debug("call callerValue function")
        if strg not in self.__allowedCMD['getDeviceChannel']:
            self.__log.error("%s is not a caller variable"%(strg))
            raise Exception
        return self.__callerValues.get(strg,"unknown")
    
    def __getDeviceChannel(self,strg):
        '''
        return a value for a device Channel
        
            raise exception on error
        '''
        self.__log.debug("call getDeviceChannel function")
        if not set(self.__allowedCMD['getDeviceChannel']) <= set(strg):
            self.__log.error("getDeviceChannel function miss some atribute %s"%(strg.keys()))
            raise Exception
        (deviceID,channelName)=(strg.get('deviceID'),strg.get('channelName'))
        self.__log.debug("get value of deviceID %s and channelName:%s"%(deviceID,channelName))
        try:
            value=self.__core.getDeviceChannelValue(deviceID,channelName)
            return value
        except:
            self.__log.debug("get no value for deviceID %s and channel %s"%(deviceID,channelName))
            raise Exception
         
    def __dateTimeNow(self,strg=False):
        '''
        return a time stamp
        '''
        return int(time.time())


if __name__ == "__main__":
    
    class core():
        def __init__(self):
            pass
        def getDeviceChannelValue(self,deviceID,channelName):
            return "98"
        def setDeviceChannel(self,deviceID,channelName,value):
            print ("set deviceID %s channel %s to value %s"%(deviceID,channelName,value))
    coreDummy=core()
    log=logging.getLogger()
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    prog=praraphser(coreDummy)
    
    prog.callBack("temp@hmc", "temperatur", "onchange", "test@hmc", 0)