from PySide import QtCore, QtWidgets
import os
import FreeCAD
import FreeCADGui

from print_export_fun import print_export

__dir__ = os.path.dirname(__file__)


class _ChangePosExport_Cmd:
    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) != 0:
            obj_select = selection[0]  # .Name
            print_export(obj_select)
        else:
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            message.setWindowTitle('Error')
            message.setText("Please, select a object")
            message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            message.setDefaultButton(QtWidgets.QMessageBox.Ok)
            message.exec_()

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Change Pos and Export',
            'Change Pos and Export')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Object selected changes to print position and it is exported in .stl')
        return {
            'Pixmap': __dir__ + '/../Resources/icons/MakerWorkbench_ChangePosExport_Cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 


# Command
FreeCADGui.addCommand('ChangePosExport', _ChangePosExport_Cmd())
