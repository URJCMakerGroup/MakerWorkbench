import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from filter_holder_clss_new import PartFilterHolder
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

import kcomp
__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _FilterHolder_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(FilterHolder_Dialog())

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Filter Holder',
            'Filter Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a Filter Holder')
        return {
            'Pixmap': __dir__ + '/../icons/Filter_Holder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class FilterHolder_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Filter Holder options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- row 0: Filter Length ----
        self.Filter_Length_Label = QtWidgets.QLabel("Filter Length")
        self.Filter_Length_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Length_Value.setValue(60)
        self.Filter_Length_Value.setSuffix(' mm')

        Length_layout = QtWidgets.QHBoxLayout()
        Length_layout.addWidget(self.Filter_Length_Label)
        Length_layout.addWidget(self.Filter_Length_Value)

        
        # ---- row 1: Filter Width ----
        self.Filter_Width_Label = QtWidgets.QLabel("Filter Width")
        self.Filter_Width_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Width_Value.setValue(25)
        self.Filter_Width_Value.setSuffix(' mm')

        Width_layout = QtWidgets.QHBoxLayout()
        Width_layout.addWidget(self.Filter_Width_Label)
        Width_layout.addWidget(self.Filter_Width_Value)

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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3','4','5','6','7','8','9','10','11','12'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3','4','5','6','7'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2','3','4','5','6','7','8','9'])
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

        # ---- row 11: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/FilterHolder.png">here</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(Length_layout)
        main_layout.addLayout(Width_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class FilterHolder_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.FilterHolder = FilterHolder_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.FilterHolder)
        self.form = [self.FilterHolder.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Filter_Length = self.FilterHolder.Filter_Length_Value.value()
        Filter_Width = self.FilterHolder.Filter_Width_Value.value()
        pos = FreeCAD.Vector(self.FilterHolder.pos_x.value(), self.FilterHolder.pos_y.value(), self.FilterHolder.pos_z.value())
        positions_d = [0,1,2,3,4,5,6,7,8,9,10,11,12]
        positions_w = [0,1,2,3,4,5,6,7]
        positions_h = [0,1,2,3,4,5,6,7,8,9]
        pos_d = positions_d[self.FilterHolder.pos_d.currentIndex()]
        pos_w = positions_w[self.FilterHolder.pos_w.currentIndex()]
        pos_h = positions_h[self.FilterHolder.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.FilterHolder.axis_d_x.value(),self.FilterHolder.axis_d_y.value(),self.FilterHolder.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.FilterHolder.axis_w_x.value(),self.FilterHolder.axis_w_y.value(),self.FilterHolder.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.FilterHolder.axis_h_x.value(),self.FilterHolder.axis_h_y.value(),self.FilterHolder.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            PartFilterHolder(filter_l = Filter_Length, #60     
                            filter_w = Filter_Width, #25
                            filter_t = 2.5,
                            base_h = 6.,
                            hold_d = 10.,
                            filt_supp_in = 2.,
                            filt_rim = 3.,
                            filt_cen_d = 30,
                            fillet_r = 1.,
                            # linear guides SEBLV16 y SEBS15, y MGN12H:
                            boltcol1_dist = 20/2.,
                            boltcol2_dist = 12.5, #thorlabs breadboard distance
                            boltcol3_dist = 25,
                            boltrow1_h = 0,
                            boltrow1_2_dist = 12.5,
                            # linear guide MGN12H
                            boltrow1_3_dist = 20.,
                            # linear guide SEBLV16 and SEBS15
                            boltrow1_4_dist = 25.,

                            bolt_cen_mtr = 4, 
                            bolt_linguide_mtr = 3, # linear guide bolts 

                            beltclamp_t = 3.,
                            beltclamp_l = 12.,
                            beltclamp_h = 8.,
                            clamp_post_dist = 4.,
                            sm_beltpost_r = 1.,

                            tol = kcomp.TOL,
                            axis_d = axis_d,#VX,
                            axis_w = axis_w,#VY,
                            axis_h = axis_h,#VZ,
                            pos_d = pos_d,
                            pos_w = pos_w,
                            pos_h = pos_h,
                            pos = pos,
                            model_type = 0, # exact
                            name = 'filter_holder')
            
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
            set_place(self.FilterHolder, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.FilterHolder,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Filter_Holder',_FilterHolder_Cmd())