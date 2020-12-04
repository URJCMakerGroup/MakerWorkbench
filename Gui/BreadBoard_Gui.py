import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from comp_optic import f_breadboard 
from fcfun import fc_isperp
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis, axis_message

import kcomp_optic

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _BreadBoard_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(BreadBoard_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'BreadBoard',
            'BreadBoard')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/../icons/BreadBoard_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class BreadBoard_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Bread Board options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- row 0: length ----
        self.Label_len = QtWidgets.QLabel("Length:")
        self.len = QtWidgets.QDoubleSpinBox()
        self.len.setMinimum(1)
        self.len.setValue(200)
        self.len.setMaximum(9999)

        lenght_layout = QtWidgets.QHBoxLayout()
        lenght_layout.addWidget(self.Label_len)
        lenght_layout.addWidget(self.len)

        # ---- row 1: width ----
        self.Label_wid = QtWidgets.QLabel("Width:")
        self.wid = QtWidgets.QDoubleSpinBox()
        self.wid.setMinimum(1)
        self.wid.setValue(500)
        self.wid.setMaximum(9999)

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.Label_wid)
        width_layout.addWidget(self.wid)

        # ---- row 2: placement ----
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

        # ---- row 5: axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
        self.Label_axis.setAlignment(QtCore.Qt.AlignTop)
        self.Label_axis_w = QtWidgets.QLabel("w:")
        self.Label_axis_h = QtWidgets.QLabel("h:")
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
        axes_layout_2.addWidget(self.Label_axis_w)
        axes_layout_2.addWidget(self.Label_axis_h)

        axes_layout_3 = QtWidgets.QVBoxLayout()
        axes_layout_3.addWidget(self.axis_w_x)
        axes_layout_3.addWidget(self.axis_h_x)

        axes_layout_4 = QtWidgets.QVBoxLayout()
        axes_layout_4.addWidget(self.axis_w_y)
        axes_layout_4.addWidget(self.axis_h_y)

        axes_layout_5 = QtWidgets.QVBoxLayout()
        axes_layout_5.addWidget(self.axis_w_z)
        axes_layout_5.addWidget(self.axis_h_z)

        axes_layout.addLayout(axes_layout_1)
        axes_layout.addLayout(axes_layout_2)
        axes_layout.addLayout(axes_layout_3)
        axes_layout.addLayout(axes_layout_4)
        axes_layout.addLayout(axes_layout_5)

        # ---- row 7: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/BreadBoard.png">here</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(lenght_layout)
        main_layout.addLayout(width_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class BreadBoard_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.BreadBoard = BreadBoard_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.BreadBoard)
        self.form = [self.BreadBoard.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        length = self.BreadBoard.len.value()
        width = self.BreadBoard.wid.value()
        pos = FreeCAD.Vector(self.BreadBoard.pos_x.value(), self.BreadBoard.pos_y.value(), self.BreadBoard.pos_z.value())
        axis_w = FreeCAD.Vector(self.BreadBoard.axis_w_x.value(),self.BreadBoard.axis_w_y.value(),self.BreadBoard.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.BreadBoard.axis_h_x.value(),self.BreadBoard.axis_h_y.value(),self.BreadBoard.axis_h_z.value())
        
        if fc_isperp(axis_w,axis_h) == 1:
            f_breadboard(kcomp_optic.BREAD_BOARD_M,
                                    length,
                                    width,
                                    cl = 1,
                                    cw = 1,
                                    ch = 1,
                                    fc_dir_h = axis_h ,#VZ,
                                    fc_dir_w = axis_w ,#VY,
                                    pos = pos,
                                    name = 'breadboard')
            
            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")
        else:
            axis_message()

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
            set_place(self.BreadBoard, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.BreadBoard,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('BreadBoard',_BreadBoard_Cmd())