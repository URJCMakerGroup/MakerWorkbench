import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from comp_optic import Lb1cPlate, Lb2cPlate, lcp01m_plate
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp_optic

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _Plate_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(Plate_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Plate',
            'Plate')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/../icons/Plate_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class Plate_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Plate options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Plate ----
        self.Label_plate = QtWidgets.QLabel('Dictionary:')
        self.type = QtWidgets.QComboBox()
        self.type.addItems(["Lb1cm_Plate","Lb2c_Plate","Lcp01m_plate"])
        self.type.setCurrentIndex(0)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Label_plate)
        type_layout.addWidget(self.type)

        # ---- Placement ----
        self.Label_position = QtWidgets.QLabel("Placement ")
        self.Label_position.setAlignment(QtCore.Qt.AlignTop)
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

        # ---- Axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
        self.Label_axis.setAlignment(QtCore.Qt.AlignTop)
        self.Label_axis_d = QtWidgets.QLabel("d:")
        self.Label_axis_w = QtWidgets.QLabel("w:")
        self.Label_axis_h = QtWidgets.QLabel("h:")
        self.axis_d_x = QtWidgets.QDoubleSpinBox()
        self.axis_d_y = QtWidgets.QDoubleSpinBox()
        self.axis_d_z = QtWidgets.QDoubleSpinBox()
        self.axis_d_x.setMinimum(-1)
        self.axis_d_x.setMaximum(1)
        self.axis_d_y.setMinimum(-1)
        self.axis_d_y.setMaximum(1)
        self.axis_d_z.setMinimum(-1)
        self.axis_d_z.setMaximum(1)
        self.axis_d_x.setValue(1)
        self.axis_d_y.setValue(0)
        self.axis_d_z.setValue(0)
        self.axis_w_x = QtWidgets.QDoubleSpinBox()
        self.axis_w_y = QtWidgets.QDoubleSpinBox()
        self.axis_w_z = QtWidgets.QDoubleSpinBox()
        self.axis_w_x.setMinimum(-1)
        self.axis_w_x.setMaximum(1)
        self.axis_w_y.setMinimum(-1)
        self.axis_w_y.setMaximum(1)
        self.axis_w_z.setMinimum(-1)
        self.axis_w_z.setMaximum(1)
        self.axis_w_x.setValue(0)
        self.axis_w_y.setValue(1)
        self.axis_w_z.setValue(0)
        self.axis_h_x = QtWidgets.QDoubleSpinBox()
        self.axis_h_y = QtWidgets.QDoubleSpinBox()
        self.axis_h_z = QtWidgets.QDoubleSpinBox()
        self.axis_h_x.setMinimum(-1)
        self.axis_h_x.setMaximum(1)
        self.axis_h_y.setMinimum(-1)
        self.axis_h_y.setMaximum(1)
        self.axis_h_z.setMinimum(-1)
        self.axis_h_z.setMaximum(1)
        self.axis_h_x.setValue(0)
        self.axis_h_y.setValue(0)
        self.axis_h_z.setValue(1)

        axes_layout = QtWidgets.QHBoxLayout()

        axes_layout_1 = QtWidgets.QVBoxLayout()
        axes_layout_1.addWidget(self.Label_axis)

        axes_layout_2 = QtWidgets.QVBoxLayout()
        axes_layout_2.addWidget(self.Label_axis_d)
        axes_layout_2.addWidget(self.Label_axis_w)
        axes_layout_2.addWidget(self.Label_axis_h)

        axes_layout_3 = QtWidgets.QVBoxLayout()
        axes_layout_3.addWidget(self.axis_d_x)
        axes_layout_3.addWidget(self.axis_w_x)
        axes_layout_3.addWidget(self.axis_h_x)

        axes_layout_4 = QtWidgets.QVBoxLayout()
        axes_layout_4.addWidget(self.axis_d_y)
        axes_layout_4.addWidget(self.axis_w_y)
        axes_layout_4.addWidget(self.axis_h_y)

        axes_layout_5 = QtWidgets.QVBoxLayout()
        axes_layout_5.addWidget(self.axis_d_z)
        axes_layout_5.addWidget(self.axis_w_z)
        axes_layout_5.addWidget(self.axis_h_z)

        axes_layout.addLayout(axes_layout_1)
        axes_layout.addLayout(axes_layout_2)
        axes_layout.addLayout(axes_layout_3)
        axes_layout.addLayout(axes_layout_4)
        axes_layout.addLayout(axes_layout_5)

        # ---- row 7: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/Plate.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class Plate_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.Plate = Plate_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.Plate)
        self.form = [self.Plate.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        pos = FreeCAD.Vector(self.Plate.pos_x.value(), self.Plate.pos_y.value(), self.Plate.pos_z.value())
        axis_d = FreeCAD.Vector(self.Plate.axis_d_x.value(),self.Plate.axis_d_y.value(),self.Plate.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.Plate.axis_w_x.value(),self.Plate.axis_w_y.value(),self.Plate.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.Plate.axis_h_x.value(),self.Plate.axis_h_y.value(),self.Plate.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if self.Plate.type.currentIndex() == 0:
                Lb1cPlate(kcomp_optic.LB1CM_PLATE,
                                    fc_axis_h = axis_h ,#VZ,
                                    fc_axis_l = axis_d ,#VX,
                                    ref_in = 1,
                                    pos = pos,
                                    name = 'lb1c_plate')

            if self.Plate.type.currentIndex() == 1:
                Lb2cPlate(fc_axis_h = axis_h ,#VZ,
                                    fc_axis_l = axis_d ,#VX,
                                    cl=1, cw=1, ch=0,
                                    pos = pos,
                                    name = 'lb2c_plate')

            if self.Plate.type.currentIndex() == 2:
                lcp01m_plate(d_lcp01m_plate = kcomp_optic.LCP01M_PLATE,
                                        fc_axis_h = axis_h ,#VZ,
                                        fc_axis_m = axis_d ,#VX,
                                        fc_axis_p = axis_w ,#V0,
                                        cm=1, cp=1, ch=1,
                                        pos = pos,
                                        wfco= 1,
                                        name = 'LCP01M_PLATE')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

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
            set_place(self.Plate, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.Plate,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Plate',_Plate_Cmd())