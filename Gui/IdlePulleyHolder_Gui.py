import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts import IdlePulleyHolder 
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _IdlePulleyHolder_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(IdlePulleyHolder_Dialog())
    
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Idle Pulley Holder',
            'Idle Pulley Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Idle Pulley Holder',
            'Create an Idle Pulley Holder')
        return {
            'Pixmap': __dir__ + '/../icons/IdlePulleyHolder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class IdlePulleyHolder_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Idle Pulley Holder options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Aluprof ----
        self.ALuprof_Label = QtWidgets.QLabel("Aluminium profile:")
        self.Aluprof_ComboBox = QtWidgets.QComboBox()
        self.Aluprof_Str = ["20mm","30mm"]
        self.Aluprof_ComboBox.addItems(self.Aluprof_Str)
        self.Aluprof_ComboBox.setCurrentIndex(0)

        aluprof_layout = QtWidgets.QHBoxLayout()
        aluprof_layout.addWidget(self.ALuprof_Label)
        aluprof_layout.addWidget(self.Aluprof_ComboBox)


        # ---- Nut Bolt ----
        self.NutBolt_Label = QtWidgets.QLabel("Nut bolt:")
        self.NutBolt_Str = ["2.5","3","4","5","6"]
        self.NutBolt_ComboBox = QtWidgets.QComboBox()
        self.NutBolt_ComboBox.addItems(self.NutBolt_Str)
        self.NutBolt_ComboBox.setCurrentIndex(3)

        bolt_layout = QtWidgets.QHBoxLayout()
        bolt_layout.addWidget(self.NutBolt_Label)
        bolt_layout.addWidget(self.NutBolt_ComboBox)
        
        # ---- High to profile ----
        self.HighToProfile_Label = QtWidgets.QLabel("High to profile:")
        self.HighToProfile_Value = QtWidgets.QDoubleSpinBox()
        self.HighToProfile_Value.setValue(40)
        self.HighToProfile_Value.setSuffix(' mm')

        high_layout = QtWidgets.QHBoxLayout()
        high_layout.addWidget(self.HighToProfile_Label)
        high_layout.addWidget(self.HighToProfile_Value)

        # ---- End Stop Side ----
        self.EndSide_Label = QtWidgets.QLabel("End Stop Side:")
        self.EndSide_ComboBox = QtWidgets.QComboBox()
        self.EndSide_Str = ["1","0","-1"]
        self.EndSide_ComboBox.addItems(self.EndSide_Str)
        self.EndSide_ComboBox.setCurrentIndex(1)

        EndSide_layout = QtWidgets.QHBoxLayout()
        EndSide_layout.addWidget(self.EndSide_Label)
        EndSide_layout.addWidget(self.EndSide_ComboBox)

        # ---- End Stop High ----
        self.EndStopHigh_Label = QtWidgets.QLabel("End Stop Pos:")
        self.EndStopHigh_Value = QtWidgets.QDoubleSpinBox()
        self.EndStopHigh_Value.setValue(0)
        self.EndStopHigh_Value.setSuffix(' mm')

        EndHigh_layout = QtWidgets.QHBoxLayout()
        EndHigh_layout.addWidget(self.EndStopHigh_Label)
        EndHigh_layout.addWidget(self.EndStopHigh_Value)

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


        main_layout.addLayout(aluprof_layout)
        main_layout.addLayout(bolt_layout)
        main_layout.addLayout(high_layout)
        main_layout.addLayout(EndSide_layout)
        main_layout.addLayout(EndHigh_layout)
        main_layout.addLayout(placement_layout)

class IdlePulleyHolder_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.IdlePulleyHolder = IdlePulleyHolder_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.IdlePulleyHolder)
        self.form = [self.IdlePulleyHolder.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        self.Aluprof_values = {0: 20, 1:30}
        self.NutBolt_values = {0:2.5, 1:3, 2:4, 3:5, 4:6}
        self.EndSide_values = {0:1, 1:0, 2:-1}
        Aluprof = self.Aluprof_values[self.IdlePulleyHolder.Aluprof_ComboBox.currentIndex()]
        NutBolt = self.NutBolt_values[self.IdlePulleyHolder.NutBolt_ComboBox.currentIndex()]
        High = self.IdlePulleyHolder.HighToProfile_Value.value()
        EndSide = self.EndSide_values[self.IdlePulleyHolder.EndSide_ComboBox.currentIndex()]
        EndHigh = self.IdlePulleyHolder.EndStopHigh_Value.value()
        pos = FreeCAD.Vector(self.IdlePulleyHolder.pos_x.value(), self.IdlePulleyHolder.pos_y.value(), self.IdlePulleyHolder.pos_z.value())

        IdlePulleyHolder( profile_size= Aluprof, #20.,#
                                pulleybolt_d=3.,
                                holdbolt_d = NutBolt, #5,#
                                above_h = High, #40,#
                                mindepth = 0,
                                attach_dir = '-y',
                                endstop_side = EndSide, #0,
                                endstop_posh = EndHigh, #0,  
                                pos = pos,
                                name = "idlepulleyhold")
        
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
            set_place(self.IdlePulleyHolder, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3),round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.IdlePulleyHolder,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Idle_Pulley_Holder',_IdlePulleyHolder_Cmd())