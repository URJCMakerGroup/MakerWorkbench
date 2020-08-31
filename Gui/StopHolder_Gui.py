import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts import hallestop_holder
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _StopHolder_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(StopHolder_Dialog())

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Stop Holder',
            'Stop Holder')
        ToolTip =QtCore.QT_TRANSLATE_NOOP(
            'Stop Holder',
            'Creates Stop Holder with set parametres')
        return {
            'Pixmap': __dir__ + '/../icons/Stop_Holder.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class StopHolder_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Stop Holder options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Width ----
        self.Width_Label = QtWidgets.QLabel("Width:")
        self.Width_Value = QtWidgets.QDoubleSpinBox()
        self.Width_Value.setValue(21)
        self.Width_Value.setSuffix("mm")

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.Width_Label)
        width_layout.addWidget(self.Width_Value)

        # ---- Height ----
        self.Heigth_Label = QtWidgets.QLabel("Heigth:")
        self.Heigth_Value = QtWidgets.QDoubleSpinBox()
        self.Heigth_Value.setValue(31)
        self.Heigth_Value.setSuffix("mm")

        height_layout = QtWidgets.QHBoxLayout()
        height_layout.addWidget(self.Heigth_Label)
        height_layout.addWidget(self.Heigth_Value)

        # ---- Thikness ----
        self.Thickness_Label = QtWidgets.QLabel("Thickness:")
        self.Thickness_Value = QtWidgets.QDoubleSpinBox()
        self.Thickness_Value.setValue(4)
        self.Thickness_Value.setSuffix("mm")

        
        thickness_layout = QtWidgets.QHBoxLayout()
        thickness_layout.addWidget(self.Thickness_Label)
        thickness_layout.addWidget(self.Thickness_Value)

        # ---- Metric Bolt ----
        self.Bolt_Label = QtWidgets.QLabel("Metric Bolt")
        self.Bolt_ComboBox = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.Bolt_ComboBox.addItems(self.TextNutType)
        self.Bolt_ComboBox.setCurrentIndex(self.TextNutType.index('M3'))

        bolt_layout = QtWidgets.QHBoxLayout()
        bolt_layout.addWidget(self.Bolt_Label)
        bolt_layout.addWidget(self.Bolt_ComboBox)

        # ---- Rail ----
        self.Rail_Label = QtWidgets.QLabel("Rail Size:")
        self.Rail_ComboBox = QtWidgets.QComboBox()
        self.Rail_ComboBox.addItems(["10mm","20mm","30mm"])
        self.Rail_ComboBox.setCurrentIndex(0)

        rail_layout = QtWidgets.QHBoxLayout()
        rail_layout.addWidget(self.Rail_Label)
        rail_layout.addWidget(self.Rail_ComboBox)

        # ---- Reinforce ----
        self.Reinforce_Label = QtWidgets.QLabel("Reinforce:")
        self.Reinforce_ComboBox = QtWidgets.QComboBox()
        self.Reinforce_ComboBox.addItems(["No","Yes"])
        self.Reinforce_ComboBox.setCurrentIndex(1)

        reinforce_layout = QtWidgets.QHBoxLayout()
        reinforce_layout.addWidget(self.Reinforce_Label)
        reinforce_layout.addWidget(self.Reinforce_ComboBox)

        # ---- placement ----
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
        placement_layout_2 = QtWidgets.QVBoxLayout()
        placement_layout_3 = QtWidgets.QVBoxLayout()

        placement_layout.addLayout(placement_layout_1)
        placement_layout.addLayout(placement_layout_2)
        placement_layout.addLayout(placement_layout_3)

        placement_layout_1.addWidget(self.Label_position)
        placement_layout_2.addWidget(self.Label_pos_x)
        placement_layout_2.addWidget(self.Label_pos_y)
        placement_layout_2.addWidget(self.Label_pos_z)
        placement_layout_3.addWidget(self.pos_x)
        placement_layout_3.addWidget(self.pos_y)
        placement_layout_3.addWidget(self.pos_z)

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
        axes_layout_2 = QtWidgets.QVBoxLayout()
        axes_layout_3 = QtWidgets.QVBoxLayout()
        axes_layout_4 = QtWidgets.QVBoxLayout()
        axes_layout_5 = QtWidgets.QVBoxLayout()

        axes_layout.addLayout(axes_layout_1)
        axes_layout.addLayout(axes_layout_2)
        axes_layout.addLayout(axes_layout_3)
        axes_layout.addLayout(axes_layout_4)
        axes_layout.addLayout(axes_layout_5)

        axes_layout_1.addWidget(self.Label_axis)
        axes_layout_2.addWidget(self.Label_axis_d)
        axes_layout_2.addWidget(self.Label_axis_w)
        axes_layout_2.addWidget(self.Label_axis_h)
        axes_layout_3.addWidget(self.axis_d_x)
        axes_layout_3.addWidget(self.axis_w_x)
        axes_layout_3.addWidget(self.axis_h_x)
        axes_layout_4.addWidget(self.axis_d_y)
        axes_layout_4.addWidget(self.axis_w_y)
        axes_layout_4.addWidget(self.axis_h_y)
        axes_layout_5.addWidget(self.axis_d_z)
        axes_layout_5.addWidget(self.axis_w_z)
        axes_layout_5.addWidget(self.axis_h_z)

        # ---- Image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/StopHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(width_layout)
        main_layout.addLayout(height_layout)
        main_layout.addLayout(thickness_layout)
        main_layout.addLayout(bolt_layout)
        main_layout.addLayout(rail_layout)
        main_layout.addLayout(reinforce_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class StopHolder_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.StopHolder = StopHolder_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.StopHolder)
        self.form = [self.StopHolder.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)
    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Width = self.StopHolder.Width_Value.value()
        Heigth = self.StopHolder.Heigth_Value.value()
        Thick = self.StopHolder.Thickness_Value.value()
        Bolt_values = {0: 3,
                       1: 4,
                       2: 5,
                       3: 6}
        Bolt = Bolt_values[self.StopHolder.Bolt_ComboBox.currentIndex()]
        Rail_values = {0: 10,
                       1: 20,
                       2: 30}
        Rail = Rail_values[self.StopHolder.Rail_ComboBox.currentIndex()]
        Reinforce_values = {0: 0, #No
                            1: 1}#Yes
        Reinforce = Reinforce_values[self.StopHolder.Reinforce_ComboBox.currentIndex()]
        pos = FreeCAD.Vector(self.StopHolder.pos_x.value(), self.StopHolder.pos_y.value(), self.StopHolder.pos_z.value())
        axis_d = FreeCAD.Vector(self.StopHolder.axis_d_x.value(),self.StopHolder.axis_d_y.value(),self.StopHolder.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.StopHolder.axis_w_x.value(),self.StopHolder.axis_w_y.value(),self.StopHolder.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.StopHolder.axis_h_x.value(),self.StopHolder.axis_h_y.value(),self.StopHolder.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            hallestop_holder(stp_w = Width,
                                stp_h = Heigth,
                                base_thick = Thick,
                                sup_thick = Thick,
                                bolt_base_d = Bolt, #metric of the bolt 
                                bolt_sup_d = Bolt, #metric of the bolt
                                bolt_sup_sep = 17.,  # fixed value
                                alu_rail_l = Rail,
                                stp_rail_l = Rail,
                                xtr_bolt_head = 3,
                                xtr_bolt_head_d = 0,
                                reinforce = Reinforce,
                                base_min_dist = 1,
                                fc_perp_ax = axis_h,#VZ,
                                fc_lin_ax = axis_d, #VX,
                                pos = pos,
                                wfco=1,
                                name = 'stop_holder')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.SendMsgToActiveView("ViewFit")
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
            set_place(self.StopHolder, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.StopHolder,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Stop_Holder',_StopHolder_Cmd())
