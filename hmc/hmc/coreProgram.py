'''
Created on 16.01.2018

@author: uschoen
'''


class coreProgram:
    '''
    classdocs
    '''
    def addProgram(self):
        pass
    
    def updateProgram(self):
        pass
    
    def restoreProgram(self):
        pass

    def runProgram(self,deviceID,channelName,eventTyp,programName):
        if programName not in self.program:
            self.logger.error("can not fnd programName %s"%programName)
            return
        try:
            program=self.program.get(programName)
            self.programPraraphser.praraphseProgramm(self)
        except:
            self.logger.error("can not strat program %s"%programName)

    
    