import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui

from print_export_fun import print_export

__dir__ = os.path.dirname(__file__)

class _ChangePosExport_Cmd:
    def Activated(self):
        objSelect = FreeCADGui.Selection.getSelection()[0]#.Name
        print_export(objSelect)
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Change Pos and Export',
            'Change Pos and Export')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Object selected changes to print position and it is exported in .stl')
        return {
            'Pixmap': __dir__ + '/../icons/Print_Export_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

# Command
FreeCADGui.addCommand('ChangePosExport',_ChangePosExport_Cmd())