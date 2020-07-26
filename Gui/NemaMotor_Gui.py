import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from partset_new import NemaMotorPulleySet
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _NemaMotor_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(NemaMotor_Dialog())
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Nema Motor',
            'Nema Motor')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Nema Motor',
            'Creates a Motor')
        return {
            'Pixmap': __dir__ + '/../icons/NemaMotor_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class NemaMotor_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Nema Motor options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        
        self.placement = True

        # ---- Size ----
        self.Label_size = QtWidgets.QLabel("Size:")
        self.Size = QtWidgets.QComboBox()
        self.Size.addItems(['8','11','14','17','23','34','42'])
        self.Size.setCurrentIndex(0)

        size_layout = QtWidgets.QHBoxLayout()
        size_layout.addWidget(self.Label_size)
        size_layout.addWidget(self.Size)

        # --- Height ----
        self.Label_Height = QtWidgets.QLabel("Height without shaft:")
        self.Height = QtWidgets.QDoubleSpinBox()
        self.Height.setValue(32)
        self.Height.setSuffix(' mm')
        self.Height.setMinimum(1)

        height_layout = QtWidgets.QHBoxLayout()
        height_layout.addWidget(self.Label_Height)
        height_layout.addWidget(self.Height)

        # ---- Shaft ----
        self.Label_shaft = QtWidgets.QLabel("Shaft")
        self.Label_shaft.setAlignment(QtCore.Qt.AlignTop)
        self.Label_shaft_h = QtWidgets.QLabel("height:")
        self.Label_shaft_r = QtWidgets.QLabel("radius:")
        self.Label_shaft_br = QtWidgets.QLabel("radius base:")
        self.Label_shaft_bh = QtWidgets.QLabel("height base:")
        self.shaft_h = QtWidgets.QDoubleSpinBox()
        self.shaft_r = QtWidgets.QDoubleSpinBox()
        self.shaft_br = QtWidgets.QDoubleSpinBox()
        self.shaft_bh = QtWidgets.QDoubleSpinBox()
        self.shaft_h.setValue(24.)
        self.shaft_r.setValue(0)
        self.shaft_br.setValue(11)
        self.shaft_bh.setValue(2)
        self.shaft_h.setSuffix(' mm')
        self.shaft_r.setSuffix(' mm')
        self.shaft_br.setSuffix(' mm')
        self.shaft_bh.setSuffix(' mm')
        self.shaft_h.setMinimum(1)
        self.shaft_r.setMinimum(1)
        self.shaft_br.setMinimum(1)
        self.shaft_bh.setMinimum(1)

        shaft_layout = QtWidgets.QHBoxLayout()
        shaft_layout_1 = QtWidgets.QVBoxLayout()
        shaft_layout_2 = QtWidgets.QVBoxLayout()
        shaft_layout_3 = QtWidgets.QVBoxLayout()
        shaft_layout_1.addWidget(self.Label_shaft)
        shaft_layout_2.addWidget(self.Label_shaft_h)
        shaft_layout_2.addWidget(self.Label_shaft_r)
        shaft_layout_2.addWidget(self.Label_shaft_br)
        shaft_layout_2.addWidget(self.Label_shaft_bh)
        shaft_layout_3.addWidget(self.shaft_h)
        shaft_layout_3.addWidget(self.shaft_r)
        shaft_layout_3.addWidget(self.shaft_br)
        shaft_layout_3.addWidget(self.shaft_bh)
        shaft_layout.addLayout(shaft_layout_1)
        shaft_layout.addLayout(shaft_layout_2)
        shaft_layout.addLayout(shaft_layout_3)
        

        # ---- Chamfer ----
        self.Label_chmf_r = QtWidgets.QLabel("Chamfer radius:") 
        self.chmf_r = QtWidgets.QDoubleSpinBox()
        self.chmf_r.setValue(1)
        self.chmf_r.setSuffix(' mm')
        self.chmf_r.setMinimum(0)

        cham_layout = QtWidgets.QHBoxLayout()
        cham_layout.addWidget(self.Label_chmf_r)
        cham_layout.addWidget(self.chmf_r)

        # ---- Bolt ----
        self.Label_bolt = QtWidgets.QLabel("Bolt deep:") 
        self.bolt_d = QtWidgets.QDoubleSpinBox()
        self.bolt_d.setValue(3)
        self.bolt_d.setSuffix(' mm')
        self.bolt_d.setMinimum(0)

        bolt_layout = QtWidgets.QHBoxLayout()
        bolt_layout.addWidget(self.Label_bolt)
        bolt_layout.addWidget(self.bolt_d)

        # ---- Pulley ----
        self.Label_pulley = QtWidgets.QLabel("Pulley")
        self.Label_pulley.setAlignment(QtCore.Qt.AlignTop)
        self.Label_pulley_pitch = QtWidgets.QLabel("pitch:")
        self.Label_pulley_teeth = QtWidgets.QLabel("teeth:")
        self.Label_pulley_top_flan = QtWidgets.QLabel("top flange:")
        self.Label_pulley_bot_flan = QtWidgets.QLabel("bot flange:")
        self.pulley_pitch = QtWidgets.QDoubleSpinBox()
        self.pulley_teeth = QtWidgets.QDoubleSpinBox()
        self.pulley_top_flan = QtWidgets.QDoubleSpinBox()
        self.pulley_bot_flan = QtWidgets.QDoubleSpinBox()
        self.pulley_pitch.setValue(2.)
        self.pulley_teeth.setValue(20)
        self.pulley_top_flan.setValue(1)
        self.pulley_bot_flan.setValue(0)
        self.pulley_pitch.setSuffix(' mm')
        self.pulley_teeth.setSuffix(' mm')
        self.pulley_teeth.setSuffix(' mm')
        self.pulley_bot_flan.setSuffix(' mm')
        self.pulley_pitch.setMinimum(0)
        self.pulley_teeth.setMinimum(0)
        self.pulley_top_flan.setMinimum(0)
        self.pulley_bot_flan.setMinimum(0)

        pulley_layout = QtWidgets.QHBoxLayout()
        pulley_layout_1 = QtWidgets.QVBoxLayout()
        pulley_layout_2 = QtWidgets.QVBoxLayout()
        pulley_layout_3 = QtWidgets.QVBoxLayout()
        pulley_layout_1.addWidget(self.Label_pulley)
        pulley_layout_2.addWidget(self.Label_pulley_pitch)
        pulley_layout_2.addWidget(self.Label_pulley_teeth)
        pulley_layout_2.addWidget(self.Label_pulley_top_flan)
        pulley_layout_2.addWidget(self.Label_pulley_bot_flan)
        pulley_layout_3.addWidget(self.pulley_pitch)
        pulley_layout_3.addWidget(self.pulley_teeth)
        pulley_layout_3.addWidget(self.pulley_top_flan)
        pulley_layout_3.addWidget(self.pulley_bot_flan)

        pulley_layout.addLayout(pulley_layout_1)
        pulley_layout.addLayout(pulley_layout_2)
        pulley_layout.addLayout(pulley_layout_3)

        # ---- Placement ----:
        self.label_position = QtWidgets.QLabel("Position ")
        self.label_position.setAlignment(QtCore.Qt.AlignTop)

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
        self.pos_d.addItems(['0','1','2','3','4'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3','4'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2','3','4','5'])
        self.pos_h.setCurrentIndex(1)

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
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/NemaMotor.png">hear</a>.')
        image.setOpenExternalLinks(True)

        main_layout.addLayout(size_layout)
        main_layout.addLayout(height_layout)
        main_layout.addLayout(shaft_layout)
        main_layout.addLayout(pulley_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)

class NemaMotor_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.NemaMotor = NemaMotor_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.NemaMotor)
        self.form = [self.NemaMotor.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        dict_size = {0: 8, 1: 11, 2: 14, 3: 17, 5: 23, 6: 34, 7: 42}
        size = dict_size[self.NemaMotor.Size.currentIndex()]
        base_h = self.NemaMotor.Height.value()
        shaft_l = self.NemaMotor.shaft_h.value()
        shaft_r = self.NemaMotor.shaft_r.value()
        shaft_br = self.NemaMotor.shaft_br.value()
        shaft_hr = self.NemaMotor.shaft_bh.value()
        chmf_r = self.NemaMotor.chmf_r.value()
        bolt_d = self.NemaMotor.bolt_d.value()
        pitch = self.NemaMotor.pulley_pitch.value()
        teeth = self.NemaMotor.pulley_teeth.value()
        top_flan = self.NemaMotor.pulley_top_flan.value()
        bot_flan = self.NemaMotor.pulley_bot_flan.value()
        positions_d = [0,1,2,3,4]
        positions_w = [0,1,2,3,4]
        positions_h = [0,1,2,3,4,5]
        pos_d = positions_d[self.NemaMotor.pos_d.currentIndex()]
        pos_w = positions_w[self.NemaMotor.pos_w.currentIndex()]
        pos_h = positions_h[self.NemaMotor.pos_h.currentIndex()]
        pos = FreeCAD.Vector(self.NemaMotor.pos_x.value(),self.NemaMotor.pos_y.value(),self.NemaMotor.pos_z.value())
        axis_d = FreeCAD.Vector(self.NemaMotor.axis_d_x.value(),self.NemaMotor.axis_d_y.value(),self.NemaMotor.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.NemaMotor.axis_w_x.value(),self.NemaMotor.axis_w_y.value(),self.NemaMotor.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.NemaMotor.axis_h_x.value(),self.NemaMotor.axis_h_y.value(),self.NemaMotor.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            NemaMotorPulleySet(nema_size = size,
                                base_l = base_h,
                                shaft_l = shaft_l,
                                shaft_r = shaft_r,
                                circle_r = shaft_br,
                                circle_h = shaft_hr,
                                chmf_r = chmf_r, 
                                rear_shaft_l=0,
                                bolt_depth = bolt_d,
                                # pulley parameters
                                pulley_pitch = pitch,
                                pulley_n_teeth = teeth,
                                pulley_toothed_h = 7.5,
                                pulley_top_flange_h = top_flan,
                                pulley_bot_flange_h = bot_flan,
                                pulley_tot_h = 16.,
                                pulley_flange_d = 15.,
                                pulley_base_d = 15.,
                                pulley_tol = 0,
                                pulley_pos_h = -1,
                                # general parameters
                                axis_d = axis_d,
                                axis_w = axis_w, #None
                                axis_h = axis_h,
                                pos_d = pos_d,
                                pos_w = pos_w,
                                pos_h = pos_h,
                                pos = pos,
                                group = 1,
                                name = None)

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
            set_place(self.NemaMotor, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.NemaMotor,pos.x,pos.y,pos.z)
            except Exception: None

# command
FreeCADGui.addCommand('Motor',_NemaMotor_Cmd())
