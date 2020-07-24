import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from filter_stage_fun import filter_stage_fun
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000
class _FilterStage_Cmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Filter Holder options")
        panel = FilterStage_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel)

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Filter_Stage_',
            'Filter Stage')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Filter_Stage',
            'Creates a Filter Stage with set parametres')
        return {
            'Pixmap': __dir__ + '/../icons/Filter_Stage_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class FilterStage_TaskPanel:                                    
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        # ---- Move distance ----
        self.move_l_Label = QtWidgets.QLabel("Move distance:")
        self.move_l_Value = QtWidgets.QDoubleSpinBox()
        self.move_l_Value.setValue(60)
        self.move_l_Value.setSuffix(' mm')

        move_layout = QtWidgets.QHBoxLayout()
        move_layout.addWidget(self.move_l_Label)
        move_layout.addWidget(self.move_l_Value)

        # ---- Filter Length ----
        self.Filter_Length_Label = QtWidgets.QLabel("Filter Length")
        self.Filter_Length_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Length_Value.setValue(60)
        self.Filter_Length_Value.setSuffix(' mm')

        length_layout = QtWidgets.QHBoxLayout()
        length_layout.addWidget(self.Filter_Length_Label)
        length_layout.addWidget(self.Filter_Length_Value)

        # ---- Filter Width ----
        self.Filter_Width_Label = QtWidgets.QLabel("Filter Width")
        self.Filter_Width_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Width_Value.setValue(25)
        self.Filter_Width_Value.setSuffix(' mm')

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.Filter_Width_Label)
        width_layout.addWidget(self.Filter_Width_Value)

        # ---- Base width ----
        self.base_w_Label = QtWidgets.QLabel("Base width:")  #10/15/20/30/40
        self.ComboBox_base_w = QtWidgets.QComboBox()
        self.TextBase_W = ["10mm","15mm","20mm","30mm","40mm"] 
        self.ComboBox_base_w.addItems(self.TextBase_W)
        self.ComboBox_base_w.setCurrentIndex(self.TextBase_W.index('20mm'))

        base_width_layout = QtWidgets.QHBoxLayout()
        base_width_layout.addWidget(self.base_w_Label)
        base_width_layout.addWidget(self.ComboBox_base_w)

        # ---- Tensioner Stroke ----
        self.tens_stroke_Label = QtWidgets.QLabel("Tensioner stroke:")
        self.tens_stroke_Value = QtWidgets.QDoubleSpinBox()
        self.tens_stroke_Value.setValue(20)
        self.tens_stroke_Value.setSuffix(' mm')

        tensioner_layout = QtWidgets.QHBoxLayout()
        tensioner_layout.addWidget(self.tens_stroke_Label)
        tensioner_layout.addWidget(self.tens_stroke_Value)

        # ---- Wall thick ----
        self.wall_th_Label = QtWidgets.QLabel("Wall thick:")
        self.wall_th_Value = QtWidgets.QDoubleSpinBox()
        self.wall_th_Value.setValue(3)
        self.wall_th_Value.setSuffix(' mm')

        wall_layout = QtWidgets.QHBoxLayout()
        wall_layout.addWidget(self.wall_th_Label)
        wall_layout.addWidget(self.wall_th_Value)


        # ---- Nut Type ----
        self.nut_hole_Label = QtWidgets.QLabel("Nut Type:")   
        self.ComboBox_Nut_Hole = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.ComboBox_Nut_Hole.addItems(self.TextNutType)
        self.ComboBox_Nut_Hole.setCurrentIndex(self.TextNutType.index('M3'))

        nut_layout = QtWidgets.QHBoxLayout()
        nut_layout.addWidget(self.nut_hole_Label)
        nut_layout.addWidget(self.ComboBox_Nut_Hole)

        # ---- Size Holder ----
        self.Size_Holder_Label = QtWidgets.QLabel("Motor size")
        self.ComboBox_Size_Holder = QtWidgets.QComboBox()
        self.TextSizeHolder = ["8","11","14","17","23","34","42"]
        self.ComboBox_Size_Holder.addItems(self.TextSizeHolder)
        self.ComboBox_Size_Holder.setCurrentIndex(self.TextSizeHolder.index('14'))

        nema_holder_layout = QtWidgets.QHBoxLayout()
        nema_holder_layout.addWidget(self.Size_Holder_Label)
        nema_holder_layout.addWidget(self.ComboBox_Size_Holder)

        # ---- Rail Max High  ----
        self.motor_high_Label = QtWidgets.QLabel("Rail high Motor holder")
        self.motor_high_Value = QtWidgets.QDoubleSpinBox()
        self.motor_high_Value.setValue(25) #Value printed
        self.motor_high_Value.setSuffix(' mm')

        rail_layout = QtWidgets.QHBoxLayout()
        rail_layout.addWidget(self.motor_high_Label)
        rail_layout.addWidget(self.motor_high_Value)

        # ---- Thikness ----
        self.Thikness_Label = QtWidgets.QLabel("Motor holder thikness:")
        self.Thikness_Value = QtWidgets.QDoubleSpinBox()
        self.Thikness_Value.setValue(3)
        self.Thikness_Value.setMinimum(2)
        self.Thikness_Value.setSuffix(' mm')

        thikness_layout = QtWidgets.QHBoxLayout()
        thikness_layout.addWidget(self.Thikness_Label)
        thikness_layout.addWidget(self.Thikness_Value)

        # ---- Placement ----
        self.label_position = QtWidgets.QLabel("Placement ")
        self.label_pos_x = QtWidgets.QLabel("x:")
        self.label_pos_y = QtWidgets.QLabel("y:")
        self.label_pos_z = QtWidgets.QLabel("z:")
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
        placement_layout_1 = QtWidgets.QHBoxLayout()
        placement_layout_2 = QtWidgets.QVBoxLayout()
        placement_layout_3 = QtWidgets.QVBoxLayout()

        placement_layout.addLayout(placement_layout_1)
        placement_layout.addLayout(placement_layout_2)
        placement_layout.addLayout(placement_layout_3)

        placement_layout_1.addWidget(self.label_position)
        placement_layout_2.addWidget(self.label_pos_x)
        placement_layout_2.addWidget(self.label_pos_y)
        placement_layout_2.addWidget(self.label_pos_z)
        placement_layout_3.addWidget(self.pos_x)
        placement_layout_3.addWidget(self.pos_y)
        placement_layout_3.addWidget(self.pos_z)


        main_layout.addLayout(move_layout)
        main_layout.addLayout(length_layout)
        main_layout.addLayout(width_layout)
        main_layout.addLayout(base_width_layout)
        main_layout.addLayout(tensioner_layout)
        main_layout.addLayout(wall_layout)
        main_layout.addLayout(nut_layout)
        main_layout.addLayout(nema_holder_layout)
        main_layout.addLayout(rail_layout)
        main_layout.addLayout(thikness_layout)
        main_layout.addLayout(placement_layout)

        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        self.selec_base = {0: 5, 1: 10, 2: 15, 3: 20, 4: 30, 5: 40}
        move_l = self.move_l_Value.value()
        #Filter holder
        Filter_Length = self.Filter_Length_Value.value()
        Filter_Width = self.Filter_Width_Value.value()
        #tensioner
        nut_hole = 3 + self.ComboBox_Nut_Hole.currentIndex()  #Index star in 0, first value = 3
        tens_stroke = self.tens_stroke_Value.value()
        base_w = self.selec_base[self.ComboBox_base_w.currentIndex()]
        wall_thick = self.wall_th_Value.value()
        #motor holder
        SizeHolder = {0:8, 1:11, 2:14, 3:17, 4:23, 5:34, 6:42}
        size_motor = SizeHolder[self.ComboBox_Size_Holder.currentIndex()]
        h_motor=self.motor_high_Value.value()
        thik_motor = self.Thikness_Value.value()

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())

        filter_stage_fun(move_l,Filter_Length,Filter_Width, nut_hole, tens_stroke, base_w, wall_thick, size_motor, h_motor, thik_motor, pos)
            #pulley_h => belt_pos_h
            #nut_hole => bolttens_mtr
            #tens_stroke => tens_stroke_Var
            #base_w => aluprof_w
            #wall_thick => wall_thick_Var
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
            self.pos_x.setValue(round(self.v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(self.v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Filter_Stage', _FilterStage_Cmd())