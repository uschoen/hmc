'''
Created on 16.01.2018

@author: uschoen
'''


__version__ = 3.1

class coreProgram:
    '''
    classdocs
    '''
    def addProgram(self,programName,program,test=True):
        '''
        restore a program, only for restart/start
        '''
        self.logger.debug("add program %s"%programName)
        self.__addProgram(programName,program,True)
    
    def updateProgram(self,programName,program,test=True):
        '''
        restore a program, only for restart/start
        '''
        self.logger.debug("update program %s"%programName)
        self.__addProgram(programName,program,True)
    
    def restoreProgram(self,programName,program,test=True):
        '''
        restore a program, only for restart/start
        '''
        self.logger.debug("restore program %s"%programName)
        self.__addProgram(programName, program,True)
    
    def __addProgram(self,programName,program,test=False):
        try:
            self.program[programName]=program
        except:
            self.logger.error("can not add program %s"%(programName))

    def runProgram(self,deviceID,channelName,eventTyp,programName,programDeep=0,test=False):
        if programName not in self.program:
            self.logger.error("can not fnd programName %s"%programName)
            raise Exception
        try:
            program=self.program.get(programName)
            self.programPraraphser.parsingProgram(self,deviceID,channelName,eventTyp,programName,program,programDeep)
        except:
            self.logger.error("can not strat program %s"%programName)

    
    