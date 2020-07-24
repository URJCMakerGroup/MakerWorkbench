import PySide2
from PySide2 import QtWidgets, QtCore
import os
import FreeCAD
import FreeCADGui
from fcfun import V0, VX, VY, VZ

import kcomp

__dir__ = os.path.dirname(__file__)

class _testCmD:
    """
    Test class
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("TEST")
        panel_test = test_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_test) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Test',
            'Test')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class test_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        # layout = QtWidgets.QGridLayout(self.form)
    
    def accept(self):
        import comps_new
        # TODO check Tensioner in NuevaClase. Mirar posiciones para ver que pasa.

        comps_new.AluProf(depth = 50.,
                          aluprof_dict = kcomp.ALU_PROF[20],
                          xtr_d=0, xtr_nd=0,
                          axis_d = VX, 
                          axis_w = VY, 
                          axis_h = V0,
                          pos_d = 0, pos_w = 0, pos_h = 0,
                          pos = V0,
                          model_type = 1, # dimensional model
                          name = 'aluprof_'+str(20))
        # tensioner_clss_new.TensionerHolder(aluprof_w = 20., belt_pos_h = 20., tens_h=10, tens_w=10, tens_d_inside=25)
        # tensioner_clss.IdlerTensionerSet()
        # tensioner_clss_new.IdlerTensionerSet()
        # print("_____________________________")
        # print("Old")
        # tensioner_clss.TensionerSet()
        # print("_____________________________")
        # print("New")
        # tensioner_clss_new.TensionerSet()

        # NuevaClase.placa_perforada( 10, 10, 5, 2, name = 'placa perforada')

        # NuevaClase.placa_tornillos( 10, 10, 5, 1, name = 'placa tornillos')

        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.Control.closeDialog() #close the dialog
        FreeCADGui.SendMsgToActiveView("ViewFit")

# Command
FreeCADGui.addCommand('test', _testCmD())