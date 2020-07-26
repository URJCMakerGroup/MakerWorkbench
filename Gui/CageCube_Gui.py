import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from comp_optic import f_cagecube, f_cagecubehalf 
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp_optic

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _CageCube_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(CageCube_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'CageCube',
            'CageCube')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/../icons/CageCube_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class CageCube_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("CageCube options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Type ----
        self.Label_Type = QtWidgets.QLabel("Type ")
        self.Type = QtWidgets.QComboBox()
        self.Type.addItems(["CAGE_CUBE_60","CAGE_CUBE_HALF_60"])
        self.Type.setCurrentIndex(0)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Label_Type)
        type_layout.addWidget(self.Type)

        # ---- Placement ----
        self.Label_position = QtWidgets.QLabel("Placement ")
        self.Label_pos_x = QtWidgets.QLabel("x:")
        self.Label_pos_y = QtWidgets.QLabel("y:")
        self.Label_pos_z = QtWidgets.QLabel("z:")
        self.pos_x = QtWidgets.QDoubleSpinBox()
        self.pos_y = QtWidgets.QDoubleSpinBox()
        self.pos_z = QtWidgets.QDoubleSpinBox()
        self.pos_x.setValue(0.000)
        self.pos_y.setValue(0.000)
        self.pos_z.setValue(0.000)
        self.pos_x.setDecimals(3)
        self.pos_y.setDecimals(3)
        self.pos_z.setDecimals(3)
        self.pos_x.setRange(minnum, maxnum)
        self.pos_y.setRange(minnum, maxnum)
        self.pos_z.setRange(minnum, maxnum)

        placement_layout = QtWidgets.QHBoxLayout()

        placement_layout_1 = QtWidgets.QVBoxLayout()
        placement_layout_1.addWidget(self.Label_position)
        placement_layout_2 = QtWidgets.QVBoxLayout()
        placement_layout_2.addWidget(self.Label_pos_x)
        placement_layout_2.addWidget(self.Label_pos_y)
        placement_layout_2.addWidget(self.Label_pos_z)
        placement_layout_3 = QtWidgets.QVBoxLayout()
        placement_layout_3.addWidget(self.pos_x)
        placement_layout_3.addWidget(self.pos_y)
        placement_layout_3.addWidget(self.pos_z)

        placement_layout.addLayout(placement_layout_1)
        placement_layout.addLayout(placement_layout_2)
        placement_layout.addLayout(placement_layout_3)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(placement_layout)

class CageCube_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.CageCube = CageCube_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.CageCube)
        self.form = [self.CageCube.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        # if fc_isperp(axis_d,axis_w) == 1:
        if self.CageCube.Type.currentIndex() == 0:
            f_cagecube(kcomp_optic.CAGE_CUBE_60,
                        axis_thru_rods = 'x',
                        axis_thru_hole = 'y',
                        name = 'cagecube',
                        toprint_tol = 0)
        if self.CageCube.Type.currentIndex() == 1:
            f_cagecubehalf(kcomp_optic.CAGE_CUBE_HALF_60,
                            axis_1 = 'x',
                            axis_2 = 'y',
                            name = 'cagecubehalf')

        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.Control.closeDialog() #close the dialog
        FreeCADGui.SendMsgToActiveView("ViewFit")
        # else:
            # axis_message()

    def reject(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        FreeCADGui.Control.closeDialog()
        
    def position(self,info):
        pos = info["Position"]
        try: 
            down = info["State"]
            if down == "DOWN" and self.placement==True:
                self.placement=False
            elif down == "DOWN"and self.placement==False:
                self.placement=True
            else:pass
        except Exception: None
        
        if self.placement == True:
            set_place(self.CageCube, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.CageCube,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('CageCube',_CageCube_Cmd())