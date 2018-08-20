#!/usr/bin/python

from PyQt5 import QtWidgets,QtCore
from functools import partial
import parallax_design
import wheel

class UI(object):
    def __init__(self, port = 'COM10'): # substitute with your own COM port
        # ---------- Initialize a control and a UI, Generate the UI frame.
        self._control = wheel.control(port)
        self._ui.parallax_design.Ui_Form()
        self._app = QtWidgets.QApplication(sys.argv)
        self._window = QtWidgets.QWidget()
        self._window.closeEvent = self.shutDown
        # --------- Specify UI functions ----------
        self._ui.radioButton_488OD0.toggled.connect(partial(self.set_488, 0))
        self._ui.radioButton_488OD1.toggled.connect(partial(self.set_488, 1))
        self._ui.radioButton_488OD2.toggled.connect(partial(self.set_488, 2))
        self._ui.radioButton_488OD3.toggled.connect(partial(self.set_488, 3))

        self._ui.radioButton_561OD0.toggled.connect(partial(self.set_561, 0))
        self._ui.radioButton_561OD1.toggled.connect(partial(self.set_561, 1))
        self._ui.radioButton_561OD2.toggled.connect(partial(self.set_561, 2))
        self._ui.radioButton_561OD3.toggled.connect(partial(self.set_561, 3))

    def set_488(self, n_OD):
        print("Optical density:", 0)
        self._control.set_OD(488, n_OD)


    def set_561(self, n_OD):
        print("Optical density:", 0)
        self._control.set_OD(561, n_OD)



def main():
    ui = UI() # generate a UI

if __name__ == '__main__':
    main()
