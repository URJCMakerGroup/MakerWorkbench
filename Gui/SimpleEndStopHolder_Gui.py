import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts_new import SimpleEndstopHolder
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _SimpleEndStopHolder_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(SimpleEndStopHolder_Dialog())
    
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Simple End Stop Holder',
            'Simple End Stop Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Simple End Stop Holder',
            'Create a Simple End Stop Holder')
        return {
            'Pixmap': __dir__ + '/../icons/SimpleEndStopHolder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
class SimpleEndStopHolder_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Simple End Stop Holder options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Type ----
        self.Type_Label = QtWidgets.QLabel("Type:")
        self.Type_ComboBox = QtWidgets.QComboBox()
        Type_text = ["A","B","D3V"]
        self.Type_ComboBox.addItems(Type_text)
        self.Type_ComboBox.setCurrentIndex(0)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Type_Label)
        type_layout.addWidget(self.Type_ComboBox)

        # ---- Rail ---- 
        self.Rail_Label = QtWidgets.QLabel("Rail Length:")
        self.Rail_Value = QtWidgets.QDoubleSpinBox()
        self.Rail_Value.setValue(15)
        self.Rail_Value.setSuffix(' mm')

        rail_layout = QtWidgets.QHBoxLayout()
        rail_layout.addWidget(self.Rail_Label)
        rail_layout.addWidget(self.Rail_Value)

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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['1','2','3','4','5'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['1','2','3','4'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['1','2'])
        self.pos_h.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_h)
        placement_layout_3.addWidget(self.pos_h)

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

        # ---- Image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/SimpleEndstopHolder.png">here</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(rail_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class SimpleEndStopHolder_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.SimpleEndStopHolder = SimpleEndStopHolder_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.SimpleEndStopHolder)
        self.form = [self.SimpleEndStopHolder.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Type_values = {0:kcomp.ENDSTOP_A, 1:kcomp.ENDSTOP_B, 2:kcomp.ENDSTOP_D3V}
        Type = Type_values[self.SimpleEndStopHolder.Type_ComboBox.currentIndex()]
        Rail_L = self.SimpleEndStopHolder.Rail_Value.value()
        pos = FreeCAD.Vector(self.SimpleEndStopHolder.pos_x.value(), self.SimpleEndStopHolder.pos_y.value(), self.SimpleEndStopHolder.pos_z.value())
        positions_d = [1,2,3,4,5]
        positions_w = [1,2,3,4]
        positions_h = [1,2]
        pos_d = positions_d[self.SimpleEndStopHolder.pos_d.currentIndex()]
        pos_w = positions_w[self.SimpleEndStopHolder.pos_w.currentIndex()]
        pos_h = positions_h[self.SimpleEndStopHolder.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.SimpleEndStopHolder.axis_d_x.value(),self.SimpleEndStopHolder.axis_d_y.value(),self.SimpleEndStopHolder.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.SimpleEndStopHolder.axis_w_x.value(),self.SimpleEndStopHolder.axis_w_y.value(),self.SimpleEndStopHolder.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.SimpleEndStopHolder.axis_h_x.value(),self.SimpleEndStopHolder.axis_h_y.value(),self.SimpleEndStopHolder.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            SimpleEndstopHolder(d_endstop = Type,
                                rail_l = Rail_L,
                                base_h = 5.,
                                h = 0,
                                holder_out = 2.,
                                #csunk = 1,
                                mbolt_d = 3.,
                                endstop_nut_dist = 0.,
                                min_d = 0,
                                axis_d = axis_d,
                                axis_w = axis_w,
                                axis_h = axis_h,
                                pos_d = pos_d,
                                pos_w = pos_w,
                                pos_h = pos_h,
                                pos = pos,
                                wfco = 1,
                                name = 'simple_endstop_holder')
            
            FreeCADGui.activeDocument().activeView().viewAxonometric() #Axonometric view
            FreeCADGui.SendMsgToActiveView("ViewFit") #Fit the view to the object
            FreeCADGui.Control.closeDialog() #close the dialog

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
            set_place(self.SimpleEndStopHolder, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3),round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.SimpleEndStopHolder,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Simple_Endstop_Holder',_SimpleEndStopHolder_Cmd())