'''
Created on 18.12.2016

@author: uschoen
'''
__version__ = "3.0"


import MySQLdb          #@UnresolvedImport
import logging

class server(object):
    '''
    install the python mysql libery 
    sudo apt-get install python-mysqldb
    ''' 
    def __init__(self,parms,core):
        '''core instance'''
        self.__core=core
        '''default configuration'''
        self.__config={
                     "host":"127.0.0.1",
                     "user":"SQLUSER",
                     "password":"",
                     "db":"hmc",
                     "table":"statistic",
                     "mapping":[]
                }
        self.__config.update(parms)
        ''' logger instance '''
        self.__log=logging.getLogger(__name__) 
        ''' db connection '''  
        self.__dbConnection=False
        
        self.__log.info("build  %s instance"%(__name__))
    
    def callback(self,deviceID,eventTyp,channelName):
        self.__log.debug("callback from deviceID:%s eventTyp:%s channel:%s"%(deviceID,eventTyp,channelName))
        try:
            self.__dbConnect(self.__config.get('host'), self.__config.get('db'), self.__config.get('user'), self.__config.get('password')) 
            self.__mapping(deviceID, channelName)
        except:
            self.__log.error("can not work for deviceID:%s eventTyp:%s channel:%s"%(deviceID,eventTyp,channelName),exc_info=True)
        
    def __mapping(self,deviceID,channel):    
        fieldString=""
        valueString=""
        sql=""
        secound=False
        try:
            for fields in self.__config['mapping']:
                for key in fields:
                    if secound:
                        fieldString+=","
                        valueString+=","
                    secound=True
                    fieldString+=("`%s`"%(key))
                    value=""
                    if key=="deviceID":
                        value=deviceID
                    else:
                        value=self.__core.getDeviceChannelKey(deviceID,channel,fields.get(key))
                    valueString+=("'%s'"%(value))
            sql=("INSERT INTO `%s` (%s) VALUES (%s)"%(self.__config.get('table'),fieldString,valueString))
            self.__excQuery(sql)
            self.__dbClose()
        except :
            self.__log.error("unknown Error at mapping sql:%s"%(sql),exc_info=True)    
        self.__dbClose()

        
    def __excQuery(self,sql):
        '''
        excequed a sql string
        
        sql: sql string
        
        return exception if sql query faild
        '''
        try:   
            self.__dbConnect(self.__config.get('host'),self.__config.get('db'),self.__config.get('user'),self.__config.get('password'))
            cur = self.__dbConnection.cursor()
            self.__log.debug("sql:%s"%(sql))
            cur.execute(sql)
            self.__dbConnection.commit()
        except:
            self.__log.error("error in sql query",exc_info=True)
            raise Exception
    
    def __dbConnect(self,host,db,user,password):
        '''
        connect to the database
        host: hostname
        db: database name
        user: username of the databse
        password: password of the user
        
        raise exeption 
        '''
        if self.__dbConnection:
            return
        self.__log.info("try connect to host:%s with user:%s table:%s"%(host,user,db))
        try:
            self.__dbConnection = MySQLdb.connect(
                                                  host=host,
                                                  db=db,
                                                  user=user, 
                                                  passwd=password
                                                  )
            self.__dbConnection.apilevel = "2.0"
            self.__dbConnection.threadsafety = 2
            self.__dbConnection.paramstyle = "format" 
            self.__log.info("connect to %s:%s succecfull"%(host,db))
            return
        except :
            self.__dbConnection=False
            self.__log.info("DB DataError to %s:%s"%(host,db),exc_info=True)
            raise Exception
                
    def __dbClose(self):
        '''
        close the db connection
        
        fetch the exception
        '''
        try:
            if self.__dbConnection:
                self.__log.info("close db connection to %s"%(self.__config.get('host')))
                self.__dbConnection.close()  
            self.__dbConnection=False
        except:
            self.__log.warning("error at close db connection to host %s"%(self.__config.get('host')),exc_info=True)
            self.__dbConnection=False
    
    def shutdown(self):
        '''
        shutdown
        '''
        self.__log.critical("%s is shutdown"%(__name__))
        self.__dbClose()       
        self.__log.critical("%s is down"%(__name__))    
