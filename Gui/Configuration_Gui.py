from PySide2 import QtCore, QtGui, QtWidgets

import os
import FreeCAD
import FreeCADGui
import sys
import logging

from configuration import read_configuration_file, change_configuration_file, default_configuration_file

from kcomp import TOL, STOL
from kparts import MTOL, MLTOL

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class configuration_cmd():
    def Activated(self):
        global TOL, STOL, MTOL, MLTOL
        if os.path.isfile(__dir__+"/../configuration.txt"):
            print("Hay archivo")
            config = read_configuration_file()
            TOL = config["Tolerance"]
            STOL = config["Smaller Tolerance"]
            MTOL = config["Metric Tolerance"]
            MLTOL = config["Metric lower Tolerance"]
        else:
            print("No hay archivo")
        window = Window()
        window.show()
        window.exec_()

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Configuration file',
            'Configuration file')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Manage the diferents parameters')
        return {
            # 'Pixmap': __dir__ + '',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None


class Window(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 150, 150)
        self.setWindowTitle("Maker's configuration")
        self.gui()  # llamamos a la interface gráfica

    def gui(self):
        main_layout = QtWidgets.QVBoxLayout()
        setting_layout_1 = QtWidgets.QHBoxLayout()
        setting_layout_2 = QtWidgets.QHBoxLayout()
        setting_layout_3 = QtWidgets.QHBoxLayout()
        setting_layout_4 = QtWidgets.QHBoxLayout()
        check_layout = QtWidgets.QHBoxLayout()
        anotation_layout = QtWidgets.QVBoxLayout()
        btns_layout = QtWidgets.QHBoxLayout()

        main_layout.addLayout(setting_layout_1)
        main_layout.addLayout(setting_layout_2)
        main_layout.addLayout(setting_layout_3)
        main_layout.addLayout(setting_layout_4)
        main_layout.addLayout(check_layout)
        main_layout.addLayout(anotation_layout)
        main_layout.addLayout(btns_layout)

        self.setLayout(main_layout)

        # settings
        tolerance_label = QtWidgets.QLabel("Tolerance: *")
        self.tolerance_value = QtWidgets.QLineEdit()
        self.tolerance_value.setText(str(TOL))
        self.tolerance_value.textChanged.connect(self.update_text)
        self.tolerance_value.textChanged.connect(self.has_change)
        self.tolerance_value.setFixedWidth(100)
        small_tolerance_label = QtWidgets.QLabel("Small tolerance:")
        self.small_tolerance_value = QtWidgets.QLineEdit()
        self.small_tolerance_value.setText(str(STOL))
        self.small_tolerance_value.textChanged.connect(self.has_change)
        self.small_tolerance_value.setFixedWidth(100)
        metric_tolerance_label = QtWidgets.QLabel("Metric tolerance:")
        self.metric_tolerance_value = QtWidgets.QLineEdit()
        self.metric_tolerance_value.setText(str(MTOL))
        self.metric_tolerance_value.textChanged.connect(self.has_change)
        self.metric_tolerance_value.setFixedWidth(100)
        metric_lower_tolerance_label = QtWidgets.QLabel("Metric lower Tolerance:")
        self.metric_lower_tolerance_value = QtWidgets.QLineEdit()
        self.metric_lower_tolerance_value.setText(str(MLTOL))
        self.metric_lower_tolerance_value.textChanged.connect(self.has_change)
        self.metric_lower_tolerance_value.setFixedWidth(100)

        # to layout
        setting_layout_1.addWidget(tolerance_label)
        setting_layout_1.addWidget(self.tolerance_value)
        setting_layout_2.addWidget(small_tolerance_label)
        setting_layout_2.addWidget(self.small_tolerance_value)
        setting_layout_3.addWidget(metric_tolerance_label)
        setting_layout_3.addWidget(self.metric_tolerance_value)
        setting_layout_4.addWidget(metric_lower_tolerance_label)
        setting_layout_4.addWidget(self.metric_lower_tolerance_value)

        # checked
        self.auto_checkbox = QtWidgets.QCheckBox("Auto update", self)
        self.auto_checkbox.setChecked(True)

        # to layout
        check_layout.addWidget(self.auto_checkbox)

        # anotation"Auto update
        annotation_label_1 = QtWidgets.QLabel("* The tolerance value will change the followings values: small tolerance,")
        annotation_label_2 = QtWidgets.QLabel("metric tolerance, metric lower tolerance. If you don't want to update all,")
        annotation_label_3 = QtWidgets.QLabel("please, uncheck the Auto update box.")

        # to layout
        anotation_layout.addWidget(annotation_label_1)
        anotation_layout.addWidget(annotation_label_2)
        anotation_layout.addWidget(annotation_label_3)

        # btns
        self.btn_change = QtWidgets.QPushButton("Save Change", self)
        self.btn_change.clicked.connect(self.change)
        self.btn_change.setEnabled(False)
        self.btn_default = QtWidgets.QPushButton("Default configuration", self)
        self.btn_default.clicked.connect(self.default)
        self.btn_cancel = QtWidgets.QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.cancel)
        # to layout
        btns_layout.addWidget(self.btn_change)
        btns_layout.addWidget(self.btn_default)
        btns_layout.addWidget(self.btn_cancel)

    def has_change(self):
        """
        Enable the save change button when the user make a change
        """
        if not self.btn_change.isEnabled():
            self.btn_change.setEnabled(True)

    def update_text(self):
        # TODO: update text
        global TOL
        if self.auto_checkbox.isChecked():
            __tol = float(self.tolerance_value.text())
            __stol = float(self.small_tolerance_value.text())
            __mtol = float(self.metric_tolerance_value.text())
            __mltol = float(self.metric_lower_tolerance_value.text())
            if __tol != 0:
                self.small_tolerance_value.setText(str(__tol / ((1 / __stol) * float(TOL))))
                self.metric_tolerance_value.setText(str(__tol))
                self.metric_lower_tolerance_value.setText(str(round(__tol - (float(TOL)-__mltol), 4)))
                TOL = __tol

    def change(self):
        # TODO: button change pressed
        __tol = self.tolerance_value.text() if self.tolerance_value.text() != TOL else None
        __stol = self.small_tolerance_value.text() if self.small_tolerance_value.text() != STOL else None
        __mtol = self.metric_tolerance_value.text() if self.metric_tolerance_value.text() != MTOL else None
        __mltol = self.metric_lower_tolerance_value.text() if self.metric_lower_tolerance_value.text() != MLTOL else None
        change_configuration_file(_tol=__tol, _stol=__stol, _mtol=__mtol, _mltol=__mltol)
        message = QtWidgets.QMessageBox()
        message.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message.setWindowTitle('Configuration saved')
        message.setText("Configuration saved")
        message.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message.setDefaultButton(QtWidgets.QMessageBox.Ok)
        message.exec_()

    def cancel(self):
        # TODO: button cancel pressed
        self.close()

    def default(self):
        # TODO: button default pressed
        message = QtWidgets.QMessageBox()
        message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message.setWindowTitle('Caution!')
        message.setText("The actual configuration will be lost. \nAre you sure?")
        message.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        message.setDefaultButton(QtWidgets.QMessageBox.Ok)
        res = message.exec_()
        if res == QtWidgets.QMessageBox.Ok:
            default_configuration_file()
            config = read_configuration_file()
            TOL = config["Tolerance"]
            STOL = config["Smaller Tolerance"]
            MTOL = config["Metric Tolerance"]
            MLTOL = config["Metric lower Tolerance"]
            self.tolerance_value.setText(str(TOL))
            self.small_tolerance_value.setText(str(STOL))
            self.metric_tolerance_value.setText(str(MTOL))
            self.metric_lower_tolerance_value.setText(str(MLTOL))
            self.btn_change.setEnabled(False)
        else:
            pass


# Command
FreeCADGui.addCommand('Configuration', configuration_cmd())
