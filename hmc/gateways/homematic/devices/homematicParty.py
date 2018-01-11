'''
Created on 11.01.2018

@author: uschoen
'''
import time
import datetime


class partyChannel(object):
    '''
    classdocs
    '''
    def _cleanUPpartyFlag(self):
        try:
            if self._partyTimer<time.time():
                self.logger.debug("reset partyflag")
                self._partyFlag=0;
                for channelName in self._partyChannels:
                    self._partyChannels[channelName]['value']=0
                self._partyTimer=int(time.time()+3)
        except:
            self.logger.critical("can not clean up party flag",exc_info=True)
    
    def _addParty(self,channelName,value):
        '''
        add party flags
        '''
        try:
            self.logger.debug("calc party time, get channel %s"%(channelName))
            self._addSysChannels()
            self._cleanUPpartyFlag()
            self._partyChannels[channelName]['value']=value
            self._partyFlag=self._partyFlag|self._partyChannels[channelName]['flag']
            if self._partyFlag==255:
                self._calcParty()
        except:
            self.logger.critical("can not finish addparty",exc_info=True)
        
    def _calcParty(self):
        '''
        calculate the party stop and start time
        '''
        try:
            '''
            calc party start time
            '''
            partyStartH=int(self._partyChannels['party_start_time']['value']/60)
            partyStartM=int(self._partyChannels['party_start_time']['value']-(partyStartH*60))
            partyStartY=int("20%02i"%(self._partyChannels['party_start_year']['value']))
            partyStart=datetime.datetime(partyStartY,self._partyChannels['party_start_day']['value'],self._partyChannels['party_start_month']['value'],partyStartH,partyStartM)
            partyStart=partyStart.strftime("%s")
            '''
            update channel
            '''
            self._core.setDeviceChannelValue(self.deviceID,'partystarttime',partyStart)    
            '''
            calc party stop time
            '''
            partyStopH=int(self._partyChannels['party_stop_time']['value']/60)
            partyStopM=int(self._partyChannels['party_stop_time']['value']-(partyStopH*60))
            partyStopY=int("20%02i"%(self._partyChannels['party_stop_year']['value']))
            partyStop=datetime.datetime(partyStopY,self._partyChannels['party_stop_day']['value'],self._partyChannels['party_stop_month']['value'],partyStopH,partyStopM)
            partyStop=partyStop.strftime("%s")
            '''
            update channel
            '''
            self._core.setDeviceChannelValue(self.deviceID,'partystoptime',partyStop) 
        except:
            self.logger.critical("can not calc party time",exc_info=True)   