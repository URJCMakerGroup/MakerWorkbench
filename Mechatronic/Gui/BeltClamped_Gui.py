import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from beltcl import PartBeltClamped
from Advance_Placement_Gui import Advance_Placement_TaskPanel
from function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

# This part dindt work properly. Need more test for the moment.
#   IS DISABLED IN InitGui.py file.
class _BeltClamped_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(BeltClamped_Dialog())

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Belt clamped')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a belt clamped')
        return {
            'Pixmap': __dir__ + '/icons/Belt_Clamped_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class BeltClamped_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Belt Clamped options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Diameters ----
        #Label :
        self.Label_Diameter = QtWidgets.QLabel("Diameter pulley")
        self.Label_Diameter.setAlignment(QtCore.Qt.AlignTop)
        # 1:
        self.Label_Diameter_1 = QtWidgets.QLabel("1:")   
        self.Pulley_D1 = QtWidgets.QDoubleSpinBox()
        self.Pulley_D1.setValue(5)
        self.Pulley_D1.setSuffix('')
        self.Pulley_D1.setMinimum(1)

        # 2:
        self.Label_Diameter_2 = QtWidgets.QLabel("2:")
        self.Pulley_D2 = QtWidgets.QDoubleSpinBox()
        self.Pulley_D2.setValue(6)
        self.Pulley_D2.setSuffix('')
        self.Pulley_D2.setMinimum(1)

        diameter_layout = QtWidgets.QHBoxLayout()
        diameter_layout_1 = QtWidgets.QVBoxLayout()
        diameter_layout_2 = QtWidgets.QVBoxLayout()
        diameter_layout_3 = QtWidgets.QVBoxLayout()

        diameter_layout.addLayout(diameter_layout_1)
        diameter_layout.addLayout(diameter_layout_2)
        diameter_layout.addLayout(diameter_layout_3)

        diameter_layout_1.addWidget(self.Label_Diameter)

        diameter_layout_2.addWidget(self.Label_Diameter_1)
        diameter_layout_2.addWidget(self.Label_Diameter_2)

        diameter_layout_3.addWidget(self.Pulley_D1)
        diameter_layout_3.addWidget(self.Pulley_D2)

        # ---- Separation ----
        # Label :
        self.Label_Sep = QtWidgets.QLabel("Separation between ")
        self.Label_Sep.setAlignment(QtCore.Qt.AlignTop)

        # Pulleys Axis d:
        self.Label_Sep_d = QtWidgets.QLabel("pulleys in axis d:")
        self.Sep_d = QtWidgets.QDoubleSpinBox()
        self.Sep_d.setValue(80)
        self.Sep_d.setSuffix(' mm')
        self.Sep_d.setMinimum(1)

        # Pulleys Axis w:
        self.Label_Sep_w = QtWidgets.QLabel("pulleys in axis w:")
        self.Sep_w = QtWidgets.QDoubleSpinBox()
        self.Sep_w.setValue(0)
        self.Sep_w.setSuffix(' mm')
        self.Sep_w.setMinimum(1)

        # Pulley 1 and Clamp 1 Axis d:
        self.Label_Sep_Clamp_1d = QtWidgets.QLabel("pulley 1 and clamp 1 in axis d")
        self.Sep_Clamp_1d = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp_1d.setValue(15)
        self.Sep_Clamp_1d.setSuffix(' mm')
        self.Sep_Clamp_1d.setMinimum(1)

        # Pulley 1 and Clamp 1 Axis w:
        self.Label_Sep_Clamp_1w = QtWidgets.QLabel("pulley 1 and clamp 1 in axis w")
        self.Sep_Clamp_1w = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp_1w.setValue(5)
        self.Sep_Clamp_1w.setSuffix(' mm')
        self.Sep_Clamp_1w.setMinimum(1)
        
        # Pulley 2 and Clamp 2 Axis d:
        self.Label_Sep_Clamp_2d = QtWidgets.QLabel("pulley 2 and clamp 2 in axis w")
        self.Sep_Clamp_2d = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp_2d.setValue(15)
        self.Sep_Clamp_2d.setSuffix(' mm')
        self.Sep_Clamp_2d.setMinimum(1)

        separation_layout = QtWidgets.QHBoxLayout()
        separation_layout_1 = QtWidgets.QVBoxLayout()
        separation_layout_2 = QtWidgets.QVBoxLayout()
        separation_layout_3 = QtWidgets.QVBoxLayout()

        separation_layout.addLayout(separation_layout_1)
        separation_layout.addLayout(separation_layout_2)
        separation_layout.addLayout(separation_layout_3)

        separation_layout_1.addWidget(self.Label_Sep)

        separation_layout_2.addWidget(self.Label_Sep_d)
        separation_layout_2.addWidget(self.Label_Sep_w)
        separation_layout_2.addWidget(self.Label_Sep_Clamp_1d)
        separation_layout_2.addWidget(self.Label_Sep_Clamp_1w)
        separation_layout_2.addWidget(self.Label_Sep_Clamp_2d)

        separation_layout_3.addWidget(self.Sep_d)
        separation_layout_3.addWidget(self.Sep_w)
        separation_layout_3.addWidget(self.Sep_Clamp_1d)
        separation_layout_3.addWidget(self.Sep_Clamp_1w)
        separation_layout_3.addWidget(self.Sep_Clamp_2d)

        # ---- Clamp ----
        # Label :
        self.Label_Clamp = QtWidgets.QLabel("Clamp ")
        self.Label_Clamp.setAlignment(QtCore.Qt.AlignTop)

        # Clamp d:
        self.Label_Clamp_d = QtWidgets.QLabel("Lenght:")
        self.Clamp_d = QtWidgets.QDoubleSpinBox()
        self.Clamp_d.setValue(5)
        self.Clamp_d.setSuffix('')
        self.Clamp_d.setMinimum(1)

        # Clamp w:
        self.Label_Clamp_w = QtWidgets.QLabel("Widht:")
        self.Clamp_w = QtWidgets.QDoubleSpinBox()
        self.Clamp_w.setValue(4)
        self.Clamp_w.setSuffix('')
        self.Clamp_w.setMinimum(1)

        # Separation bewteen clamps:
        self.Label_Sep_Clamp = QtWidgets.QLabel("Sepatarion:")
        self.Sep_Clamp = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp.setValue(8)
        self.Sep_Clamp.setSuffix('')
        self.Sep_Clamp.setMinimum(0.5)

        clamp_layout = QtWidgets.QHBoxLayout()
        clamp_layout_1 = QtWidgets.QVBoxLayout()
        clamp_layout_2 = QtWidgets.QVBoxLayout()
        clamp_layout_3 = QtWidgets.QVBoxLayout()

        clamp_layout.addLayout(clamp_layout_1)
        clamp_layout.addLayout(clamp_layout_2)
        clamp_layout.addLayout(clamp_layout_3)

        clamp_layout_1.addWidget(self.Label_Clamp)

        clamp_layout_2.addWidget(self.Label_Clamp_d)
        clamp_layout_2.addWidget(self.Label_Clamp_w)
        clamp_layout_2.addWidget(self.Label_Sep_Clamp)

        clamp_layout_3.addWidget(self.Clamp_d)
        clamp_layout_3.addWidget(self.Clamp_w)
        clamp_layout_3.addWidget(self.Sep_Clamp)

        # ---- Belt ----
        self.label_Belt = QtWidgets.QLabel("Belt ")
        self.label_Belt.setAlignment(QtCore.Qt.AlignTop)

        # Width:
        self.Label_belt_w = QtWidgets.QLabel("Width:")
        self.belt_w = QtWidgets.QDoubleSpinBox()
        self.belt_w.setValue(6)
        self.belt_w.setSuffix(' mm')
        self.belt_w.setMinimum(1)

        # Thick:
        self.Label_belt_t = QtWidgets.QLabel("Thick:")
        self.belt_t = QtWidgets.QDoubleSpinBox()
        self.belt_t.setValue(1.38)
        self.belt_t.setSuffix(' mm')
        self.belt_t.setMinimum(1)

        # Radius cyl:
        self.Label_R_cyl = QtWidgets.QLabel("Radius of the cylinder for the belt:")
        self.R_cyl = QtWidgets.QDoubleSpinBox()
        self.R_cyl.setValue(3)
        self.R_cyl.setSuffix(' mm')
        self.R_cyl.setMinimum(1)

        belt_layout = QtWidgets.QHBoxLayout()
        belt_layout_1 = QtWidgets.QVBoxLayout()
        belt_layout_2 = QtWidgets.QVBoxLayout()
        belt_layout_3 = QtWidgets.QVBoxLayout()
        belt_layout. addLayout(belt_layout_1)
        belt_layout. addLayout(belt_layout_2)
        belt_layout. addLayout(belt_layout_3)

        belt_layout_1.addWidget(self.label_Belt)

        belt_layout_2.addWidget(self.Label_belt_w)
        belt_layout_2.addWidget(self.Label_belt_t)
        belt_layout_2.addWidget(self.Label_R_cyl)

        belt_layout_3.addWidget(self.belt_w)
        belt_layout_3.addWidget(self.belt_t)
        belt_layout_3.addWidget(self.R_cyl)

        # ---- Position ----
        self.label_position = QtWidgets.QLabel("Position ")
        self.label_position.setAlignment(QtCore.Qt.AlignTop)
        self.Label_pos_x = QtWidgets.QLabel("x:")
        self.Label_pos_y = QtWidgets.QLabel("y:")
        self.Label_pos_z = QtWidgets.QLabel("z:")
        self.pos_x = QtWidgets.QDoubleSpinBox()
        self.pos_y = QtWidgets.QDoubleSpinBox()
        self.pos_z = QtWidgets.QDoubleSpinBox()
        self.pos_x.setValue(0)
        self.pos_y.setValue(0)
        self.pos_z.setValue(0)

        placement_layout = QtWidgets.QHBoxLayout()

        placement_layout_1 = QtWidgets.QVBoxLayout()
        placement_layout_1.addWidget(self.label_position)
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
        self.pos_d.addItems(['0','1','2','3','4','5','6','7','8','9','10','11'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3','4','5','6','7','8'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1'])
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
        self.axis_d_x.setValue(0)
        self.axis_d_y.setValue(1)
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
        self.axis_w_x.setValue(1)
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
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/BeltClamped.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(diameter_layout)
        main_layout.addLayout(separation_layout)
        main_layout.addLayout(clamp_layout)
        main_layout.addLayout(belt_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class BeltClamped_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.BeltClamped = BeltClamped_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.BeltClamped)
        self.form = [self.BeltClamped.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        pull1_dm = self.BeltClamped.Pulley_D1.value()
        pull2_dm = self.BeltClamped.Pulley_D2.value()
        pull_sep_d = self.BeltClamped.Sep_d.value()
        pull_sep_w = self.BeltClamped.Sep_w.value()
        clamp_pull1_d = self.BeltClamped.Sep_Clamp_1d.value()
        clamp_pull1_w = self.BeltClamped.Sep_Clamp_1w.value()
        clamp_pull2_d = self.BeltClamped.Sep_Clamp_2d.value()
        clamp_d = self.BeltClamped.Clamp_d.value()
        clamp_w = self.BeltClamped.Clamp_w.value()
        clamp_cyl_sep = self.BeltClamped.Sep_Clamp.value()
        cyl_r = self.BeltClamped.R_cyl.value()
        belt_width = self.BeltClamped.belt_w.value()
        belt_thick = self.BeltClamped.belt_t.value()
        positions_d = [0,1,2,3,4,5,6,7,8,9,10,11]
        positions_w = [0,1,2,3,4,5,6,7,8]
        positions_h = [0,1]
        pos_d = positions_d[self.BeltClamped.pos_d.currentIndex()]
        pos_w = positions_w[self.BeltClamped.pos_w.currentIndex()]
        pos_h = positions_h[self.BeltClamped.pos_h.currentIndex()]
        pos = FreeCAD.Vector(self.BeltClamped.pos_x.value(), self.BeltClamped.pos_y.value(), self.BeltClamped.pos_z.value())
        axis_d = FreeCAD.Vector(self.BeltClamped.axis_d_x.value(),self.BeltClamped.axis_d_y.value(),self.BeltClamped.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.BeltClamped.axis_w_x.value(),self.BeltClamped.axis_w_y.value(),self.BeltClamped.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.BeltClamped.axis_h_x.value(),self.BeltClamped.axis_h_y.value(),self.BeltClamped.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            PartBeltClamped(pull1_dm,
                            pull2_dm,
                            pull_sep_w,
                            pull_sep_d,
                            clamp_pull1_d,
                            clamp_pull1_w,
                            clamp_pull2_d,
                            clamp_d,
                            clamp_w,
                            clamp_cyl_sep,
                            cyl_r,
                            belt_width = belt_width,
                            belt_thick = belt_thick,
                            axis_d = axis_d ,#VY,
                            axis_w = axis_w ,#VX,
                            axis_h = axis_h ,#VZ,
                            pos_d = pos_d,
                            pos_w = pos_w,
                            pos_h = pos_h,
                            pos=pos,
                            name = 'belt')
            
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
            set_place(self.BeltClamped, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.BeltClamped,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Belt_Clamped',_BeltClamped_Cmd())
