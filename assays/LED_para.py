# behavioral assay 
import time
import numpy as np
import pandas as pd
import new_era
from arduino import Arduino
from Arduino_chip import ard_reset
from random import randint
import serial
# read the settings 

"""
About configs: 
column 0: durations of each steps 
column 1: light stimuli
column 2: food delivery 
column 3: syringe pump on
"""

dia_1ml = 4.699
flowrate = 4000
pin_LED = 13
pin_Servo = 9
CONFIG_CS = np.array([15,1,0,0]) # configuration for conditioned stimulus 
CONFIG_US = np.array([10,1,1,0]) # configuration for unconditioned stimulus (feeding)
CONFIG_REST = np.array([30,0,0,0]) # configuration for inter-trial sessions (the duration is subject to change)
CONFIG_INTER = np.array([-1,0,0,0])
Nrepeat = 20
# for loop: execute the steps one by one 
# CS_sequence = 'RCUICUICUICUICUICUICUICUICUICUICUICUI'

# Tflag_name = 'Btest'


def random_split(N0):
    # split N0 randomly into non-zero chunks 
    npart = randint(2, N0) # How many slices 
    div = np.random.choice(N0-1, npart-1, replace = False)+1     # randomly select npart - 1 divisions
    div.sort()
    
    div = np.concatenate(([0],div))
    div = np.concatenate((div,[N0])) # update div to include the head and the tail
    arr_split = np.diff(div)
    return arr_split
    


class Assay():
    # Initialize the pumps
    def __init__(self, fname, nrepeat = 10, ard_port = '/dev/ttyACM0', pump_port = '/dev/ttyUSB0'):
        self.__observers = [] # define an observer
        self.step = -1 # before execution
        self.conf_label = 'R'+ 'CUCI'*nrepeat
        print(self.conf_label)
        self.n_session = 1+ nrepeat*4
        self.sessions = len(self.conf_label) # the number of steps
        self. __construct__()
        self.time_flag = pd.Series(np.zeros(self.n_session), index = list(self.conf_label))
        ard_reset(ard_port)
        self.ard = Arduino(ard_port)
        self.ard.output([pin_LED, pin_Servo])
        self.ard.setLow(pin_LED) # Initial 
        self.fname = fname
        self.pump_init(pump_port)
        
    
    def blink_start(self, nblink = 5):
        # give a blinking start, the LED blinks at 1 Hz 
        for ii in range(nblink):
            self.ard.setHigh(pin_LED)
            time.sleep(0.50)
            self.ard.setLow(pin_LED)
            time.sleep(0.50)
            print(ii+1)
            
            
        millis = int(round(time.time() * 1000))
        self.onset = millis
        
        
        
    def pump_init(self, pump_port):    
        self.pser = serial.Serial(pump_port,19200,timeout=.1)
        print('connected to',self.pser.name)
        pumps = new_era.find_pumps(self.pser)
        self.pump = pumps[0]
        self.infuse = False
        new_era.set_diameter(self.pser, self.pump, dia_1ml) 
        new_era.set_direct(self.pser, self.pump, 1)
        new_era.set_rate(self.pser, self.pump, flowrate)
        


    def register_observer(self,observer):
        self.__observers.append(observer)
    
    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.notify(self, *args, **kwargs)
            
            
        
    def __construct__(self):
        # construct the configuration array 
        self.CS_config = np.zeros([self.n_session, 4])
        ii = 0
        for ch in self.conf_label:
            if (ch == 'R'):
                self.CS_config[ii] = CONFIG_REST
            elif (ch == 'C'):
                self.CS_config[ii] = CONFIG_CS
            elif (ch == 'U'):
                self.CS_config[ii] = CONFIG_US
            else:
                self.CS_config[ii] = CONFIG_INTER
            ii+=1 
        # then, we need to update duration of intersessions 
        inter_pos = self.CS_config[:,0] < 0  # take out the positions of intersessions, a boolean array 
        inter_dur = self.CS_config[inter_pos,0]
        self.CS_config[inter_pos,0] = np.random.randint(40, 70, size = len(inter_dur)) 
        
        print(self.CS_config)
        self.duration = self.CS_config[:,0].sum()/60.0
        print('Total experimental time: %4.1f min' %self.duration)
   
    def blink(self, duration, freq=2):
        # blink the LED
        # duration: the duration of blinking 
        nblink = int(duration * freq)
        thp = 1 / (freq*2.0) # half-period 
         
        for ii in range(nblink):
            self.ard.setHigh(pin_LED)
            time.sleep(thp)
            self.ard.setLow(pin_LED)
            time.sleep(thp)
            
        
        
    def run_step(self, sblink = False):
        millis = int(round(time.time() * 1000))
        self.step +=1 
        self.time_flag[self.step] = millis
        self.notify_observers(self.step) 
        config_list = self.CS_config[self.step]
        print(config_list[0]) 
        # take the row 
        # turn on or off all the stimuli
        
       
        # turn on or off the delivery 
        if config_list[2] == 0:
            if(self.infuse == True):
                new_era.stop_pump(self.pser, self.pump)
                self.infuse = False
        elif config_list[2] == 1:
            if(self.infuse == False):
                new_era.set_rate(self.pser, self.pump, flowrate) 
                new_era.run_all(self.pser)
                self.infuse = True
    
    
        if config_list[1] == 0: 
            self.ard.setLow(pin_LED) # keep the LED off
            time.sleep(config_list[0]) 
        elif config_list[1] == 1:
            if sblink: 
                self.blink(config_list[0])
            else:
                self.ard.setHigh(pin_LED)
                time.sleep(config_list[0])
             
        # insert or retract the feeding tube
#         if config_list[3] == 0:
#             self.ard.analogWrite(pin_Servo, 0)
#         elif config_list[3] == 0:
#             self.ard.analogWrite(pin_Servo, 80)
        
#         time.sleep(config_list[0])
#         self.terminate_step()
          
    
    def terminate_step(self):
        # terminate a step
        
        self.ard.setLow(pin_LED)
        self.ard.analogWrite(pin_Servo, 0)
        new_era.stop_pump(self.pser, self.pump)

    def run_through(self, sblink=False):
        self.blink_start()
        self.step  = -1
        ii = 0
        for ii in range(self.n_session):
            self.run_step(sblink)
            print('The'+ str(ii) + 'th session.') 



#     def shuffle_steps(self):
#         # shuffle the steps of 
#         CS_total = np.inner(self.CS_config[:,0], self.CS_config[:,1]) # inner product of the first two columns, total duration of CS
#         US_total = np.inner(self.CS_config[:,0], self.CS_config[:,2]) # total duration of US
#         time_total = self.CS_config[:,0].sum() # The total amount of time should be equal 
# 
#         # use 10 seconds as a unit of the         
#         NC_chunk = np.round(CS_total/10.).astype('int')
#         NU_chunk = np.round(US_total/10.).astype('int')
#         Total_chunk = np.round(time_total/10.).astype('int')
#      
#         shuff_LED = random_split(NC_chunk)
#          
        
        
    def close(self):
        # destruct the class
        self.ard.setLow(pin_LED)
        self.ard.close()
    
        np.save('../Data/'+self.fname, self.time_flag)
        pd.Series.to_csv(self.time_flag, '../Data/'+self.fname+'.csv')
        print("Arduino port closed. ")
        
        
def main():
    Tflag_name = 'TF_G0_D3_condition'
    Behave_assay = Assay(Tflag_name, Nrepeat)
    Behave_assay.run_through(False)
    print(Behave_assay.onset)
    print("Duration: %4.1f" %Behave_assay.duration)
    Behave_assay.close()
    
if __name__ == '__main__':
    main()