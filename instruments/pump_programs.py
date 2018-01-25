import sys
import serial
import new_era



syringes = {' 1 ml BD':'4.699',
            ' 3 ml BD':'8.585',
            ' 5 ml BD':'11.99',
            '10 ml BD':'14.60',
            '30 ml BD':'21.59',
            'Freeman ':'50.00'}


class PumpControl():
    def __init__(self):
        self.serial_port = "/dev/ttyUSB0"
    
    def stop_all(self):
        self.runbtn.setChecked(0)
        self.volbtn.setChecked(0)        
        self.stopbtn.setChecked(1)        
        new_era.stop_all(self.ser)
        self.curr_state = 'Stopped'
        self.statusbar.setText('Status: '+self.curr_state)
        self.commandbar.setText('Last command: stop all pumps') 
        [self.currflow[pump].setText('0 ul/hr') for pump in self.rates]
        self.prime_state = set()
        [self.prime_btns[p].setChecked(0) for p in self.rates]

    def run_update(self):
        #check if the flow rates are legit numbers, if not set to zero
        self.runbtn.setChecked(1)
        self.stopbtn.setChecked(0)
        rates = {}
        volumes = {}
        for pump in self.rates:
            if str(self.rates[pump].text()).strip()[1:].isdigit(): #kinda a hack to allow negative numbers
                rates[pump] = str(self.rates[pump].text()).strip()
            else:
                rates[pump] = '0'
                self.rates[pump].setText('0')
            # if the pump volume is set 
            if str(self.volume[pump].text()).strip()[1:].isdigit():
                volumes[pump] = str(self.volume[pump].text()).strip()
            else:
                volumes[pump] = '0'
            print(('rate of pump ' + str(pump)))
            print((rates[pump]))
            # added by Dan on 04/05    

        if self.curr_state=='Running':
            new_era.stop_all(self.ser)
            new_era.set_rates(self.ser,rates)
            new_era.run_all(self.ser)
            actual_rates = new_era.get_rates(self.ser,list(rates.keys()))
            self.commandbar.setText('Last command: update '+', '.join(['p%i=%s'%(p,actual_rates[p]) for p in actual_rates]))
            [self.currflow[pump].setText(actual_rates[pump]+' ul/hr') for pump in actual_rates]
                
        if self.curr_state=='Stopped':
            new_era.set_rates(self.ser,rates)
            new_era.run_all(self.ser)
            self.curr_state = 'Running'
            self.statusbar.setText('Status: '+self.curr_state)
            actual_rates = new_era.get_rates(self.ser,list(rates.keys()))
            self.commandbar.setText('Last command: run '+', '.join(['p%i=%s'%(p,actual_rates[p]) for p in actual_rates]))
            [self.currflow[pump].setText(actual_rates[pump]+' ul/hr') for pump in actual_rates]
                 
    def update_syringe(self,pump):
        if self.curr_state == 'Stopped':
            dia = syringes[str(self.mapper.mapping(pump).currentText())]
            print(dia)
            new_era.set_diameter(self.ser,pump,dia)
            dia = new_era.get_diameter(self.ser,pump)
            self.commandbar.setText('Last command: pump %i set to %s (%s mm)'%(pump,self.mapper.mapping(pump).currentText(),dia))
        else:
            self.commandbar.setText("Can't change syringe while running")

    def prime_pumps(self,pump):
        if self.curr_state == 'Stopped':
            if pump not in self.prime_state: # currently not priming
                new_era.prime(self.ser,pump)
                self.commandbar.setText('Last command: priming pump %i'%pump)
                self.statusbar.setText('Status: Priming')
                self.prime_state.add(pump)# add to prime state
            else: # currently priming
                new_era.stop_pump(self.ser,pump)
                self.commandbar.setText('Last command: stopped pump %i'%pump)
                self.prime_state.remove(pump)# remove prime state
                if len(self.prime_state)==0: self.statusbar.setText('Status: Stopped')# if this is the last one, show status=Stopped
            actual_rates = new_era.get_rates(self.ser,list(self.rates.keys()))
            self.currflow[pump].setText(actual_rates[pump]+' ul/hr')
        else:
            self.commandbar.setText("Can't prime pump while running")
            self.prime_btns[pump].setChecked(0)

    def deliver_volume(self,pump):
        self.volbtn.setChecked(1)
        self.stopbtn.setChecked(0)
        if self.curr_state == 'Stopped':
            print("Volume to be delivered:")
            print(str(self.volume[pump].text()).strip())
            try:
                vol= float(self.volume[pump].text().strip())
                print("Volume", vol)
            except ValueError:
                print("Not a float")
                vol = 50.00
            print("Finished setting volume!")
        self.volbtn.setChecked(0)
        self.stopbtn.setChecked(1)
        new_era.set_vol(self.ser,pump, vol)
        new_era.run_pump(self.ser, pump)

    def habituate(self,pump):
        self.habitbtn.setChecked(1)
        self.stopbtn.setChecked(0)
        new_era.set_direct(self.ser, pump,1)
        new_era.run_stop(self.ser, pump, 100)
        print('Withdraw:')
        new_era.set_direct(self.ser, pump, -1)
        new_era.run_stop(self.ser, pump, 100)
        self.habitbtn.setChecked(0)          
        self.stopbtn.setChecked(1)
            
                    
            
    def shutdown(self):
        self.stop_all()
        self.ser.close()
        

if __name__ == '__main__':
    main()
