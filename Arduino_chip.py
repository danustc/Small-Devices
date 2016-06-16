import time
from arduino import Arduino


def ard_reset(port = '/dev/ttyACM0'):
    ard = Arduino(port)
    ard.close()



def rotor_operation(ard, pin, status = 0):
#     ard.output([pin])
    if status == 1:
        ard.analogWrite(pin, 80)
    else:
        ard.analogWrite(pin,0)
    



def on_off(ard):
    command = raw_input("Type something..: (on/ off / bye )")
    if command =="on":
        print "The LED is on..."
        ard.setHigh(13) 
        time.sleep(5)
        on_off(ard)
    elif command =="off":
        print "The LED is off..."
        time.sleep(5) 
        ard.setLow(13)
        on_off(ard)
    elif command =="bye":
        print "See You!..."
        time.sleep(5) 
        ard.close()
    else:
        print "Sorry..type another thing..!"
        on_off(ard)


# ard_reset()