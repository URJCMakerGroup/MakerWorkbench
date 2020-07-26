import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts_new import NemaMotorHolder
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis
__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _MotorHolder_Cmd:
    
    def Activated(self):
        FreeCADGui.Control.showDialog(MotorHolder_Dialog()) 
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Motor Holder',
            'Motor Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Motor Holder',
            'Creates a Motor Holder')
        return {
            'Pixmap': __dir__ + '/../icons/Motor_Holder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class MotorHolder_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Motor Holder options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Size Holder ----
        self.Size_Holder_Label = QtWidgets.QLabel("Size")
        self.ComboBox_Size_Holder = QtWidgets.QComboBox()
        self.TextSizeHolder = ["8","11","14","17","23","34","42"]
        self.ComboBox_Size_Holder.addItems(self.TextSizeHolder)
        self.ComboBox_Size_Holder.setCurrentIndex(self.TextSizeHolder.index('11'))

        size_layout = QtWidgets.QHBoxLayout()
        size_layout.addWidget(self.Size_Holder_Label)
        size_layout.addWidget(self.ComboBox_Size_Holder)

        # ---- Rail Max High  ----
        self.motor_high_Label = QtWidgets.QLabel("Rail max High")
        self.motor_high_Value = QtWidgets.QDoubleSpinBox()
        self.motor_high_Value.setValue(40)
        self.motor_high_Value.setSuffix(' mm')

        motor_high_layout = QtWidgets.QHBoxLayout()
        motor_high_layout.addWidget(self.motor_high_Label)
        motor_high_layout.addWidget(self.motor_high_Value)

        # ---- Thikness ----
        self.Thikness_Label = QtWidgets.QLabel("Thikness:")
        self.Thikness_Value = QtWidgets.QDoubleSpinBox()
        self.Thikness_Value.setValue(3)
        self.Thikness_Value.setMinimum(2)
        self.Thikness_Value.setSuffix(' mm')

        thik_layout = QtWidgets.QHBoxLayout()
        thik_layout.addWidget(self.Thikness_Label)
        thik_layout.addWidget(self.Thikness_Value)

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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3','4','5'])
        self.pos_d.setCurrentIndex(3)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2','3','4'])
        self.pos_h.setCurrentIndex(1)

        placement_layout_2.addWidget(self.Label_pos_h)
        placement_layout_3.addWidget(self.pos_h)

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

        # ---- Image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/MotorHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(size_layout)
        main_layout.addLayout(motor_high_layout)
        main_layout.addLayout(thik_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class MotorHolder_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.MotorHolder = MotorHolder_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.MotorHolder)
        self.form = [self.MotorHolder.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        SizeHolder = {0:8, 1:11, 2:14, 3:17, 4:23, 5:34, 6:42}
        self.size_motor = SizeHolder[self.MotorHolder.ComboBox_Size_Holder.currentIndex()]
        h_motor=self.MotorHolder.motor_high_Value.value()
        Thikness = self.MotorHolder.Thikness_Value.value()
        pos = FreeCAD.Vector(self.MotorHolder.pos_x.value(), self.MotorHolder.pos_y.value(), self.MotorHolder.pos_z.value())
        pos_h = self.MotorHolder.pos_h.currentIndex()
        pos_d = self.MotorHolder.pos_d.currentIndex()
        pos_w = self.MotorHolder.pos_w.currentIndex()
        axis_d = FreeCAD.Vector(self.MotorHolder.axis_d_x.value(),self.MotorHolder.axis_d_y.value(),self.MotorHolder.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.MotorHolder.axis_w_x.value(),self.MotorHolder.axis_w_y.value(),self.MotorHolder.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.MotorHolder.axis_h_x.value(),self.MotorHolder.axis_h_y.value(),self.MotorHolder.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:

            NemaMotorHolder(nema_size = self.size_motor,
                            wall_thick = Thikness,
                            motorside_thick = Thikness,
                            reinf_thick = Thikness,
                            motor_min_h =10.,
                            motor_max_h = h_motor,
                            rail = 1, # if there is a rail or not at the profile side
                            motor_xtr_space = 2., # counting on one side
                            bolt_wall_d = 4., # Metric of the wall bolts
                            bolt_wall_sep = 0., # optional   30
                            chmf_r = 1.,
                            axis_h = axis_h,
                            axis_d = axis_d,
                            axis_w = axis_w,
                            pos_h = pos_h,
                            pos_d = pos_d,
                            pos_w = pos_w,
                            pos = pos,
                            model_type = 3,
                            name = 'nema_holder')

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
            set_place(self.MotorHolder, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))

        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.MotorHolder,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Motor_Holder',_MotorHolder_Cmd())