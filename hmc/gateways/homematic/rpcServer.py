'''
Created on 22.10.2016

@author: uschoen
'''

__version__= "1.9"

import threading

import xmlrpclib,socket,sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import urllib2,xmltodict
import traceback



from time import localtime, strftime, sleep, time
from datetime import datetime
from getpass import fallback_getpass


class hmc_rpc_callback:
    def __init__(self,parms,core,logger,timer):
        self.__core=core
        self.__config=parms
        self.__timer=timer
        self.__devices={}
        self.__config['host']=str(socket.gethostbyaddr(socket.gethostname())[0])
        self.__logger=logger
    def event(self, interface_id, deviceAddress, chanel, value,*unkown):
        self.__timer()
        self.__log("debug","event: interface_id = %s, address: %s, value_key = %s, value = %s" % ( interface_id,deviceAddress, chanel, str(value) ) )
        if deviceAddress not in self.__devices:
            self.__log("error","unkown device adress %s"%(deviceAddress))
            return
        deviceID=("%s_%s@%s.%s"%(deviceAddress,chanel,self.__config['gateway'],self.__config['host']))   
        if deviceID not in self.__core.getAllDeviceId():
            typ=self.__devices[deviceAddress]['typ']
            self.__log("info","add new devicesID:%s"%(deviceID))       
            self.__core.addDevice(deviceID,typ)
        self.__core.setValue(deviceID,value)
    def listMethods(self,*args):
        self.__timer()
        self.__log("error","listMethods")
        print "methode"
        return ''
    def listDevices(self,*args):
        self.__timer()
        self.__log("error","listDevices")
        for arg in args:
            self.__log("error","listDevices %s"%(arg))
            print "listdevice"
        return ''
    def newDevices(self, interface_id, allDevices):
        self.__timer()
        self.__log("debug","get newDevices ")
        for device in allDevices:
            if device['PARENT']=="":
                self.__log("debug","ignore type is parent")
            else:
                typ=("%s_%s"%(device['PARENT_TYPE'],device['TYPE']))      # 'PARENT_TYPE': 'HMW-IO-12-Sw7-DR'      
                                                                        # 'TYPE': 'MAINTENANCE'                                        """
                deviceAddress=device['ADDRESS']                         # 'ADDRESS': 'JEQ0149163:0' 
                if deviceAddress not in  self.__devices:
                    self.__devices[deviceAddress]={}
                self.__devices[deviceAddress]['typ']=typ
                self.__log("debug","add internel device adress %s with typ %s"%(deviceAddress,self.__devices[deviceAddress]['typ']))
        return ''
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
    

class server(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self,params,core,logger=False):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.running=1
        self.__core=core
        self.__timer=int(time())
        self.__timeoutnow=False
        self.__config=params
        self.__config['host']=str(socket.gethostbyaddr(socket.gethostname())[0])
        self.__logger=logger
        self.__log("debug","build  %s instance"%(__name__))
    def run(self):
        self.__log("info", "start thread")
        while not self.__adding_server():
            self.__log("error","can not start RPC server wait 120 sec and ty again")
            sleep(120)
        self.__log("info","wait 2 sec to INIT RPC Connect")
        sleep(2)
        self.__RPC_connect()
        self.__RPC_Init()
        while self.running:
            if (self.__timer+self.__config['timeout'] < int(time())):
                self.__log("error","timeout, no meassages from homematic")
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
        self.__log("warning","thread %s stop"%(__name__))
        
    def __sendcommand(self):
        self.__log("error","send meassages to homematic")
        HMurl=self.__config['hmXmlUrl']
        iseID=self.__config['iseID']
        value=self.__config['iseIDValue']
        url=("%s?ise_id=%s&new_value=%s"%(HMurl,iseID,value))
        self.__log("debug","url is %s "%(url))
        try:
            response = urllib2.urlopen(url)
            httcode=response.getcode()
            self.__log("debug","http response code %s"%(httcode))
            if  httcode<>200:
                self.__log("error","can not send request to url") 
                return
            xml=response.read()
            self.__log("data","xml response %s"%(xml))
            HMresponse=xmltodict.parse(xml)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    self.__log("debug","value successful change")
                elif "not_found" in HMresponse['result']: 
                    self.__log("error","can not found iseID %s"%(iseID))
                else:
                    self.__log("warning","get some unkown answer %s"%(xml))
            else:
                self.__log("warning","get some unkown answer %s"%(xml)) 
        except urllib2.URLError:
            self.__log("error","get some error at url request")
        except ValueError:
            self.__log("error","some error at request, check configuration")
        except :
            self.__log("emergency","somthing going wrong !!!")    
        
    def __adding_server(self):
        try:
            self.__log("info","rpc Server %s:%s start"%(self.__config["rpc_ip"],self.__config["rpc_port"]))
            server = SimpleXMLRPCServer((self.__config["rpc_ip"],int(self.__config["rpc_port"])))
            server.logRequests=False
            server.register_introspection_functions() 
            server.register_multicall_functions() 
            server.register_instance(hmc_rpc_callback(self.__config,self.__core,self.__logger,self.resetTimer))
            self.__rpc_server = threading.Thread(target=server.serve_forever)
            self.__rpc_server.start()
            self.__log("info","rpc Server Start")
            return True
        except Exception as e:
            self.__log("error","can not start rpc server %s -"%(e))
            traceback.print_exc()
            server=False
            return False
    '''
    shutdown
    '''
    def shutdown(self):
        self.__log("emergency","rpc Server stop")
        self.__RPC_connect()
        self.__RPC_stop()
        self.__log("emergency","rpc Server is stop")
    '''
    Logging Intance
    '''
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
    def __RPC_Init(self):
        self.__log("info","RPC Init: init(http://%s:%i, '%s')" % (self.__config["rpc_ip"],int(self.__config["rpc_port"]), self.__config["hm_interface_id"]) )
        try:
            self.proxy.init("http://%s:%i" % (self.__config["rpc_ip"], int(self.__config["rpc_port"])), self.__config["hm_interface_id"])
            self.__log("debug","Proxy initialized")
        except:
            self.__log("error","Failed to initialize proxy")
            raise Exception
    def __RPC_connect(self):
        self.__log("debug","Creating proxy. Connecting to http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
        try:
            self.proxy = xmlrpclib.ServerProxy("http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
            self.__log("debug","start rpc data from homematic")
        except:
            self.__log("warning","Failed connecting to proxy at http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
            raise Exception
    def __RPC_stop(self):
        self.__log("debug","stopping RPC data from Homematic. Connecting to http://%s:%i" % (self.__config["hm_ip"], int(self.__config["hm_port"])))
        self.__log("info","RPC Init STOP: init(http://%s:%i)" % (self.__config["rpc_ip"],int(self.__config["rpc_port"])) )
        try:
            self.proxy.init("http://%s:%i" % (self.__config["rpc_ip"], int(self.__config["rpc_port"])))
            self.__log("debug","stopped rpc data from homematic")
        except:
            self.__log("error","Failed to stop RPC ")
            raise Exception
    def resetTimer(self):
        self.__log("debug","reset timeout timer")
        self.__timer=int(time())
        self.__timeoutnow=False