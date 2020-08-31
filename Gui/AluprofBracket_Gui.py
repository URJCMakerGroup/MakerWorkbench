import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import logging

from parts import AluProfBracketPerp, AluProfBracketPerpFlap, AluProfBracketPerpTwin
from Gui.Advance_Placement_Gui import Advance_Placement_TaskPanel
from Gui.function_Gui import set_place, ortonormal_axis
__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

maxnum =  1e10000
minnum = -1e10000

class _AluprofBracket_Cmd:
    def Activated(self):
        FreeCADGui.Control.showDialog(AluprofBracket_Dialog())
    
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Aluprof Bracket',
            'Aluprof Bracket')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Aluprof Bracket',
            'Create an Aluprof Bracket')
        return {
            'Pixmap': __dir__ + '/../icons/AluprofBracket_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class AluprofBracket_TaskPanel:
    def __init__(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Aluminium profile Bracket options")
        main_layout = QtWidgets.QVBoxLayout(self.widget)

        # ---- Type ----
        self.Type_Label = QtWidgets.QLabel("Select Type:")
        self.Type_Aluprof = ["2 profiles","2 profiles with flap","3 profiles"]
        self.Type_ComboBox = QtWidgets.QComboBox()
        self.Type_Aluprof = ["2 profiles","2 profiles with flap","3 profiles"]
        self.Type_ComboBox.addItems(self.Type_Aluprof)
        self.Type_ComboBox.setCurrentIndex(0)
        self.Type_ComboBox.currentTextChanged.connect(self.change_layout)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Type_Label)
        type_layout.addWidget(self.Type_ComboBox)
    
        # ---- Size profile line 1 ----
        self.Size_1_Label = QtWidgets.QLabel("Size first profile:")
        self.Size_1_ComboBox = QtWidgets.QComboBox()
        self.Size_text = ["10mm","15mm","20mm","30mm","40mm"]         ##Select profiles kcomp
        self.Size_1_ComboBox.addItems(self.Size_text)
        self.Size_1_ComboBox.setCurrentIndex(self.Size_text.index('20mm'))

        size_layout_1 = QtWidgets.QHBoxLayout()
        size_layout_1.addWidget(self.Size_1_Label)
        size_layout_1.addWidget(self.Size_1_ComboBox)
        
        # ---- Size profile line 2 ----
        self.Size_2_Label = QtWidgets.QLabel("Size second profile:")
        self.Size_2_ComboBox = QtWidgets.QComboBox()
        self.Size_2_ComboBox.addItems(self.Size_text)
        self.Size_2_ComboBox.setCurrentIndex(self.Size_text.index('20mm'))

        size_layout_2 = QtWidgets.QHBoxLayout()
        size_layout_2.addWidget(self.Size_2_Label)
        size_layout_2.addWidget(self.Size_2_ComboBox)
        
        # ---- Thikness ----
        self.Thikness_Label = QtWidgets.QLabel("Thikness:")
        self.Thikness_Value = QtWidgets.QDoubleSpinBox()
        self.Thikness_Value.setValue(3)
        self.Thikness_Value.setMinimum(2)
        self.Thikness_Value.setSuffix(' mm')

        thikness_layout = QtWidgets.QHBoxLayout()
        thikness_layout.addWidget(self.Thikness_Label)
        thikness_layout.addWidget(self.Thikness_Value)
        
        # ---- Nut profile line 1 ----
        self.Nut_Profile_1_Label = QtWidgets.QLabel("Size of Nut first profile :")
        self.Nut_Profile_1_ComboBox = QtWidgets.QComboBox()
        self.NUT_text = ["M3","M4","M5","M6"]    #D912
        self.Nut_Profile_1_ComboBox.addItems(self.NUT_text)
        self.Nut_Profile_1_ComboBox.setCurrentIndex(0)

        nut_layout_1 = QtWidgets.QHBoxLayout()
        nut_layout_1.addWidget(self.Nut_Profile_1_Label)
        nut_layout_1.addWidget(self.Nut_Profile_1_ComboBox)
        
        # ---- Nut profile line 2 ----
        self.Nut_Profile_2_Label = QtWidgets.QLabel("Size of Nut second profile :")
        self.Nut_Profile_2_ComboBox = QtWidgets.QComboBox()
        self.Nut_Profile_2_ComboBox.addItems(self.NUT_text)
        self.Nut_Profile_2_ComboBox.setCurrentIndex(0)

        nut_layout_2 = QtWidgets.QHBoxLayout()
        nut_layout_2.addWidget(self.Nut_Profile_2_Label)
        nut_layout_2.addWidget(self.Nut_Profile_2_ComboBox)

        # ---- Nº Nut ----
        self.N_Nut_Label = QtWidgets.QLabel("Number of Nuts:")
        self.N_Nut_ComboBox = QtWidgets.QComboBox()
        self.N_Nut_text = ["1","2"]
        self.N_Nut_ComboBox.addItems(self.N_Nut_text)
        self.N_Nut_ComboBox.setCurrentIndex(0)

        n_nut_layout = QtWidgets.QHBoxLayout()
        n_nut_layout.addWidget(self.N_Nut_Label)
        n_nut_layout.addWidget(self.N_Nut_ComboBox)

        # ---- Dist Nut ----
        self.Dist_Nut_Label = QtWidgets.QLabel("Distance between nuts:")
        self.Dist_Nut_Label2 = QtWidgets.QLabel("(0 = min distance)")
        self.Dist_Nut_Value = QtWidgets.QDoubleSpinBox()
        self.Dist_Nut_Value.setValue(0)
        self.Dist_Nut_Value.setMinimum(0)
        self.Dist_Nut_Value.setSuffix(' mm')

        dist_nut_layout = QtWidgets.QHBoxLayout()
        dist_nut_layout_1 = QtWidgets.QVBoxLayout()
        dist_nut_layout_2 = QtWidgets.QVBoxLayout()
        dist_nut_layout_1.addWidget(self.Dist_Nut_Label)
        dist_nut_layout_1.addWidget(self.Dist_Nut_Label2)
        dist_nut_layout_2.addWidget(self.Dist_Nut_Value)

        dist_nut_layout.addLayout(dist_nut_layout_1)
        dist_nut_layout.addLayout(dist_nut_layout_2)
        
        # ---- Sunk ----
        self.Sunk_Label = QtWidgets.QLabel("Sunk:")
        self.Sunk_ComboBox = QtWidgets.QComboBox()
        Sunk_Text = ["Hole fot Nut","Without center","Withput reinforce"]
        self.Sunk_ComboBox.addItems(Sunk_Text)
        self.Sunk_ComboBox.setCurrentIndex(0)
        
        sunk_layout = QtWidgets.QHBoxLayout()
        sunk_layout.addWidget(self.Sunk_Label)
        sunk_layout.addWidget(self.Sunk_ComboBox)

        # ---- Reinforce ----
        self.Reinforce_Label = QtWidgets.QLabel("Reinforce:")
        self.Reinforce_ComboBox = QtWidgets.QComboBox()
        self.Reinforce_text = ["No","Yes"]
        self.Reinforce_ComboBox.addItems(self.Reinforce_text)
        self.Reinforce_ComboBox.setCurrentIndex(0)
        
        reinforce_layout = QtWidgets.QHBoxLayout()
        reinforce_layout.addWidget(self.Reinforce_Label)
        reinforce_layout.addWidget(self.Reinforce_ComboBox)

        # ---- Flap ----
        self.Flap_Label = QtWidgets.QLabel("Flap:")
        self.Flap_ComboBox = QtWidgets.QComboBox()
        self.Flap_text = ["No","Yes"]
        self.Flap_ComboBox.addItems(self.Flap_text)
        self.Flap_ComboBox.setCurrentIndex(1)

        flap_layout = QtWidgets.QHBoxLayout()
        flap_layout.addWidget(self.Flap_Label)
        flap_layout.addWidget(self.Flap_ComboBox)

        # ---- Dist Between Profiles ----
        self.Dist_Prof_Label = QtWidgets.QLabel("Dist between profiles:")
        self.Dist_Prof_Value = QtWidgets.QDoubleSpinBox()
        self.Dist_Prof_Value.setValue(26)
        self.Dist_Prof_Value.setMinimum(26)
        self.Dist_Prof_Value.setSuffix(' mm')

        Dist_Layout = QtWidgets.QHBoxLayout()
        Dist_Layout.addWidget(self.Dist_Prof_Label)
        Dist_Layout.addWidget(self.Dist_Prof_Value)

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
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic_Documentation/master/img_gui/AluprofBracket.png">hear</a>.')
        image.setOpenExternalLinks(True)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(size_layout_1)
        main_layout.addLayout(size_layout_2)
        main_layout.addLayout(thikness_layout)
        main_layout.addLayout(nut_layout_1)
        main_layout.addLayout(nut_layout_2)
        main_layout.addLayout(dist_nut_layout)
        main_layout.addLayout(sunk_layout)
        main_layout.addLayout(reinforce_layout)
        main_layout.addLayout(flap_layout)
        main_layout.addLayout(Dist_Layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)

        if self.Type_ComboBox.currentIndex() == 0:
            self.Reinforce_ComboBox.setEnabled(True)
            self.Flap_ComboBox.setEnabled(False)
            self.Dist_Prof_Value.setEnabled(False)

    def change_layout(self):
        if self.Type_ComboBox.currentIndex() == 0:
            self.Reinforce_ComboBox.setEnabled(True)
            self.Flap_ComboBox.setEnabled(False)
            self.Dist_Prof_Value.setEnabled(False)
        elif self.Type_ComboBox.currentIndex() == 1:
            self.Reinforce_ComboBox.setEnabled(False)
            self.Flap_ComboBox.setEnabled(True)
            self.Dist_Prof_Value.setEnabled(False)
        elif self.Type_ComboBox.currentIndex() == 2:
            self.Reinforce_ComboBox.setEnabled(False)
            self.Flap_ComboBox.setEnabled(False)
            self.Dist_Prof_Value.setEnabled(True)

class AluprofBracket_Dialog:
    def __init__(self):
        self.placement = True
        self.v = FreeCAD.Gui.ActiveDocument.ActiveView

        self.AluprofBracket = AluprofBracket_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.AluprofBracket)
        self.form = [self.AluprofBracket.widget, self.Advance.widget]
    
        # Event to track the mouse 
        self.track = self.v.addEventCallback("SoEvent",self.position)

    def accept(self):
        self.v.removeEventCallback("SoEvent",self.track)

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        NUT = {0:3, 1:4, 2:5, 3:6}
        Size = {0: 10, 1: 15, 2: 20, 3: 30, 4: 40}
        Sunk_values = {0:0, 1:1, 2:2}
        Size_1 = Size[self.AluprofBracket.Size_1_ComboBox.currentIndex()]
        Size_2 = Size[self.AluprofBracket.Size_2_ComboBox.currentIndex()]
        Thikness = self.AluprofBracket.Thikness_Value.value()
        Nut_Prof_1 = NUT[self.AluprofBracket.Nut_Profile_1_ComboBox.currentIndex()]
        Nut_Prof_2 = NUT[self.AluprofBracket.Nut_Profile_2_ComboBox.currentIndex()]
        NumberNut = 1+self.AluprofBracket.N_Nut_ComboBox.currentIndex()
        Dist_Nut = self.AluprofBracket.Dist_Nut_Value.value()
        Sunk = Sunk_values[self.AluprofBracket.Sunk_ComboBox.currentIndex()]
        self.Type = self.AluprofBracket.Type_ComboBox.currentIndex()
        pos = FreeCAD.Vector(self.AluprofBracket.pos_x.value(), self.AluprofBracket.pos_y.value(), self.AluprofBracket.pos_z.value())
        axis_d = FreeCAD.Vector(self.AluprofBracket.axis_d_x.value(),self.AluprofBracket.axis_d_y.value(),self.AluprofBracket.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.AluprofBracket.axis_w_x.value(),self.AluprofBracket.axis_w_y.value(),self.AluprofBracket.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.AluprofBracket.axis_h_x.value(),self.AluprofBracket.axis_h_y.value(),self.AluprofBracket.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if self.Type == 0:
                Reinforce = self.AluprofBracket.Reinforce_ComboBox.currentIndex()
                AluProfBracketPerp(alusize_lin = Size_1, alusize_perp = Size_2, #cambiar a combobox
                                    br_perp_thick = Thikness,
                                    br_lin_thick = Thikness,
                                    bolt_lin_d = Nut_Prof_1,
                                    bolt_perp_d = Nut_Prof_2,
                                    nbolts_lin = NumberNut,
                                    bolts_lin_dist = Dist_Nut,
                                    bolts_lin_rail = Dist_Nut,
                                    xtr_bolt_head = 0,
                                    xtr_bolt_head_d = 0, # space for the nut
                                    reinforce = Reinforce,
                                    fc_perp_ax = axis_h,
                                    fc_lin_ax = axis_d,
                                    pos = pos,
                                    wfco=1,
                                    name = 'bracket2_perp')
            elif self.Type == 1:
                Flap = self.AluprofBracket.Flap_ComboBox.currentIndex()
                AluProfBracketPerpFlap(alusize_lin = Size_1, alusize_perp = Size_2,
                                        br_perp_thick = Thikness,
                                        br_lin_thick = Thikness,
                                        bolt_lin_d = Nut_Prof_1,
                                        bolt_perp_d = Nut_Prof_2,
                                        nbolts_lin = NumberNut,
                                        bolts_lin_dist = Dist_Nut,
                                        bolts_lin_rail = Dist_Nut,
                                        xtr_bolt_head = 1,
                                        sunk = Sunk,
                                        flap = Flap, 
                                        fc_perp_ax = axis_h,
                                        fc_lin_ax = axis_d,
                                        pos = pos,
                                        wfco=1,
                                        name = 'bracket3_flap')
            elif self.Type ==2:
                Dis_Prof = self.AluprofBracket.Dist_Prof_Value.value()
                AluProfBracketPerpTwin(alusize_lin = Size_1, alusize_perp = Size_2,
                                        alu_sep = Dis_Prof,
                                        br_perp_thick = Thikness,
                                        br_lin_thick = Thikness,
                                        bolt_lin_d = Nut_Prof_1,
                                        bolt_perp_d = Nut_Prof_2,
                                        nbolts_lin = NumberNut,
                                        bolts_lin_dist = Dist_Nut,
                                        bolts_lin_rail = Dist_Nut,
                                        bolt_perp_line = 0,
                                        xtr_bolt_head = 2, 
                                        sunk = Sunk,
                                        fc_perp_ax = axis_h,
                                        fc_lin_ax = axis_d,
                                        fc_wide_ax = axis_w,
                                        pos = pos,
                                        wfco=1,
                                        name = 'bracket_twin')

            FreeCADGui.activeDocument().activeView().viewAxonometric() #Axonometric view
            FreeCADGui.SendMsgToActiveView("ViewFit") #Fit the view to the object
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
            set_place(self.AluprofBracket, round(self.v.getPoint(pos)[0],3), round(self.v.getPoint(pos)[1],3), round(self.v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self.AluprofBracket,pos.x,pos.y,pos.z)
            except Exception: None

# Command
FreeCADGui.addCommand('Aluprof_Bracket',_AluprofBracket_Cmd())