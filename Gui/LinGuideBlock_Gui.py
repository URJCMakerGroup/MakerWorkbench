import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from comps_new import PartLinGuideBlock 
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _LinGuideBlockCmd:
    """
    This class create Linear Guide Block
    """
    def Activated(self):
        FreeCADGui.Control.showDialog(LinGuideBlock_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Linear Guide Block',
            'Linear Guide Block')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/../icons/LinGuideBlock_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class LinGuideBlock_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Linear Guide Block options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Size ----
        self.Label_block = QtWidgets.QLabel("Type:")
        self.block_dict = QtWidgets.QComboBox()
        self.block_dict.addItems(["SEBW16","SEB15A","SEB8","SEB10"])
        self.block_dict.setCurrentIndex(0)

        size_layout = QtWidgets.QHBoxLayout()
        size_layout.addWidget(self.Label_block)
        size_layout.addWidget(self.block_dict)

        # ---- row 1: Position ----
        self.label_position = QtWidgets.QLabel("Position ")
        self.label_position.setAlignment(QtCore.Qt.AlignTop)

        # pos:
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
        self.pos_d.addItems(['0','1','2','3'])
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
        self.pos_h.addItems(['0','1','2','3','4'])
        self.pos_h.setCurrentIndex(1)

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
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/LinearGuideBlock.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(size_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class LinGuideBlock_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.LinGuideBlock = LinGuideBlock_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.LinGuideBlock)
        self.form = [self.LinGuideBlock.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        dict_block = {0: kcomp.SEBWM16_B, 1: kcomp.SEB15A_B, 2: kcomp.SEB8_B, 3: kcomp.SEB10_B}
        dict_rail = {0: kcomp.SEBWM16_R, 1: kcomp.SEB15A_R, 2: kcomp.SEB8_R, 3: kcomp.SEB10_R}
        block_dict = dict_block[self.LinGuideBlock.block_dict.currentIndex()]
        rail_dict = dict_rail[self.LinGuideBlock.block_dict.currentIndex()]
        
        positions_d = [0,1,2,3]
        positions_w = [0,1,2,3,4]
        positions_h = [0,1,2,3,4]
        pos_d = positions_d[self.LinGuideBlock.pos_d.currentIndex()]
        pos_w = positions_w[self.LinGuideBlock.pos_w.currentIndex()]
        pos_h = positions_h[self.LinGuideBlock.pos_h.currentIndex()]
        pos = FreeCAD.Vector(self.LinGuideBlock.pos_x.value(),self.LinGuideBlock.pos_y.value(),self.LinGuideBlock.pos_z.value())
        axis_d = FreeCAD.Vector(self.LinGuideBlock.axis_d_x.value(),self.LinGuideBlock.axis_d_y.value(),self.LinGuideBlock.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.LinGuideBlock.axis_w_x.value(),self.LinGuideBlock.axis_w_y.value(),self.LinGuideBlock.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.LinGuideBlock.axis_h_x.value(),self.LinGuideBlock.axis_h_y.value(),self.LinGuideBlock.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            PartLinGuideBlock(block_dict, rail_dict,
                                    axis_d = axis_d ,#VX, 
                                    axis_w = axis_w ,#V0, 
                                    axis_h = axis_h ,#VZ,
                                    pos_d = pos_d, pos_w = pos_w, pos_h = pos_h,
                                    pos = pos,
                                    model_type = 1, # dimensional model
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
            set_place(self.LinGuideBlock, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.LinGuideBlock,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Linear_Guide_Block',_LinGuideBlockCmd())