#!/usr/bin/python
#
# Copyright 2017 Ullrich Schoen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# course: cs108
# laboratory: 1
#
#Created on 
# username: uschoen
# name: Ullrich Schoen
#
# description: a hmc start-up program.

__version__=2.0

import sys
import getopt
import time
import json 
import os
import getpass
import signal
from hmc.core import manager as coreManager
import socket
import logging
import logging.config


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
'''
load configuratin file
'''
def loadConfigurationFile(file):
    '''
    loading configuration file
    '''
    try:
        with open(os.path.normpath(file)) as jsonDataFile:
            dateFile = json.load(jsonDataFile)
        return dateFile 
    except IOError:
        logger.critical("can not find file:%s"%(os.path.normpath(file)), exc_info=True)
        sys.exit()
    except ValueError:
        logger.critical("error in configuration file", exc_info=True)
        sys.exit()
    except :
        logger.critical("error at loading configuration file", exc_info=True)
        sys.exit()
        
def signal_handler(signum, frame):
    logging.critical("Signal handler called with signal %s"%(signum))
    sys.exit()
    
'''
##################################################################################
__MAIN__ 

##################################################################################
'''
    
    
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
        os.chdir(os.path.normpath(configuration['workingdirectoty']))
    except :
        print ("error with the configuration file %s"%(configuration['configfile']))
        sys.exit()
    
    """
    add logger 
    """
    try:
        logger=logging.getLogger(__name__)  
        logging.config.dictConfig(configuration['logging'])
    except:
        print ("can not build logger, starting without logging !")
    
        
    logger.info("startup and run under user:%s"%(getpass.getuser())) 
    logger.info("EasyHMC Version: %s"%(__version__)) 
    logger.info("EasyHMC configuration file: %s"%(configuration['configfile'])) 
    
    try:
        coreInstance=coreManager(getConfiguration('core'))
        while 1:
            for gatewayName in coreInstance.getGatewaysName():
                logger.info("check gateway %s"%(gatewayName['name']))
                gatewayobj=coreInstance.getGatewaysInstance(gatewayName['name'])
                if not gatewayName['enable']:
                    logger.info("gateway %s is disable"%(gatewayName['name']))
                    continue
                if gatewayobj.isAlive():
                    logger.info("gateway %s is alive"%(gatewayName['name']))
                else:
                    logger.error("gateway %s is not alive"%(gatewayName['name'])) 
                    coreInstance.startGateway(gatewayName['instance'])
            logger.info("EasyHMC wait %s sec for next check"%(configuration['checkgatewaysintervall']))
            time.sleep(configuration['checkgatewaysintervall'])    
    except (SystemExit, KeyboardInterrupt):
        logger.critical("control C press!!,system going down !!")  
    except :
        logger.error("unkown error:", exc_info=True)
      
    finally:
        logger.critical("system going down !!")
        if coreInstance:
            coreInstance.shutdown() 
        logger.critical("system is finally down !!")
        sys.exit()
    
    
    
    
    
    
    
    
    
    
    
    
    
    