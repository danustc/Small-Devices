import sys
import os
import serial
from PyQt5 import QtGui, QtWidgets, QtCore
import pump_design
import new_era
import time
from functools import partial
from collections import deque
from threading import Timer, Thread, Event

serial_port = "/dev/ttyUSB0"
syringes = {' 1 ml BD':'4.699',
            ' 3 ml BD':'8.585',
            ' 5 ml BD':'11.99',
            '10 ml BD':'14.60',
            '30 ml BD':'21.59',
            'Freeman ':'50.00'}

class pump_ui(object):

    def __init__(self):
        try:
            self.ser = serial.Serial(serial_port,19200,timeout=.1)
            print('Connected to:', self.ser.name)
            pumps = new_era.find_pumps(self.ser)
            print(pumps)
            self.pump = pumps[0]
        except OSError:
            print('Cannot find the port.')
            sys.exit(1)

        self._app = QtWidgets.QApplication(sys.argv)
        self._window = QtWidgets.QWidget()
        self._window.closeEvent = self.shutDown

        self._ui = pump_design.Ui_Form()
        self._ui.setupUi(self._window)

        # set the default value
        self.set_default()
        self.n_steps = 0

        # Following are the definition of button and lineEdit functions
        self._ui.pushButton_godefault.clicked.connect(self.go_default)
        self._ui.pushButton_run.clicked.connect(self.run_pump)
        self._ui.pushButton_stop.clicked.connect(self.stop_pump)
        self._ui.pushButton_adds.clicked.connect(self.add_step)
        self._ui.pushButton_runpro.clicked.connect(self.run_protocol)
        self._ui.lineEdit_rate.returnPressed.connect(partial(self.set_rate))
        self._ui.lineEdit_volume.returnPressed.connect(partial(self.set_vol))
        # ------------------Done with definition of buton and lineEdit functions
        self.protocol_threads = deque()
        self.protocol_list = []
        self.isrunning = False

        self._window.show()
        self._app.exec_()


    def go_default(self):
        self.set_vol(self.default_volume)
        self.set_rate(self.default_rate)

    def set_default(self, rate = None, vol = None, direct = None):
        if rate is None:
            rate = int(self._ui.lineEdit_rate.text())
        self.default_rate = rate
        if vol is None:
            vol = float(self._ui.lineEdit_volume.text())
        self.default_volume = vol

        if direct is None:
            if self._ui.radioButton_withdraw.isChecked():
                self.default_dir = 'W'
            else:
                self.default_dir = 'F'
        else:
            self.default_dir = direct

    def run_pump(self):
        return new_era.run_pump(self.ser,self.pump)


    def set_vol(self, vol = None):
        if vol is None:
            vol = float(self._ui.lineEdit_volume.text())
        self.vol = vol
        new_era.set_vol(self.ser, self.pump, self.vol)

    def set_rate(self, rate=None):
        if rate is None:
            rate = int(self._ui.lineEdit_rate.text())
        self.rate = rate
        new_era.set_rate(self.ser, self.pump, self.rate)
        self._ui.lcdNumber_current.display(self.rate)

    def load_protocol(self, protocol):
        '''
        protocol: two-column arrays, the first colume specifies the time at which the volumes are delivered, and the second
        '''
        self.time_stamps = protocol[:,0]
        self.deliveries = protocol[:,1]

    def add_step(self):
        row_position = self._ui.tableWidget_steps.rowCount()
        self._ui.tableWidget_steps.insertRow(row_position)
        # set items in the table
        item_time = QtWidgets.QTableWidgetItem()
        time_string = self._ui.lineEdit_deltime.text()
        item_time.setText(time_string)
        self._ui.tableWidget_steps.setItem(row_position, 0, item_time)

        item_rate= QtWidgets.QTableWidgetItem()
        rate_string = self._ui.lineEdit_rate.text()
        item_rate.setText(rate_string)
        self._ui.tableWidget_steps.setItem(row_position, 1, item_rate)

        item_vol= QtWidgets.QTableWidgetItem()
        vol_string= self._ui.lineEdit_volume.text()
        item_vol.setText(vol_string)
        self._ui.tableWidget_steps.setItem(row_position, 2, item_vol)
        # add a step

        step_parameters = [float(time_string), int(rate_string), float(vol_string)]
        self.protocol_list.append(step_parameters)
        self.n_steps +=1


    def delete_step(self, d_step = None):
        if d_step is None:
            self.protocol_list.pop()
            d_step = -1
        elif d_step == 0:
            self.protocol_list.popleft()
        else:
            del self.protocol_list[d_step]

        self.n_steps -=1
        self._ui.tableWidget_steps.removeRow(dstep)

    def clear_protocol(self):
        pass


    def stop_pump(self):
        new_era.stop_pump(self.ser, self.pump)

    def shutDown(self, event):
        if self.isrunning:
            self.stop_pump()
        self.ser.close()
        self._app.quit()

    def run_protocol(self):
        '''
        This needs a thread
        '''
        tinit = 0.
        row_position = 0
        for step_paras in self.protocol_list:
            print(row_position)
            time_running = step_paras[0]-tinit
            tinit = step_paras[0]
            rate_running = step_paras[1]
            vol_running = step_paras[2]
            step_flag = Event()
            tmr = Protocol_thread(new_era, step_flag)
            tmr.set_dt(time_running)
            tmr.start()
            while not tmr.finished():
                continue
            self.set_rate(rate_running)
            self.set_vol(vol_running)
            self.run_pump()
            item_status = QtWidgets.QTableWidgetItem()
            item_status.setText("executed")
            self._ui.tableWidget_steps.setItem(row_position, 3, item_status)
            row_position +=1

        print("Protocol finished.")

#--------------------------------------This is the timer threading ----------------------------------
class Protocol_thread(Thread):
    '''
    The protocol thread
    '''
    def __init__(self, control, event):
        Thread.__init__(self)
        self.ne = control  # load new_era
        self.stopped = event

    def set_dt(self, dt):
        self.dt = dt

    def run(self):
        self.stopped.wait(self.dt)
        self.stopped.set()
        print(time.ctime())

    def finished(self):
        return self.stopped.is_set()
                # call the function of 



def main():
    ui = pump_ui()

if __name__=='__main__':
    main()
