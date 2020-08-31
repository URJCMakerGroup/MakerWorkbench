import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from comps import Sk_dir
import comps_new
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _SkDir_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(SK_Dialog())

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Sk',
            'Sk')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Sk',
            'Create a Sk')
        return {
            'Pixmap': __dir__ + '/../icons/Sk_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class Sk_Dir_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Sk options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget.setLayout(main_layout)

        # ---- Size ----
        self.Size_Label = QtWidgets.QLabel("Size:")
        self.Size_ComboBox = QtWidgets.QComboBox()
        self.Size_text = ["6","8","10","12"]
        self.Size_ComboBox.addItems(self.Size_text)
        self.Size_ComboBox.setCurrentIndex(0)
        size_layout = QtWidgets.QHBoxLayout()
        size_layout.addWidget(self.Size_Label)
        size_layout.addWidget(self.Size_ComboBox)
        
        # ---- Pillow ----
        self.Pillow_Label = QtWidgets.QLabel("Pillow:")
        self.Pillow_ComboBox = QtWidgets.QComboBox()
        self.V_Pillow = ["No","Yes"]
        self.Pillow_ComboBox.addItems(self.V_Pillow)
        self.Pillow_ComboBox.setCurrentIndex(self.V_Pillow.index('No'))
        if self.Size_ComboBox.currentText() == "8":
            self.Pillow_ComboBox.setEnabled(True)
        else:self.Pillow_ComboBox.setEnabled(False)

        pillow_layout = QtWidgets.QHBoxLayout()
        pillow_layout.addWidget(self.Pillow_Label)
        pillow_layout.addWidget(self.Pillow_ComboBox)


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

        placement_layout.addLayout(placement_layout_1)
        placement_layout.addLayout(placement_layout_2)
        placement_layout.addLayout(placement_layout_3)

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['-1','0','1'])
        self.pos_w.setCurrentIndex(1)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1'])
        self.pos_h.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_h)
        placement_layout_3.addWidget(self.pos_h)

        # ---- Axes ----
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
        self.axis_d_y.setValue(0)
        self.axis_d_z.setValue(1)
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
        self.axis_h_x.setValue(1)
        self.axis_h_y.setValue(0)
        self.axis_h_z.setValue(0)

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
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/SK_dir.png">hear</a>.')
        image.setOpenExternalLinks(True)
        # svgimage = QtSvg.QSvgWidget(":/img_gui/SK_dir.svg") # TODO No carga la imagen
        # svgimage.renderer()

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)
        # image_layout.addWidget(svgimage)

        main_layout.addLayout(size_layout)
        main_layout.addLayout(pillow_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

class SK_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.Sk = Sk_Dir_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.Sk)
        self.form = [self.Sk.widget, self.Advance.widget]

        self.Sk.Size_ComboBox.currentTextChanged.connect(self.change_layout)
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Size_Value = {0:6, 1:8, 2:10, 3:12}
        Values_Pillow = {0: 0, 1: 1}
        TOL_Value = {0: 0.4, 1: 0.7}
        Size = Size_Value[self.Sk.Size_ComboBox.currentIndex()]
        Pillow = Values_Pillow[self.Sk.Pillow_ComboBox.currentIndex()]
        Tol = TOL_Value[self.Sk.Pillow_ComboBox.currentIndex()]
        pos = FreeCAD.Vector(self.Sk.pos_x.value(), self.Sk.pos_y.value(), self.Sk.pos_z.value())
        positions_d = [0,1]
        positions_w = [-1,0,1]
        positions_h = [0,1]
        pos_d = positions_d[self.Sk.pos_d.currentIndex()]
        pos_w = positions_w[self.Sk.pos_w.currentIndex()]
        pos_h = positions_h[self.Sk.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.Sk.axis_d_x.value(),self.Sk.axis_d_y.value(),self.Sk.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.Sk.axis_w_x.value(),self.Sk.axis_w_y.value(),self.Sk.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.Sk.axis_h_x.value(),self.Sk.axis_h_y.value(),self.Sk.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if Pillow == 0 or (Pillow == 1 and Size == 8): # Pillow only exist for size 8.
                
                comps_new.Sk_dir(size = Size,
                                fc_axis_h = axis_h,
                                fc_axis_d = axis_d,
                                fc_axis_w = axis_w,
                                pos_h = pos_h,
                                pos_w = pos_w,
                                pos_d = pos_d,
                                pillow = Pillow,
                                pos = pos,
                                tol = Tol,#0.7, # for the pillow block
                                wfco = 1,
                                name= "shaft" + str(Size) + "_holder")

                FreeCADGui.activeDocument().activeView().viewAxonometric() #Axonometric view
                FreeCADGui.SendMsgToActiveView("ViewFit") #Fit the view to the object
                FreeCADGui.Control.closeDialog() #close the dialog

            elif Pillow == 1 and Size != 8:
                message = QtWidgets.QMessageBox()
                message.setText("This Size don't have Pillow option")
                message.setStandardButtons(QtWidgets.QMessageBox.Ok)
                message.setDefaultButton(QtWidgets.QMessageBox.Ok)
                message.exec_()
        # else: axis_message 
        
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
            set_place(self.Sk, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.Sk,pos.x,pos.y,pos.z)
            except Exception: None

    def change_layout(self):
        if self.Sk.Size_ComboBox.currentText() == "8":
            self.Sk.Pillow_ComboBox.setEnabled(True)
        else: self.Sk.Pillow_ComboBox.setEnabled(False)
    
# Command
FreeCADGui.addCommand('Sk',_SkDir_Cmd())