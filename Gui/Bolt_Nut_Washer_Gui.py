import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from fc_clss_new import Din912Bolt, Din934Nut, Din125Washer, Din9021Washer 
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _Bolt_Cmd:
    """
    This class create Bolts, Nuts & Washers with diferents metrics
    """
    def Activated(self):
        FreeCADGui.Control.showDialog(Bolt_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Bolts, Nuts & Washers',
            'Bolts, Nuts & Washers')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/../icons/Bolt_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class Bolt_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Bolt, Nut and Whaser options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Type ----
        self.Type_select_Label = QtWidgets.QLabel("Type")  
        self.Type_text = ["Bolt D912", "Nut D934", "Whasher DIN 125", "Whasher DIN 9021"]
        self.Type_select = QtWidgets.QComboBox()
        self.Type_select.addItems(self.Type_text)
        self.Type_select.setCurrentIndex(0)
        self.Type_select.currentTextChanged.connect(self.changeLayout)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Type_select_Label)
        type_layout.addWidget(self.Type_select)

        # ---- Metric ----
        self.Bolt_Metric_Label = QtWidgets.QLabel("Metric")  
        self.Bolt_metric = ["3","4","5","6"]
        self.metric = QtWidgets.QComboBox()
        self.metric.addItems(self.Bolt_metric)
        self.metric.setCurrentIndex(0)

        metric_layout = QtWidgets.QHBoxLayout()
        metric_layout.addWidget(self.Bolt_Metric_Label)
        metric_layout.addWidget(self.metric)

        # ---- Length ----
        self.length_Label = QtWidgets.QLabel("Length for bolt")  
        self.length_bolt = QtWidgets.QDoubleSpinBox()
        self.length_bolt.setValue(20)
        self.length_bolt.setSuffix(' mm')
        self.length_bolt.setMinimum(4) 

        length_layout = QtWidgets.QHBoxLayout()
        length_layout.addWidget(self.length_Label)
        length_layout.addWidget(self.length_bolt)

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

        # # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2','3','4','5','6','7'])
        self.pos_h.setCurrentIndex(0)
        
        placement_layout_2.addWidget(self.Label_pos_h)
        placement_layout_3.addWidget(self.pos_h)

        # ---- Axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
        self.Label_axis.setAlignment(QtCore.Qt.AlignTop)
        self.Label_axis_h = QtWidgets.QLabel("h:")
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
        axes_layout_2.addWidget(self.Label_axis_h)

        axes_layout_3 = QtWidgets.QVBoxLayout()
        axes_layout_3.addWidget(self.axis_h_x)

        axes_layout_4 = QtWidgets.QVBoxLayout()
        axes_layout_4.addWidget(self.axis_h_y)

        axes_layout_5 = QtWidgets.QVBoxLayout()
        axes_layout_5.addWidget(self.axis_h_z)

        axes_layout.addLayout(axes_layout_1)
        axes_layout.addLayout(axes_layout_2)
        axes_layout.addLayout(axes_layout_3)
        axes_layout.addLayout(axes_layout_4)
        axes_layout.addLayout(axes_layout_5)

        # ---- row 9: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/Bolt_Nut_Washer.png">here</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(metric_layout)
        main_layout.addLayout(length_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

    def changeLayout(self):
        if self.Type_select.currentIndex() == 0: #Bolt D912
            self.length_bolt.setEnabled(True)
            self.pos_d.clear()
            self.pos_w.clear()
            self.pos_h.clear()
            self.pos_d.setEnabled(True)
            self.pos_w.setEnabled(True)
            self.pos_d.addItems(['0','1','2'])
            self.pos_w.addItems(['0','1','2'])
            self.pos_h.addItems(['0','1','2','3','4','5','6','7'])
        elif self.Type_select.currentIndex() == 1: #Nut D934
            self.pos_d.clear()
            self.pos_w.clear()
            self.pos_h.clear()
            self.pos_d.setEnabled(True)
            self.pos_w.setEnabled(True)
            self.pos_d.addItems(['0','1','2','3'])
            self.pos_w.addItems(['0','1','2','3'])
            self.pos_h.addItems(['0','-1','1','-2','2'])
        elif self.Type_select.currentIndex() == 2: #Whasher DIN 125
            self.pos_d.clear()
            self.pos_w.clear()
            self.pos_h.clear()
            self.pos_d.setEnabled(False)
            self.pos_w.setEnabled(False)
            self.pos_h.addItems(['0','1'])
        elif self.Type_select.currentIndex() == 2: #Whasher DIN 9021
            self.pos_d.clear()
            self.pos_w.clear()
            self.pos_h.clear()
            self.pos_d.setEnabled(False)
            self.pos_w.setEnabled(False)
            self.pos_h.addItems(['0','1'])

class Bolt_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.Bolt = Bolt_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.Bolt)
        self.form = [self.Bolt.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)
        
        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        metric = {0: 3,
                  1: 4,
                  2: 5,
                  3: 6}
        metric = metric[self.Bolt.metric.currentIndex()]
        Type_sel = self.Bolt.Type_text[self.Bolt.Type_select.currentIndex()]
        length = self.Bolt.length_bolt.value()

        axis_h = FreeCAD.Vector(self.Bolt.axis_h_x.value(),self.Bolt.axis_h_y.value(),self.Bolt.axis_h_z.value())

        pos = FreeCAD.Vector(self.Bolt.pos_x.value(), self.Bolt.pos_y.value(), self.Bolt.pos_z.value())

        # Chose the data in function of the type selected
        if Type_sel == "Bolt D912":
            posd = [0,1,2,3]
            posw = [0,1,2,3]
            posh = [0,1,2,3,4,5,6,7]
            pos_d = posd[self.Bolt.pos_d.currentIndex()]
            pos_w = posw[self.Bolt.pos_w.currentIndex()]
            pos_h = posh[self.Bolt.pos_h.currentIndex()]
            Din912Bolt(metric,
                               shank_l = length,
                               shank_l_adjust = 0,
                               shank_out = 0,
                               head_out = 0,
                               axis_h = axis_h, axis_d = None, axis_w = None,
                               pos_h = pos_h, pos_d = pos_d, pos_w = pos_w,
                               pos = pos,
                               model_type = 0,
                               name = None)

        elif Type_sel == "Nut D934":
            posd = [0,1,2,3]
            posw = [0,1,2,3]
            posh = [0,-1,1,-2,2]
            pos_d = posd[self.Bolt.pos_d.currentIndex()]
            pos_w = posw[self.Bolt.pos_w.currentIndex()]
            pos_h = posh[self.Bolt.pos_h.currentIndex()]
            Din934Nut(metric = metric,
                              axis_d_apo = 0, 
                              h_offset = 0,
                              axis_h = axis_h,
                              axis_d = None,
                              axis_w = None,
                              pos_h = pos_h, pos_d = pos_d, pos_w = pos_w,
                              pos = pos,
                              name = None)

        elif Type_sel == "Whasher DIN 125":
            pos_h = self.Bolt.pos_h.currentIndex()
            Din125Washer(metric,
                                 axis_h = axis_h, 
                                 pos_h = pos_h, 
                                 tol = 0,
                                 pos = pos,
                                 model_type = 0, # exact
                                 name = None)

        else : #Type_sel == "Whasher DIN 9021"
            pos_h = self.Bolt.pos_h.currentIndex()
            Din9021Washer(metric,
                                  axis_h = axis_h, 
                                  pos_h = pos_h, 
                                  tol = 0,
                                  pos = pos,
                                  model_type = 0, # exact
                                  name = None)
            
            # If there are other types of bolts it could be there

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
            set_place(self.Bolt, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.Bolt,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Bolts, Nuts & Washers',_Bolt_Cmd())  
