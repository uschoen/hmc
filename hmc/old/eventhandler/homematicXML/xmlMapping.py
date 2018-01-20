'''
Created on 18.12.2016

@author: uschoen
'''
__version__ = "1.9"


from time import localtime, strftime,sleep
from datetime import datetime
import urllib2,xmltodict

class server(object):
    '''
    classdocs
    '''


    def __init__(self,parms,core,logger=False):
        '''
        Constructor
         '''
        self.__core=core
        self.__config={}
        self.__config.update(self.__loadDefaultArgs())
        self.__config.update(parms)
        self.__logger=logger 
        self.__log("debug","build  %s instance"%(__name__))
    def callback(self,device):
        self.__log("debug","callback from device id %s"%(device.getAttributeValue('deviceID')))
        if not "iseID" in device.getAllAttribute():
            self.__log("error","device id %s has no attribut iseID"%(device.getAttributeValue('deviceID')))
            return
        url=("%s%s?ise_id=%s&new_value=%s"%(self.__config['hmHost'],self.__config['url'],device.getAttributeValue('iseID'),device.getAttributeValue('value')))
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
                    self.__log("error","can not found iseID %s"%(device.getAttributeValue('iseID')))
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
                
        '''
         http://192.168.3.90/config/xmlapi/statechange.cgi?ise_id=29702&new_value=45.60
        '''
     
    def __loadDefaultArgs(self):
        args={"hmHost":"http://127.0.0.1",
             "url":"/config/xmlapi/statechange.cgi"
             }
        return args
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
            
            
            
            
if __name__ == "__main__":            
    class logger(object):
        def write(self,arg):
            print arg['messages']
    
    class device(object):
        def __init__(self):
            self.__config={
                "deviceID":
                    {
                        "value":"999",
                        "typ":"init"
                    },
                "value":
                    {
                        "value":"6",
                        "typ":"init"
                    },
                "iseID":
                    {
                        "value":"297042",
                        "typ":"init"
                    },
                 }
        def getAttributeValue(self,value):
            return self.__config[value]['value']
        def getAllAttribute(self):
            return self.__config
            
            
            
    args={"hmHost":"http://192.168.3.99",
             "url":"/config/xmlapi/statechange.cgi"
             }
    deviceObj=device()
    mapper = server(args,False,logger())
    print("start")
    print("xml Mapper  build")
    mapper.callback(deviceObj)
    while True:
        print("main wait 10 sec")
        sleep(10) 
'''
sudo pip install xmltodict
'''        