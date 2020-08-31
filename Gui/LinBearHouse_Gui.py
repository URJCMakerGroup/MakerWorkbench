import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts import ThinLinBearHouse, ThinLinBearHouse1rail, ThinLinBearHouseAsim, LinBearHouse
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _LinBearHouse_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(LinBearHouse_Dialog())
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Linear Bear House',
            'Linear Bear House')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Linear Bear House',
            'Creates a Linear Bear House')
        return {
            'Pixmap': __dir__ + '/../icons/Thin_Linear_Bear_House_1Rail_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class LinBearHouse_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Linear Bear House options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Version ----
        self.LinBearHouse_Label = QtWidgets.QLabel("Select Bear House:")
        self.LinBearHouse_ComboBox = QtWidgets.QComboBox()
        self.LinBearHouse_text = ["Thin 1 rail", "Thin","Normal (only SC type)","Asimetric"]
        self.LinBearHouse_ComboBox.addItems(self.LinBearHouse_text)
        self.LinBearHouse_ComboBox.setCurrentIndex(0)

        version_layout = QtWidgets.QHBoxLayout()
        version_layout.addWidget(self.LinBearHouse_Label)
        version_layout.addWidget(self.LinBearHouse_ComboBox)

        # ---- Type ----
        self.Type_Label = QtWidgets.QLabel("Type:")
        self.Type_ComboBox = QtWidgets.QComboBox()
        self.Type_text = ["LMUU 6","LMUU 8","LMUU 10","LMUU 12","LMUU 20","LMEUU 8","LMEUU 10","LMEUU12","LMELUU 12","LMEUU 20","SC8UU_Pr","SC10UU_Pr","SC12UU_Pr","SCE20UU_Pr30","SCE20UU_Pr30b"]
        self.Type_ComboBox.addItems(self.Type_text)
        self.Type_ComboBox.setCurrentIndex(1)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Type_Label)
        type_layout.addWidget(self.Type_ComboBox)

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
        self.axis_h_x.setValue(0.00)
        self.axis_h_y.setValue(0.00)
        self.axis_h_z.setValue(-1.00)

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
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/LinearBearHouse.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(version_layout)
        main_layout.addLayout(type_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class LinBearHouse_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.LinBearHouse = LinBearHouse_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.LinBearHouse)
        self.form = [self.LinBearHouse.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Type_values = {0:kcomp.LM6UU,
                       1:kcomp.LM8UU,
                       2:kcomp.LM10UU,
                       3:kcomp.LM12UU,
                       4:kcomp.LM20UU,
                       5:kcomp.LME8UU,
                       6:kcomp.LME10UU,
                       7:kcomp.LME12UU,
                       8:kcomp.LME12LUU,
                       9:kcomp.LME20UU,
                       10:kcomp.SC8UU_Pr,
                       11:kcomp.SC10UU_Pr,
                       12:kcomp.SC12UU_Pr,
                       13:kcomp.SCE20UU_Pr30,
                       14:kcomp.SCE20UU_Pr30b }

        LinBearHouse = self.LinBearHouse.LinBearHouse_ComboBox.currentIndex()
        Type = Type_values[self.LinBearHouse.Type_ComboBox.currentIndex()]
        pos = FreeCAD.Vector(self.LinBearHouse.pos_x.value(), self.LinBearHouse.pos_y.value(), self.LinBearHouse.pos_z.value())
        axis_d = FreeCAD.Vector(self.LinBearHouse.axis_d_x.value(),self.LinBearHouse.axis_d_y.value(),self.LinBearHouse.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.LinBearHouse.axis_w_x.value(),self.LinBearHouse.axis_w_y.value(),self.LinBearHouse.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.LinBearHouse.axis_h_x.value(),self.LinBearHouse.axis_h_y.value(),self.LinBearHouse.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if LinBearHouse == 0:
                ThinLinBearHouse1rail(d_lbear = Type,
                                            fc_slide_axis = axis_d, #VX
                                            fc_bot_axis =axis_h, #VZN
                                            axis_center = 1,
                                            mid_center  = 1,
                                            pos = pos,
                                            name = 'thinlinbearhouse1rail')
            elif LinBearHouse == 1:
                ThinLinBearHouse(d_lbear = Type,
                                    fc_slide_axis = axis_d, #VX
                                    fc_bot_axis =axis_h, #VZN
                                    fc_perp_axis = axis_w,
                                    axis_h = 0,
                                    bolts_side = 1,
                                    axis_center = 1,
                                    mid_center  = 1,
                                    bolt_center  = 0,
                                    pos = pos,
                                    name = 'thinlinbearhouse')
            elif LinBearHouse == 2:
                LinBearHouse(d_lbearhousing = Type, #SC only
                                fc_slide_axis = axis_d, #VX
                                fc_bot_axis =axis_h, #VZN
                                axis_center = 1,
                                mid_center  = 1,
                                pos = pos,
                                name = 'linbearhouse')

            else:
                ThinLinBearHouseAsim(d_lbear = Type,
                                        fc_fro_ax = axis_d,
                                        fc_bot_ax = axis_h,
                                        fc_sid_ax = axis_w,
                                        axis_h = 0,
                                        bolts_side = 1,
                                        refcen_hei = 1,
                                        refcen_dep  = 1,
                                        refcen_wid  = 1,
                                        bolt2cen_wid_n = 0,
                                        bolt2cen_wid_p = 0,
                                        pos = pos,
                                        name = 'thinlinbearhouse_asim')


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
            set_place(self.LinBearHouse, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.LinBearHouse,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('LinBearHouse',_LinBearHouse_Cmd())