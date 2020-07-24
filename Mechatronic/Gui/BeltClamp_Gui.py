import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from beltcl import BeltClamp, DoubleBeltClamp 
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _BeltClamp_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(BeltClamp_Dialog())

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Belt clamp')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a belt clamp')
        return {
            'Pixmap': __dir__ + '/../icons/Double_Belt_Clamp_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class BeltClamp_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Belt Clamp options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Type ----
        self.Type_Label = QtWidgets.QLabel("Type:")   

        self.Type_ComboBox = QtWidgets.QComboBox()
        self.TextType = ["Simple","Double"]
        self.Type_ComboBox.addItems(self.TextType)
        self.Type_ComboBox.setCurrentIndex(0)

        Type_layout = QtWidgets.QHBoxLayout()
        Type_layout.addWidget(self.Type_Label)
        Type_layout.addWidget(self.Type_ComboBox)

        # ---- Length ----
        self.Length_Label = QtWidgets.QLabel("Length:")
        self.Length_Value = QtWidgets.QDoubleSpinBox()
        self.Length_Value.setValue(42)
        self.Length_Value.setSuffix(' mm')
        self.Length_Value.setMinimum(42)

        Length_layout = QtWidgets.QHBoxLayout()
        Length_layout.addWidget(self.Length_Label)
        Length_layout.addWidget(self.Length_Value)

        # ---- Width ----
        self.Width_Label = QtWidgets.QLabel("Width:")
        self.Width_Value = QtWidgets.QDoubleSpinBox()
        self.Width_Value.setValue(10.8)
        self.Width_Value.setSuffix(' mm')
        self.Width_Value.setMinimum(10.8)

        Width_layout = QtWidgets.QHBoxLayout()
        Width_layout.addWidget(self.Width_Label)
        Width_layout.addWidget(self.Width_Value)

        # ---- Nut Type ----
        self.nut_hole_Label = QtWidgets.QLabel("Nut Type:")   
        self.ComboBox_Nut_Hole = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.ComboBox_Nut_Hole.addItems(self.TextNutType)
        self.ComboBox_Nut_Hole.setCurrentIndex(self.TextNutType.index('M3'))

        Nut_layout = QtWidgets.QHBoxLayout()
        Nut_layout.addWidget(self.nut_hole_Label)
        Nut_layout.addWidget(self.ComboBox_Nut_Hole)

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
        self.pos_x.setAlignment(PySide2.QtCore.Qt.AlignCenter)
        self.pos_y.setAlignment(PySide2.QtCore.Qt.AlignCenter)
        self.pos_z.setAlignment(PySide2.QtCore.Qt.AlignCenter)

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

        # ---- Image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/BeltClamp.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(Type_layout)
        main_layout.addLayout(Length_layout)
        main_layout.addLayout(Width_layout)
        main_layout.addLayout(Nut_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class BeltClamp_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.BeltClamp = BeltClamp_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.BeltClamp)
        self.form = [self.BeltClamp.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)
    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Type = self.BeltClamp.Type_ComboBox.currentIndex()
        Length = self.BeltClamp.Length_Value.value()
        Width = self.BeltClamp.Width_Value.value()
        IndexNut = {0 : 3,
                    1 : 4,
                    2 : 5,
                    3 : 6}
        nut_hole = IndexNut[self.BeltClamp.ComboBox_Nut_Hole.currentIndex()]
        pos = FreeCAD.Vector(self.BeltClamp.pos_x.value(), self.BeltClamp.pos_y.value(), self.BeltClamp.pos_z.value())
        axis_d = FreeCAD.Vector(self.BeltClamp.axis_d_x.value(),self.BeltClamp.axis_d_y.value(),self.BeltClamp.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.BeltClamp.axis_w_x.value(),self.BeltClamp.axis_w_y.value(),self.BeltClamp.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.BeltClamp.axis_h_x.value(),self.BeltClamp.axis_h_y.value(),self.BeltClamp.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if Type == 0:
                BeltClamp(fc_fro_ax = axis_d,#VX,
                          fc_top_ax = axis_h,#VZ,
                          base_h = 2,
                          base_l = Length,
                          base_w = Width,
                          bolt_d = nut_hole,
                          bolt_csunk = 0,
                          ref = 1,
                          pos = pos,
                          extra=1,
                          wfco = 1,
                          intol = 0,
                          name = 'belt_clamp' )
            elif Type == 1:
                DoubleBeltClamp(axis_h = axis_h,#VZ,
                                axis_d = axis_d,#VX,
                                axis_w = axis_w,#VY,
                                base_h = 2,
                                base_l = Length,
                                base_w = Width,
                                bolt_d = nut_hole,
                                bolt_csunk = 0,
                                ref = 1,
                                pos = pos,
                                extra=1,
                                wfco = 1,
                                intol = 0,
                                    name = 'double_belt_clamp' )
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
            set_place(self.BeltClamp, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.BeltClamp,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Belt_Clamp',_BeltClamp_Cmd())