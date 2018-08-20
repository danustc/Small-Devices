#!/usr/bin/python


import serial
import struct
import time
import arduino_API

channel_pins = {'488':1, '561':2}
OD_angles = {'0': 0, '1': 45, '2': 90, '3': 135}

class Control(object):
    def __init__(self,port):
        print('Initializing filter wheels.')
        self._api = arduino_API.API(port)
        if self._api.serial.isOpen():
            print("The port is open.")


    def set_OD(self, n_channel, n_OD):
        ch_pin = channel_pins[str(n_channel)]
        print(ch_pin)
        OD_ang = OD_angles[str(n_OD)]
        #self._api.output([ch_pin]) # set the output 
        to_write = struct.pack('>2B', ch_pin, OD_ang)
        print(to_write)
        self._api.write(to_write)



    def shutDown(self):
        if self._api.serial.isOpen():
            self._api.close()
