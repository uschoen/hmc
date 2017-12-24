'''
Created on 24.12.2017
@author: uschoen

'''
from hmc.devices.defaultDevice import device

__version__="2.0"


class device(device):
    def _name_(self):
        return "fs20"
    
    
    def _codeTranslation(self,code):
        code={
            '00':0,                        #off
            '01':6.25,                     #an, 6,25% Einschalten auf Helligkeitsstufe 1 (min.)
            '03':12.5,                     #an, 12,5%
            '04':12.5,
            '05':12.5,
            '06':12.5,
            '07':12.5,
            '08':12.5,
            '09':12.5,
            '10':12.5,
            '11':12.5,
            '12':12.5,
            '13':12.5,
            '14':12.5,
            '15':93.5,
            '16':100,                         #an, 100% Einschalten auf Helligkeitsstufe 16 (max.)
            '17':"",                          #an, alter Wert Auf letztem Helligkeitswert einschalten
            '18':"",                          #toggle Wechsel zwischen aus? und  an, alter Wert
            '19':"",                          #dim up Eine Helligkeitsstufe heller
            '20':"",                          #dim down Eine Helligkeitsstufe dunkler
            '21':"",                          #dim up and down ..., + bis max, kurz warten, - bis min, kurz warten, 
            '22':"",                          #timeset Timerprogrammierung (Start, Ende)
            '23':"",                          #send status Nur bei bidirektionalen Komponenten!
            '24':"",                          #aus, fuer Timerzeit
            '25':"",                          #an, 100%, fuer Timerzeit
            '26':"",                          #an, alter Wert, fuer Timerzeit
            '27':"",                          #reset (auf Auslieferzustand)
            '28':"",                          #frei
            '29':"",                          #frei
            '30':"",                          #frei
            '31':""                           #frei
        }