import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts import sensor_holder 
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _SensorHolder_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(SensorHolder_Dialog())

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Sensor Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a sensor holder')
        return {
            'Pixmap': __dir__ + '/../icons/Sensor_holder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class SensorHolder_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Sensor Holder options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Sensor Pin Length ----
        self.Sensor_Pin_Length_Label = QtWidgets.QLabel("Sensor Pin Length:")  
        self.Sensor_Pin_Length_Value = QtWidgets.QDoubleSpinBox()
        self.Sensor_Pin_Length_Value.setValue(10)
        self.Sensor_Pin_Length_Value.setSuffix(' mm')
        self.Sensor_Pin_Length_Value.setMinimum(10) #Not sure

        pinlength_layout = QtWidgets.QHBoxLayout()
        pinlength_layout.addWidget(self.Sensor_Pin_Length_Label)
        pinlength_layout.addWidget(self.Sensor_Pin_Length_Value)

        # ---- row 1: Sensor Pin Width ----
        self.Sensor_Pin_Width_Label = QtWidgets.QLabel("Sensor Pin Width:")  
        self.Sensor_Pin_Width_Value = QtWidgets.QDoubleSpinBox()
        self.Sensor_Pin_Width_Value.setValue(2)
        self.Sensor_Pin_Width_Value.setSuffix(' mm')
        self.Sensor_Pin_Width_Value.setMinimum(2) #Not sure

        pinwidth_layout = QtWidgets.QHBoxLayout()
        pinwidth_layout.addWidget(self.Sensor_Pin_Width_Label)
        pinwidth_layout.addWidget(self.Sensor_Pin_Width_Value)
        
        # ---- Sensor Pin High ----
        self.Sensor_Pin_High_Label = QtWidgets.QLabel("Sensor Pin High:")  
        self.Sensor_Pin_High_Value = QtWidgets.QDoubleSpinBox()
        self.Sensor_Pin_High_Value.setValue(3)
        self.Sensor_Pin_High_Value.setSuffix(' mm')
        self.Sensor_Pin_High_Value.setMinimum(3) #Not sure

        pinhigh_layout = QtWidgets.QHBoxLayout()
        pinhigh_layout.addWidget(self.Sensor_Pin_High_Label)
        pinhigh_layout.addWidget(self.Sensor_Pin_High_Value)

        # ---- Depth ----
        self.Depth_CD_Label = QtWidgets.QLabel("Depth:")  
        self.Depth_CD_Value = QtWidgets.QDoubleSpinBox()
        self.Depth_CD_Value.setValue(8)
        self.Depth_CD_Value.setSuffix(' mm')
        self.Depth_CD_Value.setMinimum(8) #Not sure

        depth_layout = QtWidgets.QHBoxLayout()
        depth_layout.addWidget(self.Depth_CD_Label)
        depth_layout.addWidget(self.Depth_CD_Value)

        # ---- Width CD case----
        self.Width_CD_Label = QtWidgets.QLabel("Width CD case:")  
        self.Width_CD_Value = QtWidgets.QDoubleSpinBox()
        self.Width_CD_Value.setValue(20)
        self.Width_CD_Value.setSuffix(' mm')
        self.Width_CD_Value.setMinimum(20) #Not sure

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.Width_CD_Label)
        width_layout.addWidget(self.Width_CD_Value)

        # ---- High CD case----
        self.High_CD_Label = QtWidgets.QLabel("High CD case:")  
        self.High_CD_Value = QtWidgets.QDoubleSpinBox()
        self.High_CD_Value.setValue(37)
        self.High_CD_Value.setSuffix(' mm')
        self.High_CD_Value.setMinimum(37) #Not sure

        high_layout = QtWidgets.QHBoxLayout()
        high_layout.addWidget(self.High_CD_Label)
        high_layout.addWidget(self.High_CD_Value)

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
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/SensorHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(pinlength_layout)
        main_layout.addLayout(pinwidth_layout)
        main_layout.addLayout(pinhigh_layout)
        main_layout.addLayout(depth_layout)
        main_layout.addLayout(width_layout)
        main_layout.addLayout(high_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class SensorHolder_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.SensorHolder = SensorHolder_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.SensorHolder)
        self.form = [self.SensorHolder.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Sensor_Pin_Length = self.SensorHolder.Sensor_Pin_Length_Value.value()
        Sensor_Pin_Width = self.SensorHolder.Sensor_Pin_Width_Value.value()
        Sensor_Pin_High = self.SensorHolder.Sensor_Pin_High_Value.value()
        Depth_CD = self.SensorHolder.Depth_CD_Value.value()
        Width_CD = self.SensorHolder.Width_CD_Value.value()
        High_CD = self.SensorHolder.High_CD_Value.value()
        pos = FreeCAD.Vector(self.SensorHolder.pos_x.value(), self.SensorHolder.pos_y.value(), self.SensorHolder.pos_z.value())
        axis_d = FreeCAD.Vector(self.SensorHolder.axis_d_x.value(),self.SensorHolder.axis_d_y.value(),self.SensorHolder.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.SensorHolder.axis_w_x.value(),self.SensorHolder.axis_w_y.value(),self.SensorHolder.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.SensorHolder.axis_h_x.value(),self.SensorHolder.axis_h_y.value(),self.SensorHolder.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            sensor_holder(sensor_support_length = Sensor_Pin_Length,
                                sensor_pin_sep = 2.54,
                                sensor_pin_pos_h = Sensor_Pin_High,
                                sensor_pin_pos_w = Sensor_Pin_Width,
                                sensor_pin_r_tol = 1.05,
                                sensor_pin_rows = 6,
                                sensor_pin_cols = 6,
                                #sensor_clip_pos_h = 2.45, #position from center
                                #sensor_clip_h_tol = 1.28,
                                #sensor_clip_w_tol = 1.,
                                base_height = High_CD, # height of the cd case
                                base_width = Width_CD, # width of the cd case
                                flap_depth = Depth_CD,
                                flap_thick = 2.,
                                base_thick = 2., #la altura
                                basesensor_thick = 9., #la altura de la parte de los sensores
                                pos =pos,
                                axis_h = axis_h,#VZ,
                                axis_d = axis_d,#VX,
                                axis_w = axis_w,#VY,
                                wfco=1,
                                name = 'sensorholder')

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
            set_place(self.SensorHolder, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.SensorHolder,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Sensor_Holder',_SensorHolder_Cmd())