import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from tensioner_clss_new import TensionerSet
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _Tensioner_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(Tensioner_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Tensioner',
            'Tensioner')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Tensioner',
            'Creates a Tensioner')
        return {
            'Pixmap': __dir__ + '/../icons/Tensioner_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class Tensioner_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Tensioner options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Belt High ----
        self.belt_h_Label = QtWidgets.QLabel("Belt hight:")
        self.belt_h_Value = QtWidgets.QDoubleSpinBox()
        self.belt_h_Value.setValue(20)
        self.belt_h_Value.setSuffix(' mm')

        BeltHight_layout = QtWidgets.QHBoxLayout()
        BeltHight_layout.addWidget(self.belt_h_Label)
        BeltHight_layout.addWidget(self.belt_h_Value)

        # ---- Base width ----
        self.base_w_Label = QtWidgets.QLabel("Base width:")  #10/15/20/30/40
        self.ComboBox_base_w = QtWidgets.QComboBox()
        self.TextBase_W = ["10mm","15mm","20mm","30mm","40mm"] 
        self.ComboBox_base_w.addItems(self.TextBase_W)
        self.ComboBox_base_w.setCurrentIndex(self.TextBase_W.index('20mm'))
        
        BaseWidth_layout = QtWidgets.QHBoxLayout()
        BaseWidth_layout.addWidget(self.base_w_Label)
        BaseWidth_layout.addWidget(self.ComboBox_base_w)

        # ---- Tensioner Stroke ----
        self.tens_stroke_Label = QtWidgets.QLabel("Tensioner stroke:")
        self.tens_stroke_Value = QtWidgets.QDoubleSpinBox()
        self.tens_stroke_Value.setValue(20)
        self.tens_stroke_Value.setSuffix(' mm')

        Stroke_layout = QtWidgets.QHBoxLayout()
        Stroke_layout.addWidget(self.tens_stroke_Label)
        Stroke_layout.addWidget(self.tens_stroke_Value)

        # ---- Wall thick ----
        self.wall_th_Label = QtWidgets.QLabel("Wall thick:")
        self.wall_th_Value = QtWidgets.QDoubleSpinBox()
        self.wall_th_Value.setValue(3)
        self.wall_th_Value.setSuffix(' mm')

        Wall_layout = QtWidgets.QHBoxLayout()
        Wall_layout.addWidget(self.wall_th_Label)
        Wall_layout.addWidget(self.wall_th_Value)

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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3','4','5','6'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2'])
        self.pos_h.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_h)
        placement_layout_3.addWidget(self.pos_h)

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
        self.axis_d_x.setValue(0)
        self.axis_d_y.setValue(-1)
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
        self.axis_w_x.setValue(-1)
        self.axis_w_y.setValue(0)
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
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/Tensioner.png">here</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)
        
        main_layout.addLayout(BeltHight_layout)
        main_layout.addLayout(BaseWidth_layout)
        main_layout.addLayout(Stroke_layout)
        main_layout.addLayout(Wall_layout)
        main_layout.addLayout(Nut_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class Tensioner_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.Tensioner = Tensioner_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.Tensioner)
        self.form = [self.Tensioner.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        IndexNut = {0:3,1:4,2:5,3:6}
        IndexBase = {0: 10, 1: 15, 2: 20, 3: 30, 4: 40}
        tensioner_belt_h = self.Tensioner.belt_h_Value.value()
        nut_hole = IndexNut[self.Tensioner.ComboBox_Nut_Hole.currentIndex()]
        tens_stroke = self.Tensioner.tens_stroke_Value.value()
        base_w = IndexBase[self.Tensioner.ComboBox_base_w.currentIndex()]
        wall_thick = self.Tensioner.wall_th_Value.value()
        pos = FreeCAD.Vector(self.Tensioner.pos_x.value(), self.Tensioner.pos_y.value(), self.Tensioner.pos_z.value())
        positions_d = [0,1,2,3,4,5,6]
        positions_w = [0,1,2]
        positions_h = [0,1,2]
        pos_d = positions_d[self.Tensioner.pos_d.currentIndex()]
        pos_w = positions_w[self.Tensioner.pos_w.currentIndex()]
        pos_h = positions_h[self.Tensioner.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.Tensioner.axis_d_x.value(),self.Tensioner.axis_d_y.value(),self.Tensioner.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.Tensioner.axis_w_x.value(),self.Tensioner.axis_w_y.value(),self.Tensioner.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.Tensioner.axis_h_x.value(),self.Tensioner.axis_h_y.value(),self.Tensioner.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            TensionerSet(aluprof_w = base_w,#20.,
                        belt_pos_h = tensioner_belt_h, 
                        hold_bas_h = 0,
                        hold_hole_2sides = 1,
                        boltidler_mtr = 3,
                        bolttens_mtr = nut_hole,   #métrica del tensor
                        boltaluprof_mtr = nut_hole,
                        tens_stroke = tens_stroke ,
                        wall_thick = wall_thick,
                        in_fillet = 2.,
                        pulley_stroke_dist = 0,
                        nut_holder_thick = nut_hole ,   
                        opt_tens_chmf = 0,
                        min_width = 0,
                        tol = kcomp.TOL,
                        axis_d = axis_d,#VY.negative(),
                        axis_w = axis_w,#VX.negative(),
                        axis_h = axis_h,#VZ,
                        pos_d = pos_d,
                        pos_w = pos_w,
                        pos_h = pos_h,
                        pos = pos,
                        name = 'tensioner_set')

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
            set_place(self.Tensioner, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.Tensioner,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Tensioner',_Tensioner_Cmd())