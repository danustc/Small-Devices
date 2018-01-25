import sys
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import pump_design
from functools import partial

class pump_ui(object):

    def __init__(self, control):
        self._control = control
        self._app = QtWidgets.QApplication(sys.argv)
        self._window = QtWidgets.QWidget()
        self._window.closeEvent = self.shutDown

        self._ui = pump_design.UI_form()
        self._ui.setupUi(self._window)

        # set the default value
        self.set_default()

        # Following are the definition of button and lineEdit functions
        self._ui.pushButton_godefault.click.connect(self.go_default)
        self._ui.lineEdit_rate.returnPressed(partial(self.setrate))
        self._ui.lineEdit_volume.returnPressed(partial(self.setvolume))

    def go_default(self):
        self._control.setvol(self.default_volume)
        self._control.setrate(self.default_rate)

    def set_default(self, rate = None, vol = None, direct = None):
        if rate is None:
            rate = float(self._ui.lineEdit_rate.text())
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

    def set_rate(self, rate):
