'''
Created on 23.09.2017

@author: uschoen
'''
__version__=0.1
import sys,getopt,time,json,os,getpass,signal
from datetime import datetime
from multilogger import dispatcher as LogDispatcher
from hmc.core import maganer as coreManager
import socket



'''
getConfiguration
'''
def getConfiguration(confName=False):
    tempconf={}
    if confName in configuration:
        tempconf=configuration[confName]
        tempconf['global']=configuration['global']
    return tempconf
"""
usage command line
"""
def usageCMD():
    '''
    command line menu for -help --h
    '''
    print sys.argv[0], "--config=configfile [--daemon] "
    print sys.argv[0], "--help (-h) this menu"
    print sys.argv[0], "--version (-v) show version of HMC"
    print sys.argv[0], "--daemon (-d) run as daemon"  
"""
get consol options
"""
def getOptions():
    '''
    check command line argument
    --h -help helpmenu
    --v -version show version
    --d -daemon run as daemon, default false
    --c -config config file, default etc/config.json
    '''
    shortOptions = 'hdvc:'
    longOptions = ['help', 'version','config=', 'daemon']
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortOptions, longOptions)
        return opts
    except getopt.GetoptError:
        print "please use:"
        usageCMD()
        sys.exit() 
"""
Logging
"""
def log (level="unkown",messages="no messages"):
    '''
    logger converter
    '''
    global logger
    if logger:
        dt = datetime.now()
        meassage={}
        meassage['package']=__name__
        meassage['level']=level
        meassage['messages']=messages
        meassage['time']=time.strftime("%d.%b %H:%M:%S", time.localtime())
        meassage['microsecond']=dt.microsecond
        logger.write(meassage) 
"""
load configuratin file
"""
def loadConfigurationFile(file):
    '''
    loading configuration file
    '''
    try:
        with open(os.path.normpath(file)) as jsonDataFile:
            dateFile = json.load(jsonDataFile)
        return dateFile 
    except IOError:
        print ('can not find file: '+os.path.normpath(file))
        sys.exit()
    except ValueError:
        e = sys.exc_info()[1]
        print ('error in config file: '+os.path.normpath(file))
        print("error: %s" % e )
        sys.exit()
    except :
        print("UNKOWN ERROR in script:")
        print(sys.exc_info())
        tb = sys.exc_info()
        for msg in tb:
            print("Traceback Info:%s"%(msg))
        sys.exit()
        
def signal_handler(signum, frame):
    log("emergency","Signal handler called with signal %s"%(signum))
    exit()
    
"""
##################################################################################
__MAIN__ 

##################################################################################
"""
if __name__ == '__main__':
    """
    Gloable Variablen
    """
    configuration=  { 'configfile':'etc/'+socket.gethostname()+'/config.json',
                      'daemon':False, 
                      'global':{
                                'host':socket.gethostname()
                               }           
                    }        
    logger=False
    CoreManager=False
    coreInstance=False
    signal.signal(signal.SIGINT, signal_handler) 
    """
    load command line option
    """       
    for o, a in getOptions():
        if o == "--help" or o == "-h":
            print "HELP:"
            usageCMD()
            sys.exit()
        elif o == "--config" or o == "-c":
            print "use config file:", a
            configuration['configfile']=a
        elif o == "--daemon" or o== "-d":
            print "run as daemon:", a
            configuration['daemon']=True
        elif o == "--version" or o=="-v":
            print ("version: %s on host %s"%(__version__,socket.gethostname()))
            sys.exit()
    """
    load configuration file
    """
    try:
        configuration.update(loadConfigurationFile(configuration['configfile']))
    except :
        print ("error with the configuration file")
        exit()
    
    """
    add multilogger 
    """
    try:
        if 'multilogger' in configuration:
            if configuration['multilogger']['enable']:
                logger=LogDispatcher.core(getConfiguration('multilogger'))
    except:
        print ("warning can not bulid logger, start without logging")
        
    log("info", "startup and run under user:%s"%(getpass.getuser())) 
    log("info", "EasyHMC Version: %s"%(__version__)) 
    log("info", "EasyHMC configuration file: %s"%(configuration['configfile'])) 
    
    try:
        coreInstance=coreManager(getConfiguration('core'),logger)
        while 1:
            for gatewayName in coreInstance.getGatewaysName():
                log("info", "check gateway %s"%(gatewayName['name']))
                gatewayobj=coreInstance.getGatewaysInstance(gatewayName['name'])
                if not gatewayName['enable']:
                    log("info", "gateway %s is disable"%(gatewayName['name']))
                    continue
                if gatewayobj.isAlive():
                    log("info", "gateway %s is alive"%(gatewayName['name']))
                else:
                    log("error", "gateway %s is not alive"%(gatewayName['name'])) 
                    coreInstance.startGateway(gatewayName['instance'])
            log("info", "EasyHMC wait %s sec for next check"%(configuration['checkgatewaysintervall']))
            time.sleep(configuration['checkgatewaysintervall'])    
    except KeyboardInterrupt:
        log("emergency","control C press!!,system going down !!")  
    except :
        log("error",sys.exc_info())
        tb = sys.exc_info()
        for msg in tb:
            log("error","Traceback Info:" + str(msg)) 
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log("error","%s %s %s "%(exc_type, fname, exc_tb.tb_lineno))
    finally:
        log("emergency","system going down !!")
        if coreInstance:
            coreInstance.shutdown() 
        log("emergency","system is finally down !!")
        sys.exit()
    
    
    
    
    
    
    
    
    
    
    
    
    
    