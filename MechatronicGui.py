# -*- coding: utf-8 -*-
# FreeCAD script for the commands of the mechatronic workbench
# (c) 2019 David Muñoz Bernal

#***************************************************************************
#*   (c) David Muñoz Bernal                                                *
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/

import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui
import Draft
import logging

import comps, comp_optic
from fcfun import V0, VX, VY, VZ, VZN, fc_isperp
import parts
import kcomp, kcomp_optic
import partset
import beltcl
from filter_stage_fun import filter_stage_fun
import tensioner_clss
import filter_holder_clss
import fc_clss
from print_export_fun import print_export

from parts import AluProfBracketPerp, AluProfBracketPerpFlap, AluProfBracketPerpTwin, PartNemaMotorHolder, ThinLinBearHouse1rail

import grafic

import NuevaClase

import tensioner_clss_new

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if FreeCAD.Gui.ActiveDocument == None:
    FreeCAD.newDocument()
else:
    pass

v = FreeCAD.Gui.ActiveDocument.ActiveView

maxnum =  1e10000
minnum = -1e10000
#  _________________________________________________________________
# |                                                                 |
# |                               SK                                |
# |_________________________________________________________________|

class _SkDirCmd:
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
            'Pixmap': __dir__ + '/icons/Sk_cmd.svg',
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
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/SK_dir.png">hear</a>.')
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

        self.Sk = Sk_Dir_TaskPanel()
        self.Advance = Advance_Placement_TaskPanel(self.Sk)
        self.form = [self.Sk.widget, self.Advance.widget]

        self.Sk.Size_ComboBox.currentTextChanged.connect(self.change_layout)
    
        # Event to track the mouse 
        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

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
                comps.Sk_dir(size = Size,
                            fc_axis_h = axis_h,
                            fc_axis_d = axis_d,
                            fc_axis_w = axis_w,
                            ref_hr = pos_h,
                            ref_wc = pos_w,
                            ref_dc = pos_d,
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
        v.removeEventCallback("SoEvent",self.track)
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
            set_place(self.Sk, round(v.getPoint(pos)[0],3), round(v.getPoint(pos)[1],3), round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                set_place(self,pos.x,pos.y,pos.z)
            except Exception: None

    def change_layout(self):
        if self.Sk.Size_ComboBox.currentText() == "8":
            self.Sk.Pillow_ComboBox.setEnabled(True)
        else: self.Sk.Pillow_ComboBox.setEnabled(False)
    
def set_place(self,x,y,z):
    self.pos_x.setValue(x)
    self.pos_y.setValue(y)
    self.pos_z.setValue(z)

class Advance_Placement_TaskPanel:
    def __init__(self,obj_task):
        self.obj_task = obj_task

        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Advance Placement")
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget.setLayout(main_layout)

        obj_layout = QtWidgets.QHBoxLayout()
        obj_label = QtWidgets.QLabel()
        obj_label.setText("Select Object")
        self.obj_combo = QtWidgets.QComboBox()
        self.obj_combo.addItem('') #add initial null value

        obj_layout.addWidget(obj_label)
        obj_layout.addWidget(self.obj_combo)


        points_layout = QtWidgets.QHBoxLayout()
        points_layout_1 = QtWidgets.QVBoxLayout()
        points_layout_2 = QtWidgets.QVBoxLayout()
        
        obj_d_label = QtWidgets.QLabel()
        obj_d_label.setText("Point in d_o")
        obj_w_label = QtWidgets.QLabel()
        obj_w_label.setText("Point in w_o")
        obj_h_label = QtWidgets.QLabel()
        obj_h_label.setText("Point in h_o")

        self.obj_d = QtWidgets.QComboBox()
        self.obj_w = QtWidgets.QComboBox()
        self.obj_h = QtWidgets.QComboBox()

        points_layout_1.addWidget(obj_d_label)
        points_layout_1.addWidget(obj_w_label)
        points_layout_1.addWidget(obj_h_label)
        points_layout_2.addWidget(self.obj_d)
        points_layout_2.addWidget(self.obj_w)
        points_layout_2.addWidget(self.obj_h)

        points_layout.addLayout(points_layout_1)
        points_layout.addLayout(points_layout_2)

        button_layout = QtWidgets.QHBoxLayout()
        btn_setpos = QtWidgets.QPushButton("Set this position to the model")
        btn_point = QtWidgets.QPushButton("Show point")
        button_layout.addWidget(btn_setpos)
        button_layout.addWidget(btn_point)
        # Connect the button 
        btn_setpos.clicked.connect(self.button_clicked) 
        btn_point.clicked.connect(self.show_point) 

        for obj in FreeCAD.ActiveDocument.Objects: # Save the objects name
            self.obj_combo.addItem(obj.Name)

        self.obj_combo.currentTextChanged.connect(self.set_points)

        main_layout.addLayout(obj_layout)
        main_layout.addLayout(points_layout)
        main_layout.addLayout(button_layout)
    
    def set_points(self):
        obj = FreeCAD.ActiveDocument.Objects[self.obj_combo.currentIndex()-1]

        if hasattr(obj, "d_o"):
            if obj.d0_cen == 0:
                for p in range(0,len(obj.d_o)):
                    self.obj_d.addItem(str(p))
            elif obj.d0_cen == 1:
                for p in range(-len(obj.d_o)+1,len(obj.d_o)): # +1 is necessary to eliminate the 0 value duplicate
                    self.obj_d.addItem(str(p)) 
        else:
            print("The object didn't have the attribute d_o")
        if hasattr(obj, "w_o"):
            if obj.w0_cen == 0:
                for p in range(0,len(obj.w_o)):
                    self.obj_w.addItem(str(p))
            elif obj.w0_cen == 1:
                for p in range(-len(obj.w_o)+1,len(obj.w_o)):
                    self.obj_w.addItem(str(p))
        else:
            print("The object didn't have the attribute w_o")
        if hasattr(obj, "h_o"):
            if obj.h0_cen == 0:
                for p in range(0,len(obj.h_o)):
                    self.obj_h.addItem(str(p))
            elif obj.h0_cen == 1:
                for p in range(-len(obj.h_o)+1,len(obj.h_o)):
                    self.obj_h.addItem(str(p))
        else:
            print("The object didn't have the attribute h_o")

    def button_clicked(self):
        obj_selected = FreeCAD.ActiveDocument.Objects[self.obj_combo.currentIndex()-1]
        set_place(self.obj_task, obj_selected.d_o[int(self.obj_d.currentText())].x, obj_selected.w_o[int(self.obj_w.currentText())].y, obj_selected.h_o[int(self.obj_h.currentText())].z)

    def show_point(self):
        obj_selected = FreeCAD.ActiveDocument.Objects[self.obj_combo.currentIndex()-1]
        d = self.obj_d.currentText()
        w = self.obj_w.currentText()
        h = self.obj_h.currentText()

        if '-' in d:
            point_x = obj_selected.Placement.Base.x - obj_selected.d_o[abs(int((d)))].x
        else: 
            point_x = obj_selected.Placement.Base.x + obj_selected.d_o[int((d))].x

        if '-' in w:
            point_y = obj_selected.Placement.Base.y - obj_selected.w_o[abs(int((w)))].y
        else: 
            point_y = obj_selected.Placement.Base.y + obj_selected.w_o[int((w))].y

        if '-' in h:
            point_z = obj_selected.Placement.Base.z - obj_selected.h_o[abs(int((h)))].z
        else: 
            point_z = obj_selected.Placement.Base.z + obj_selected.h_o[int((h))].z

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Draft.makePoint(X=point_x, Y=point_y, Z=point_z, name='Point_d_w_h', point_size=10, color=(0,1,0))
        print('Point_d_w_h in place (' + str(point_x) + ',' + str(point_y) + ',' + str(point_z) + ')' )
        FreeCAD.ActiveDocument.recompute()
#  _________________________________________________________________
# |                                                                 |
# |                        Idle Pulley Holder                       |
# |_________________________________________________________________|

class _IdlePulleyHolderCmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Idle Pulley Holder options")
        panel = IdlePulleyHolder_TaskPanel(baseWidget)

        FreeCADGui.Control.showDialog(panel)
    
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Idle Pulley Holder',
            'Idle Pulley Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Idle Pulley Holder',
            'Create an Idle Pulley Holder')
        return {
            'Pixmap': __dir__ + '/icons/IdlePulleyHolder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class IdlePulleyHolder_TaskPanel:
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)

        self.placement = True

        # ---- Aluprof ----
        self.ALuprof_Label = QtWidgets.QLabel("Aluminium profile:")
        self.Aluprof_ComboBox = QtWidgets.QComboBox()
        self.Aluprof_Str = ["20mm","30mm"]
        self.Aluprof_ComboBox.addItems(self.Aluprof_Str)
        self.Aluprof_ComboBox.setCurrentIndex(0)

        aluprof_layout = QtWidgets.QHBoxLayout()
        aluprof_layout.addWidget(self.ALuprof_Label)
        aluprof_layout.addWidget(self.Aluprof_ComboBox)


        # ---- Nut Bolt ----
        self.NutBolt_Label = QtWidgets.QLabel("Nut bolt:")
        self.NutBolt_Str = ["2.5","3","4","5","6"]
        self.NutBolt_ComboBox = QtWidgets.QComboBox()
        self.NutBolt_ComboBox.addItems(self.NutBolt_Str)
        self.NutBolt_ComboBox.setCurrentIndex(3)

        bolt_layout = QtWidgets.QHBoxLayout()
        bolt_layout.addWidget(self.NutBolt_Label)
        bolt_layout.addWidget(self.NutBolt_ComboBox)
        
        # ---- High to profile ----
        self.HighToProfile_Label = QtWidgets.QLabel("High to profile:")
        self.HighToProfile_Value = QtWidgets.QDoubleSpinBox()
        self.HighToProfile_Value.setValue(40)
        self.HighToProfile_Value.setSuffix(' mm')

        high_layout = QtWidgets.QHBoxLayout()
        high_layout.addWidget(self.HighToProfile_Label)
        high_layout.addWidget(self.HighToProfile_Value)

        # ---- End Stop Side ----
        self.EndSide_Label = QtWidgets.QLabel("End Stop Side:")
        self.EndSide_ComboBox = QtWidgets.QComboBox()
        self.EndSide_Str = ["1","0","-1"]
        self.EndSide_ComboBox.addItems(self.EndSide_Str)
        self.EndSide_ComboBox.setCurrentIndex(1)

        EndSide_layout = QtWidgets.QHBoxLayout()
        EndSide_layout.addWidget(self.EndSide_Label)
        EndSide_layout.addWidget(self.EndSide_ComboBox)

        # ---- End Stop High ----
        self.EndStopHigh_Label = QtWidgets.QLabel("End Stop Pos:")
        self.EndStopHigh_Value = QtWidgets.QDoubleSpinBox()
        self.EndStopHigh_Value.setValue(0)
        self.EndStopHigh_Value.setSuffix(' mm')

        EndHigh_layout = QtWidgets.QHBoxLayout()
        EndHigh_layout.addWidget(self.EndStopHigh_Label)
        EndHigh_layout.addWidget(self.EndStopHigh_Value)

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


        main_layout.addLayout(aluprof_layout)
        main_layout.addLayout(bolt_layout)
        main_layout.addLayout(high_layout)
        main_layout.addLayout(EndSide_layout)
        main_layout.addLayout(EndHigh_layout)
        main_layout.addLayout(placement_layout)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):

        v.removeEventCallback("SoEvent",self.track)

        self.Aluprof_values = {0: 20, 1:30}
        self.NutBolt_values = {0:2.5, 1:3, 2:4, 3:5, 4:6}
        self.EndSide_values = {0:1, 1:0, 2:-1}
        Aluprof = self.Aluprof_values[self.Aluprof_ComboBox.currentIndex()]
        NutBolt = self.NutBolt_values[self.NutBolt_ComboBox.currentIndex()]
        High = self.HighToProfile_Value.value()
        EndSide = self.EndSide_values[self.EndSide_ComboBox.currentIndex()]
        EndHigh = self.EndStopHigh_Value.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())

        parts.IdlePulleyHolder( profile_size= Aluprof, #20.,#
                                pulleybolt_d=3.,
                                holdbolt_d = NutBolt, #5,#
                                above_h = High, #40,#
                                mindepth = 0,
                                attach_dir = '-y',
                                endstop_side = EndSide, #0,
                                endstop_posh = EndHigh, #0,  
                                pos = pos,
                                name = "idlepulleyhold")
        
        FreeCADGui.activeDocument().activeView().viewAxonometric() #Axonometric view
        FreeCADGui.SendMsgToActiveView("ViewFit") #Fit the view to the object
        FreeCADGui.Control.closeDialog() #close the dialog

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                      Simple End Stop Holder                     |
# |_________________________________________________________________|

class _SimpleEndStopHolderCmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Simple End Stop Holder options")
        panel = SimpleEndStopHolder_TaskPanel(baseWidget)

        FreeCADGui.Control.showDialog(panel)
    
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Simple End Stop Holder',
            'Simple End Stop Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Simple End Stop Holder',
            'Create a Simple End Stop Holder')
        return {
            'Pixmap': __dir__ + '/icons/SimpleEndStopHolder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
class SimpleEndStopHolder_TaskPanel:
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)

        self.placement = True

        # ---- Type ----
        self.Type_Label = QtWidgets.QLabel("Type:")
        self.Type_ComboBox = QtWidgets.QComboBox()
        Type_text = ["A","B","D3V"]
        self.Type_ComboBox.addItems(Type_text)
        self.Type_ComboBox.setCurrentIndex(0)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.Type_Label)
        type_layout.addWidget(self.Type_ComboBox)

        # ---- Rail ---- 
        self.Rail_Label = QtWidgets.QLabel("Rail Length:")
        self.Rail_Value = QtWidgets.QDoubleSpinBox()
        self.Rail_Value.setValue(15)
        self.Rail_Value.setSuffix(' mm')

        rail_layout = QtWidgets.QHBoxLayout()
        rail_layout.addWidget(self.Rail_Label)
        rail_layout.addWidget(self.Rail_Value)

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
        self.pos_d.addItems(['1','2','3','4','5'])
        self.pos_d.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_d)
        placement_layout_3.addWidget(self.pos_d)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['1','2','3','4'])
        self.pos_w.setCurrentIndex(0)

        placement_layout_2.addWidget(self.Label_pos_w)
        placement_layout_3.addWidget(self.pos_w)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['1','2'])
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

        # ---- Image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/SimpleEndstopHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(rail_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        Type_values = {0:kcomp.ENDSTOP_A, 1:kcomp.ENDSTOP_B, 2:kcomp.ENDSTOP_D3V}
        Type = Type_values[self.Type_ComboBox.currentIndex()]
        Rail_L = self.Rail_Value.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        positions_d = [1,2,3,4,5]
        positions_w = [1,2,3,4]
        positions_h = [1,2]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            parts.SimpleEndstopHolder(d_endstop = Type,
                                    rail_l = Rail_L,
                                    base_h = 5.,
                                    h = 0,
                                    holder_out = 2.,
                                    #csunk = 1,
                                    mbolt_d = 3.,
                                    endstop_nut_dist = 0.,
                                    min_d = 0,
                                    fc_axis_d = VX,
                                    fc_axis_w = V0,
                                    fc_axis_h = VZ,
                                    ref_d = pos_d,
                                    ref_w = pos_w,
                                    ref_h = pos_h,
                                    pos = pos,
                                    wfco = 1,
                                    name = 'simple_endstop_holder')
            
            FreeCADGui.activeDocument().activeView().viewAxonometric() #Axonometric view
            FreeCADGui.SendMsgToActiveView("ViewFit") #Fit the view to the object
            FreeCADGui.Control.closeDialog() #close the dialog

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                         Aluprof Bracket                         |
# |_________________________________________________________________|

class _AluprofBracketCmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Aluminium profile Bracket options")
        panel = AluprofBracket_TaskPanel(baseWidget)

        FreeCADGui.Control.showDialog(panel)
    
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Aluprof Bracket',
            'Aluprof Bracket')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Aluprof Bracket',
            'Create an Aluprof Bracket')
        return {
            'Pixmap': __dir__ + '/icons/AluprofBracket_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class AluprofBracket_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        main_layout = QtWidgets.QVBoxLayout(self.form)

        self.placement = True

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
        
        # ---- Thickness ----
        self.Thickness_Label = QtWidgets.QLabel("Thickness:")
        self.Thickness_Value = QtWidgets.QDoubleSpinBox()
        self.Thickness_Value.setValue(3)
        self.Thickness_Value.setMinimum(2)
        self.Thickness_Value.setSuffix(' mm')

        thickness_layout = QtWidgets.QHBoxLayout()
        thickness_layout.addWidget(self.Thickness_Label)
        thickness_layout.addWidget(self.Thickness_Value)
        
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
        Sunk_Text = ["Hole for Nut","Without center","Without reinforce"]
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
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/AluprofBracket.png">hear</a>.')
        image.setOpenExternalLinks(True)

        main_layout.addLayout(type_layout)
        main_layout.addLayout(size_layout_1)
        main_layout.addLayout(size_layout_2)
        main_layout.addLayout(thickness_layout)
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

        self.track = v.addEventCallback("SoEvent",self.position)

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

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        NUT = {0:3, 1:4, 2:5, 3:6}
        Size = {0: 10, 1: 15, 2: 20, 3: 30, 4: 40}
        Sunk_values = {0:0, 1:1, 2:2}
        Size_1 = Size[self.Size_1_ComboBox.currentIndex()]
        Size_2 = Size[self.Size_2_ComboBox.currentIndex()]
        Thickness = self.Thickness_Value.value()
        Nut_Prof_1 = NUT[self.Nut_Profile_1_ComboBox.currentIndex()]
        Nut_Prof_2 = NUT[self.Nut_Profile_2_ComboBox.currentIndex()]
        NumberNut = 1+self.N_Nut_ComboBox.currentIndex()
        Dist_Nut = self.Dist_Nut_Value.value()
        Sunk = Sunk_values[self.Sunk_ComboBox.currentIndex()]
        self.Type = self.Type_ComboBox.currentIndex()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if self.Type == 0:
                Reinforce = self.Reinforce_ComboBox.currentIndex()
                parts.AluProfBracketPerp( alusize_lin = Size_1, alusize_perp = Size_2, #cambiar a combobox
                                        br_perp_thick = Thickness,
                                        br_lin_thick = Thickness,
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
                Flap = self.Flap_ComboBox.currentIndex()
                parts.AluProfBracketPerpFlap(alusize_lin = Size_1, alusize_perp = Size_2,
                                            br_perp_thick = Thickness,
                                            br_lin_thick = Thickness,
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
                Dis_Prof = self.Dist_Prof_Value.value()
                parts.AluProfBracketPerpTwin(alusize_lin = Size_1, alusize_perp = Size_2,
                                            alu_sep = Dis_Prof,
                                            br_perp_thick = Thickness,
                                            br_lin_thick = Thickness,
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
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                           Motor Holder                          |
# |_________________________________________________________________|

class _MotorHolderCmd:
    
    def Activated(self):
        Widget_MotorHolder = QtWidgets.QWidget()
        Widget_MotorHolder.setWindowTitle("Motor Holder options")
        Panel_MotorHolder = MotorHolderTaskPanel(Widget_MotorHolder)
        FreeCADGui.Control.showDialog(Panel_MotorHolder) 
        

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Motor Holder',
            'Motor Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Motor Holder',
            'Creates a Motor Holder')
        return {
            'Pixmap': __dir__ + '/icons/Motor_Holder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class MotorHolderTaskPanel:
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)

        self.placement = True

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

        # ---- Thickness ----
        self.Thickness_Label = QtWidgets.QLabel("Thickness:")
        self.Thickness_Value = QtWidgets.QDoubleSpinBox()
        self.Thickness_Value.setValue(3)
        self.Thickness_Value.setMinimum(2)
        self.Thickness_Value.setSuffix(' mm')

        thik_layout = QtWidgets.QHBoxLayout()
        thik_layout.addWidget(self.Thickness_Label)
        thik_layout.addWidget(self.Thickness_Value)

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

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        SizeHolder = {0:8, 1:11, 2:14, 3:17, 4:23, 5:34, 6:42}
        self.size_motor = SizeHolder[self.ComboBox_Size_Holder.currentIndex()]
        h_motor=self.motor_high_Value.value()
        Thickness = self.Thickness_Value.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        pos_h = self.pos_h.currentIndex()
        pos_d = self.pos_d.currentIndex()
        pos_w = self.pos_w.currentIndex()
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            parts.PartNemaMotorHolder(nema_size = self.size_motor,
                                    wall_thick = Thickness,
                                    motorside_thick = Thickness,
                                    reinf_thick = Thickness,
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
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                           Nema  Motor                           |
# |_________________________________________________________________|

class _NemaMotorCmd:
    def Activated(self):
        Widget_NemaMotor = QtWidgets.QWidget()
        Widget_NemaMotor.setWindowTitle("Nema Motor options")
        Panel_NemaMotor = NemaMotorTaskPanel(Widget_NemaMotor)
        FreeCADGui.Control.showDialog(Panel_NemaMotor) 
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Nema Motor',
            'Nema Motor')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Nema Motor',
            'Creates a Motor')
        return {
            'Pixmap': __dir__ + '/icons/NemaMotor_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class NemaMotorTaskPanel:
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)
        
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

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        dict_size = {0: 8, 1: 11, 2: 14, 3: 17, 5: 23, 6: 34, 7: 42}
        size = dict_size[self.Size.currentIndex()]
        base_h = self.Height.value()
        shaft_l = self.shaft_h.value()
        shaft_r = self.shaft_r.value()
        shaft_br = self.shaft_br.value()
        shaft_hr = self.shaft_bh.value()
        chmf_r = self.chmf_r.value()
        bolt_d = self.bolt_d.value()
        pitch = self.pulley_pitch.value()
        teeth = self.pulley_teeth.value()
        top_flan = self.pulley_top_flan.value()
        bot_flan = self.pulley_bot_flan.value()
        positions_d = [0,1,2,3,4]
        positions_w = [0,1,2,3,4]
        positions_h = [0,1,2,3,4,5]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(),self.pos_y.value(),self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            partset.NemaMotorPulleySet(nema_size = size,
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
                                    name = '')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                        Linear Bear House                        |
# |_________________________________________________________________|

class _LinBearHouseCmd:
    def Activated(self):
        Widget_LinBearHouse = QtWidgets.QWidget()
        Widget_LinBearHouse.setWindowTitle("Linear Bear House options")
        Panel_LinBearHouse = LinBearHouseTaskPanel(Widget_LinBearHouse)
        FreeCADGui.Control.showDialog(Panel_LinBearHouse) 
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Linear Bear House',
            'Linear Bear House')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Linear Bear House',
            'Creates a Linear Bear House')
        return {
            'Pixmap': __dir__ + '/icons/Thin_Linear_Bear_House_1Rail_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class LinBearHouseTaskPanel:
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)
        self.placement = True

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
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/LinearBearHouse.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(version_layout)
        main_layout.addLayout(type_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

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

        LinBearHouse = self.LinBearHouse_ComboBox.currentIndex()
        Type = Type_values[self.Type_ComboBox.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if LinBearHouse == 0:
                parts.ThinLinBearHouse1rail(d_lbear = Type,
                                            fc_slide_axis = axis_d, #VX
                                            fc_bot_axis =axis_h, #VZN
                                            axis_center = 1,
                                            mid_center  = 1,
                                            pos = pos,
                                            name = 'thinlinbearhouse1rail')
            elif LinBearHouse == 1:
                parts.ThinLinBearHouse(d_lbear = Type,
                                    fc_slide_axis = axis_d, #VX
                                    fc_bot_axis =axis_h, #VZN
                                    fc_perp_axis = V0,
                                    axis_h = 0,
                                    bolts_side = 1,
                                    axis_center = 1,
                                    mid_center  = 1,
                                    bolt_center  = 0,
                                    pos = pos,
                                    name = 'thinlinbearhouse')
            elif LinBearHouse == 2:
                parts.LinBearHouse(d_lbearhousing = Type, #SC only
                                fc_slide_axis = axis_d, #VX
                                fc_bot_axis =axis_h, #VZN
                                axis_center = 1,
                                mid_center  = 1,
                                pos = pos,
                                name = 'linbearhouse')

            else:
                parts.ThinLinBearHouseAsim(d_lbear = Type,
                                        fc_fro_ax = VX,
                                        fc_bot_ax =VZN,
                                        fc_sid_ax = V0,
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
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                           Stop Holder                           |
# |_________________________________________________________________|

class _stop_holderCmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Stop Holder options")
        panel = stop_holderTaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel)

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Stop Holder',
            'Stop Holder')
        ToolTip =QtCore.QT_TRANSLATE_NOOP(
            'Stop Holder',
            'Creates Stop Holder with set parametres')
        return {
            'Pixmap': __dir__ + '/icons/Stop_Holder.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class stop_holderTaskPanel:
    def __init__(self, widget):
        self.form = widget
        main_layout = QtWidgets.QVBoxLayout(self.form)

        self.placement = True

        # ---- Width ----
        self.Width_Label = QtWidgets.QLabel("Width:")
        self.Width_Value = QtWidgets.QDoubleSpinBox()
        self.Width_Value.setValue(21)
        self.Width_Value.setSuffix("mm")

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.Width_Label)
        width_layout.addWidget(self.Width_Value)

        # ---- Height ----
        self.Heigth_Label = QtWidgets.QLabel("Height:")
        self.Heigth_Value = QtWidgets.QDoubleSpinBox()
        self.Heigth_Value.setValue(31)
        self.Heigth_Value.setSuffix("mm")

        height_layout = QtWidgets.QHBoxLayout()
        height_layout.addWidget(self.Heigth_Label)
        height_layout.addWidget(self.Heigth_Value)

        # ---- Thickness ----
        self.Thickness_Label = QtWidgets.QLabel("Thickness:")
        self.Thickness_Value = QtWidgets.QDoubleSpinBox()
        self.Thickness_Value.setValue(4)
        self.Thickness_Value.setSuffix("mm")

        
        thickness_layout = QtWidgets.QHBoxLayout()
        thickness_layout.addWidget(self.Thickness_Label)
        thickness_layout.addWidget(self.Thickness_Value)

        # ---- Metric Bolt ----
        self.Bolt_Label = QtWidgets.QLabel("Metric Bolt")
        self.Bolt_ComboBox = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.Bolt_ComboBox.addItems(self.TextNutType)
        self.Bolt_ComboBox.setCurrentIndex(self.TextNutType.index('M3'))

        bolt_layout = QtWidgets.QHBoxLayout()
        bolt_layout.addWidget(self.Bolt_Label)
        bolt_layout.addWidget(self.Bolt_ComboBox)

        # ---- Rail ----
        self.Rail_Label = QtWidgets.QLabel("Rail Size:")
        self.Rail_ComboBox = QtWidgets.QComboBox()
        self.Rail_ComboBox.addItems(["10mm","20mm","30mm"])
        self.Rail_ComboBox.setCurrentIndex(0)

        rail_layout = QtWidgets.QHBoxLayout()
        rail_layout.addWidget(self.Rail_Label)
        rail_layout.addWidget(self.Rail_ComboBox)

        # ---- Reinforce ----
        self.Reinforce_Label = QtWidgets.QLabel("Reinforce:")
        self.Reinforce_ComboBox = QtWidgets.QComboBox()
        self.Reinforce_ComboBox.addItems(["No","Yes"])
        self.Reinforce_ComboBox.setCurrentIndex(1)

        reinforce_layout = QtWidgets.QHBoxLayout()
        reinforce_layout.addWidget(self.Reinforce_Label)
        reinforce_layout.addWidget(self.Reinforce_ComboBox)

        # ---- placement ----
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
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/StopHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        image_layout = QtWidgets.QHBoxLayout()
        image_layout.addWidget(image)

        main_layout.addLayout(width_layout)
        main_layout.addLayout(height_layout)
        main_layout.addLayout(thickness_layout)
        main_layout.addLayout(bolt_layout)
        main_layout.addLayout(rail_layout)
        main_layout.addLayout(reinforce_layout)
        main_layout.addLayout(placement_layout)
        main_layout.addLayout(axes_layout)
        main_layout.addLayout(image_layout)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        Width = self.Width_Value.value()
        Height = self.Heigth_Value.value()
        Thick = self.Thickness_Value.value()
        Bolt_values = {0: 3,
                       1: 4,
                       2: 5,
                       3: 6}
        Bolt = Bolt_values[self.Bolt_ComboBox.currentIndex()]
        Rail_values = {0: 10,
                       1: 20,
                       2: 30}
        Rail = Rail_values[self.Rail_ComboBox.currentIndex()]
        Reinforce_values = {0: 0, #No
                            1: 1}#Yes
        Reinforce = Reinforce_values[self.Reinforce_ComboBox.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            parts.hallestop_holder(stp_w = Width,
                                stp_h = Height,
                                base_thick = Thick,
                                sup_thick = Thick,
                                bolt_base_d = Bolt, #metric of the bolt 
                                bolt_sup_d = Bolt, #metric of the bolt
                                bolt_sup_sep = 17.,  # fixed value
                                alu_rail_l = Rail,
                                stp_rail_l = Rail,
                                xtr_bolt_head = 3,
                                xtr_bolt_head_d = 0,
                                reinforce = Reinforce,
                                base_min_dist = 1,
                                fc_perp_ax = axis_h,#VZ,
                                fc_lin_ax = axis_d, #VX,
                                pos = pos,
                                wfco=1,
                                name = 'stop_holder')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.SendMsgToActiveView("ViewFit")
            FreeCADGui.Control.closeDialog() #close the dialog
        
    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                          Filter Stage                           |
# |_________________________________________________________________|

class _FilterStageCmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Filter Holder options")
        panel = FilterStageTaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel)

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Filter_Stage_',
            'Filter Stage')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Filter_Stage',
            'Creates a Filter Stage with set parametres')
        return {
            'Pixmap': __dir__ + '/icons/Filter_Stage_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class FilterStageTaskPanel:                                    
    def __init__(self, widget):
        self.form = widget

        main_layout = QtWidgets.QVBoxLayout(self.form)
        self.placement = True

        # ---- Move distance ----
        self.move_l_Label = QtWidgets.QLabel("Move distance:")
        self.move_l_Value = QtWidgets.QDoubleSpinBox()
        self.move_l_Value.setValue(60)
        self.move_l_Value.setSuffix(' mm')

        move_layout = QtWidgets.QHBoxLayout()
        move_layout.addWidget(self.move_l_Label)
        move_layout.addWidget(self.move_l_Value)

        # ---- Filter Length ----
        self.Filter_Length_Label = QtWidgets.QLabel("Filter Length")
        self.Filter_Length_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Length_Value.setValue(60)
        self.Filter_Length_Value.setSuffix(' mm')

        length_layout = QtWidgets.QHBoxLayout()
        length_layout.addWidget(self.Filter_Length_Label)
        length_layout.addWidget(self.Filter_Length_Value)

        # ---- Filter Width ----
        self.Filter_Width_Label = QtWidgets.QLabel("Filter Width")
        self.Filter_Width_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Width_Value.setValue(25)
        self.Filter_Width_Value.setSuffix(' mm')

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(self.Filter_Width_Label)
        width_layout.addWidget(self.Filter_Width_Value)

        # ---- Base width ----
        self.base_w_Label = QtWidgets.QLabel("Base width:")  #10/15/20/30/40
        self.ComboBox_base_w = QtWidgets.QComboBox()
        self.TextBase_W = ["10mm","15mm","20mm","30mm","40mm"] 
        self.ComboBox_base_w.addItems(self.TextBase_W)
        self.ComboBox_base_w.setCurrentIndex(self.TextBase_W.index('20mm'))

        base_width_layout = QtWidgets.QHBoxLayout()
        base_width_layout.addWidget(self.base_w_Label)
        base_width_layout.addWidget(self.ComboBox_base_w)

        # ---- Tensioner Stroke ----
        self.tens_stroke_Label = QtWidgets.QLabel("Tensioner stroke:")
        self.tens_stroke_Value = QtWidgets.QDoubleSpinBox()
        self.tens_stroke_Value.setValue(20)
        self.tens_stroke_Value.setSuffix(' mm')

        tensioner_layout = QtWidgets.QHBoxLayout()
        tensioner_layout.addWidget(self.tens_stroke_Label)
        tensioner_layout.addWidget(self.tens_stroke_Value)

        # ---- Wall thick ----
        self.wall_th_Label = QtWidgets.QLabel("Wall thick:")
        self.wall_th_Value = QtWidgets.QDoubleSpinBox()
        self.wall_th_Value.setValue(3)
        self.wall_th_Value.setSuffix(' mm')

        wall_layout = QtWidgets.QHBoxLayout()
        wall_layout.addWidget(self.wall_th_Label)
        wall_layout.addWidget(self.wall_th_Value)


        # ---- Nut Type ----
        self.nut_hole_Label = QtWidgets.QLabel("Nut Type:")   
        self.ComboBox_Nut_Hole = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.ComboBox_Nut_Hole.addItems(self.TextNutType)
        self.ComboBox_Nut_Hole.setCurrentIndex(self.TextNutType.index('M3'))

        nut_layout = QtWidgets.QHBoxLayout()
        nut_layout.addWidget(self.nut_hole_Label)
        nut_layout.addWidget(self.ComboBox_Nut_Hole)

        # ---- Size Holder ----
        self.Size_Holder_Label = QtWidgets.QLabel("Motor size")
        self.ComboBox_Size_Holder = QtWidgets.QComboBox()
        self.TextSizeHolder = ["8","11","14","17","23","34","42"]
        self.ComboBox_Size_Holder.addItems(self.TextSizeHolder)
        self.ComboBox_Size_Holder.setCurrentIndex(self.TextSizeHolder.index('14'))

        nema_holder_layout = QtWidgets.QHBoxLayout()
        nema_holder_layout.addWidget(self.Size_Holder_Label)
        nema_holder_layout.addWidget(self.ComboBox_Size_Holder)

        # ---- Rail Max High  ----
        self.motor_high_Label = QtWidgets.QLabel("Rail high Motor holder")
        self.motor_high_Value = QtWidgets.QDoubleSpinBox()
        self.motor_high_Value.setValue(25) #Value printed
        self.motor_high_Value.setSuffix(' mm')

        rail_layout = QtWidgets.QHBoxLayout()
        rail_layout.addWidget(self.motor_high_Label)
        rail_layout.addWidget(self.motor_high_Value)

        # ---- Thickness ----
        self.Thickness_Label = QtWidgets.QLabel("Motor holder thickness:")
        self.Thickness_Value = QtWidgets.QDoubleSpinBox()
        self.Thickness_Value.setValue(3)
        self.Thickness_Value.setMinimum(2)
        self.Thickness_Value.setSuffix(' mm')

        thickness_layout = QtWidgets.QHBoxLayout()
        thickness_layout.addWidget(self.Thickness_Label)
        thickness_layout.addWidget(self.Thickness_Value)

        # ---- Placement ----
        self.label_position = QtWidgets.QLabel("Placement ")
        self.label_pos_x = QtWidgets.QLabel("x:")
        self.label_pos_y = QtWidgets.QLabel("y:")
        self.label_pos_z = QtWidgets.QLabel("z:")
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
        placement_layout_1 = QtWidgets.QBBoxLayout()
        placement_layout_2 = QtWidgets.QVBoxLayout()
        placement_layout_3 = QtWidgets.QVBoxLayout()

        placement_layout.addLayout(placement_layout_1)
        placement_layout.addLayout(placement_layout_2)
        placement_layout.addLayout(placement_layout_3)

        placement_layout_1.addWidget(self.label_position)
        placement_layout_2.addWidget(self.label_pos_x)
        placement_layout_2.addWidget(self.label_pos_y)
        placement_layout_2.addWidget(self.label_pos_z)
        placement_layout_3.addWidget(self.pos_x)
        placement_layout_3.addWidget(self.pos_y)
        placement_layout_3.addWidget(self.pos_z)


        main_layout.addLayout(move_layout)
        main_layout.addLayout(length_layout)
        main_layout.addLayout(width_layout)
        main_layout.addLayout(base_width_layout)
        main_layout.addLayout(tensioner_layout)
        main_layout.addLayout(wall_layout)
        main_layout.addLayout(nut_layout)
        main_layout.addLayout(nema_holder_layout)
        main_layout.addLayout(rail_layout)
        main_layout.addLayout(thickness_layout)
        main_layout.addLayout(placement_layout)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        self.selec_base = {0: 5, 1: 10, 2: 15, 3: 20, 4: 30, 5: 40}
        move_l = self.move_l_Value.value()
        #Filter holder
        Filter_Length = self.Filter_Length_Value.value()
        Filter_Width = self.Filter_Width_Value.value()
        #tensioner
        nut_hole = 3 + self.ComboBox_Nut_Hole.currentIndex()  #Index star in 0, first value = 3
        tens_stroke = self.tens_stroke_Value.value()
        base_w = self.selec_base[self.ComboBox_base_w.currentIndex()]
        wall_thick = self.wall_th_Value.value()
        #motor holder
        SizeHolder = {0:8, 1:11, 2:14, 3:17, 4:23, 5:34, 6:42}
        size_motor = SizeHolder[self.ComboBox_Size_Holder.currentIndex()]
        h_motor=self.motor_high_Value.value()
        thik_motor = self.Thickness_Value.value()

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())

        filter_stage_fun(move_l,Filter_Length,Filter_Width, nut_hole, tens_stroke, base_w, wall_thick, size_motor, h_motor, thik_motor, pos)
            #pulley_h => belt_pos_h
            #nut_hole => bolttens_mtr
            #tens_stroke => tens_stroke_Var
            #base_w => aluprof_w
            #wall_thick => wall_thick_Var
        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.Control.closeDialog() #close the dialog

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                          Filter Holder                          |
# |_________________________________________________________________|

class _FilterHolderCmd:
    def Activated(self):
        Widget_FilterHolder = QtWidgets.QWidget()
        Widget_FilterHolder.setWindowTitle("Filfer Holder options")
        Panel_FilterHolder = FilterHolderTaskPanel(Widget_FilterHolder)
        FreeCADGui.Control.showDialog(Panel_FilterHolder) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Filter Holder',
            'Filter Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a Filter Holder')
        return {
            'Pixmap': __dir__ + '/icons/Filter_Holder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class FilterHolderTaskPanel: # TODO
    def __init__(self, widget):
        self.form = widget
        main_layout = QtWidgets.QVBoxLayout(self.form)

        self.placement = True

        # ---- row 0: Filter Length ----
        self.Filter_Length_Label = QtWidgets.QLabel("Filter Length")
        self.Filter_Length_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Length_Value.setValue(60)
        self.Filter_Length_Value.setSuffix(' mm')


        
        # ---- row 1: Filter Width ----
        self.Filter_Width_Label = QtWidgets.QLabel("Filter Width")
        self.Filter_Width_Value = QtWidgets.QDoubleSpinBox()
        self.Filter_Width_Value.setValue(25)
        self.Filter_Width_Value.setSuffix(' mm')

        # ---- row 2: placement ----
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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3','4','5','6','7','8','9','10','11','12'])
        self.pos_d.setCurrentIndex(0)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3','4','5','6','7'])
        self.pos_w.setCurrentIndex(0)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2','3','4','5','6','7','8','9'])
        self.pos_h.setCurrentIndex(0)

        # ---- row 8: axis ----
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

        # ---- row 11: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/FilterHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Filter_Length_Label,0,0,1,2)
        layout.addWidget(self.Filter_Length_Value,0,1,1,2)

        layout.addWidget(self.Filter_Width_Label,1,0,1,2)
        layout.addWidget(self.Filter_Width_Value,1,1,1,2)

        layout.addWidget(self.Label_position,2,0,1,2)
        layout.addWidget(self.Label_pos_x,2,1,1,2)
        layout.addWidget(self.pos_x,2,2,1,2)
        layout.addWidget(self.Label_pos_y,3,1,1,2)
        layout.addWidget(self.pos_y,3,2,1,2)
        layout.addWidget(self.Label_pos_z,4,1,1,2)
        layout.addWidget(self.pos_z,4,2,1,2)

        layout.addWidget(self.Label_pos_d,5,1,1,2)
        layout.addWidget(self.pos_d,5,2,1,2)
        layout.addWidget(self.Label_pos_w,6,1,1,2)
        layout.addWidget(self.pos_w,6,2,1,2)
        layout.addWidget(self.Label_pos_h,7,1,1,2)
        layout.addWidget(self.pos_h,7,2,1,2)

        layout.addWidget(self.Label_axis,8,0,1,4)
        layout.addWidget(self.Label_axis_d,8,1,1,4)
        layout.addWidget(self.axis_d_x,8,2,1,4)
        layout.addWidget(self.axis_d_y,8,3,1,4)
        layout.addWidget(self.axis_d_z,8,4,1,4)
        layout.addWidget(self.Label_axis_w,9,1,1,4)
        layout.addWidget(self.axis_w_x,9,2,1,4)
        layout.addWidget(self.axis_w_y,9,3,1,4)
        layout.addWidget(self.axis_w_z,9,4,1,4)
        layout.addWidget(self.Label_axis_h,10,1,1,4)
        layout.addWidget(self.axis_h_x,10,2,1,4)
        layout.addWidget(self.axis_h_y,10,3,1,4)
        layout.addWidget(self.axis_h_z,10,4,1,4)

        layout.addWidget(image,11,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        Filter_Length = self.Filter_Length_Value.value()
        Filter_Width = self.Filter_Width_Value.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        positions_d = [0,1,2,3,4,5,6,7,8,9,10,11,12]
        positions_w = [0,1,2,3,4,5,6,7]
        positions_h = [0,1,2,3,4,5,6,7,8,9]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            filter_holder_clss.PartFilterHolder(filter_l = Filter_Length, #60     
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
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                            Tensioner                            |
# |_________________________________________________________________|

class _TensionerCmd:
    
    def Activated(self):
        # what is done when the command is clicked
        # creates a panel with a dialog
        Widget_Tensioner = QtWidgets.QWidget()
        Widget_Tensioner.setWindowTitle("Tensioner options")
        Panel_Tensioner = TensionerTaskPanel(Widget_Tensioner)
        FreeCADGui.Control.showDialog(Panel_Tensioner) 
        

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Tensioner',
            'Tensioner')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Tensioner',
            'Creates a Tensioner')
        return {
            'Pixmap': __dir__ + '/icons/Tensioner_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

class TensionerTaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Belt Height ----
        self.belt_h_Label = QtWidgets.QLabel("Belt height:")
        self.belt_h_Value = QtWidgets.QDoubleSpinBox()
        self.belt_h_Value.setValue(20)
        self.belt_h_Value.setSuffix(' mm')

        # ---- row 1: Base width ----
        self.base_w_Label = QtWidgets.QLabel("Base width:")  #10/15/20/30/40
        self.ComboBox_base_w = QtWidgets.QComboBox()
        self.TextBase_W = ["10mm","15mm","20mm","30mm","40mm"] 
        self.ComboBox_base_w.addItems(self.TextBase_W)
        self.ComboBox_base_w.setCurrentIndex(self.TextBase_W.index('20mm'))
                
        # ---- row 2: Tensioner Stroke ----
        self.tens_stroke_Label = QtWidgets.QLabel("Tensioner stroke:")
        self.tens_stroke_Value = QtWidgets.QDoubleSpinBox()
        self.tens_stroke_Value.setValue(20)
        self.tens_stroke_Value.setSuffix(' mm')

        # ---- row 3: Wall thick ----
        self.wall_th_Label = QtWidgets.QLabel("Wall thick:")
        self.wall_th_Value = QtWidgets.QDoubleSpinBox()
        self.wall_th_Value.setValue(3)
        self.wall_th_Value.setSuffix(' mm')

        # ---- row 4: Nut Type ----
        self.nut_hole_Label = QtWidgets.QLabel("Nut Type:")   
        self.ComboBox_Nut_Hole = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.ComboBox_Nut_Hole.addItems(self.TextNutType)
        self.ComboBox_Nut_Hole.setCurrentIndex(self.TextNutType.index('M3'))

        # ---- row 5: Set Holder ----
        self.Set_Label = QtWidgets.QLabel("See Set")
        self.ComboBox_Set = QtWidgets.QComboBox()
        self.TextSet = ["No","Yes"]
        self.ComboBox_Set.addItems(self.TextSet)
        self.ComboBox_Set.setCurrentIndex(self.TextSet.index('No'))

        # ---- row 6: placement ----
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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3','4','5','6'])
        self.pos_d.setCurrentIndex(0)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2'])
        self.pos_w.setCurrentIndex(0)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2'])
        self.pos_h.setCurrentIndex(0)

        # ---- row 12: axis ----
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
        self.axis_d_x.setValue(0)
        self.axis_d_y.setValue(-1)
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
        self.axis_w_x.setValue(-1)
        self.axis_w_y.setValue(0)
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

        # ---- row 15: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/Tensioner.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.belt_h_Label,0,0,1,2)
        layout.addWidget(self.belt_h_Value,0,1,1,2)

        layout.addWidget(self.base_w_Label,1,0,1,2)
        layout.addWidget(self.ComboBox_base_w,1,1,1,2)

        layout.addWidget(self.tens_stroke_Label,2,0,1,2)
        layout.addWidget(self.tens_stroke_Value,2,1,1,2)

        layout.addWidget(self.wall_th_Label,3,0,1,2)
        layout.addWidget(self.wall_th_Value,3,1,1,2)

        layout.addWidget(self.nut_hole_Label,4,0,1,2)
        layout.addWidget(self.ComboBox_Nut_Hole,4,1,1,2)

        layout.addWidget(self.Set_Label,5,0,1,2)
        layout.addWidget(self.ComboBox_Set,5,1,1,2)

        layout.addWidget(self.Label_position,6,0,1,2)
        layout.addWidget(self.Label_pos_x,6,1,1,2)
        layout.addWidget(self.pos_x,6,2,1,2)
        layout.addWidget(self.Label_pos_y,7,1,1,2)
        layout.addWidget(self.pos_y,7,2,1,2)
        layout.addWidget(self.Label_pos_z,8,1,1,2)
        layout.addWidget(self.pos_z,8,2,1,2)

        layout.addWidget(self.Label_pos_d,9,1,1,2)
        layout.addWidget(self.pos_d,9,2,1,2)
        layout.addWidget(self.Label_pos_w,10,1,1,2)
        layout.addWidget(self.pos_w,10,2,1,2)
        layout.addWidget(self.Label_pos_h,11,1,1,2)
        layout.addWidget(self.pos_h,11,2,1,2)

        layout.addWidget(self.Label_axis,12,0,1,4)
        layout.addWidget(self.Label_axis_d,12,1,1,4)
        layout.addWidget(self.axis_d_x,12,2,1,4)
        layout.addWidget(self.axis_d_y,12,3,1,4)
        layout.addWidget(self.axis_d_z,12,4,1,4)
        layout.addWidget(self.Label_axis_w,13,1,1,4)
        layout.addWidget(self.axis_w_x,13,2,1,4)
        layout.addWidget(self.axis_w_y,13,3,1,4)
        layout.addWidget(self.axis_w_z,13,4,1,4)
        layout.addWidget(self.Label_axis_h,14,1,1,4)
        layout.addWidget(self.axis_h_x,14,2,1,4)
        layout.addWidget(self.axis_h_y,14,3,1,4)
        layout.addWidget(self.axis_h_z,14,4,1,4)

        layout.addWidget(image,15,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        IndexNut = {0:3,1:4,2:5,3:6}
        IndexBase = {0: 10, 1: 15, 2: 20, 3: 30, 4: 40}
        tensioner_belt_h = self.belt_h_Value.value()
        nut_hole = IndexNut[self.ComboBox_Nut_Hole.currentIndex()]
        tens_stroke = self.tens_stroke_Value.value()
        base_w = IndexBase[self.ComboBox_base_w.currentIndex()]
        wall_thick = self.wall_th_Value.value()
        Set_Select = self.ComboBox_Set.currentIndex()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        positions_d = [0,1,2,3,4,5,6]
        positions_w = [0,1,2]
        positions_h = [0,1,2]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            tensioner_clss.TensionerSet(aluprof_w = base_w,#20.,
                                        belt_pos_h = tensioner_belt_h, 
                                        hold_bas_h = 0,
                                        hold_hole_2sides = 1,
                                        boltidler_mtr = 3,
                                        bolttens_mtr = nut_hole,   #métrica del tensor
                                        boltaluprof_mtr = nut_hole,
                                        tens_stroke = tens_stroke ,
                                        wall_thick = wall_thick,
                                        in_fillet = 2.,
                                        pulley_stroke_dist = 0,
                                        nut_holder_thick = nut_hole ,   
                                        opt_tens_chmf = 0,
                                        min_width = 0,
                                        tol = kcomp.TOL,
                                        axis_d = axis_d,#VY.negative(),
                                        axis_w = axis_w,#VX.negative(),
                                        axis_h = axis_h,#VZ,
                                        pos_d = pos_d,
                                        pos_w = pos_w,
                                        pos_h = pos_h,
                                        pos = pos,
                                        name = 'tensioner_set')
            if Set_Select == 0: #work only for tens_stroke = 20
                FreeCAD.ActiveDocument.removeObject("bearing_idlpulley_m3")
                FreeCAD.ActiveDocument.removeObject("idlpull_bearing")
                FreeCAD.ActiveDocument.removeObject("idlpull_rwash_bt")
                FreeCAD.ActiveDocument.removeObject("idlpull_lwash_bt")
                FreeCAD.ActiveDocument.removeObject("idlpull_rwash_tp")
                FreeCAD.ActiveDocument.removeObject("idlpull_lwash_tp")
                FreeCAD.ActiveDocument.removeObject("d912bolt_washer_m3")
                FreeCAD.ActiveDocument.removeObject("din125_washer_m3")  
                FreeCAD.ActiveDocument.removeObject("leadscrew_nut")
                FreeCAD.ActiveDocument.removeObject("d9343")
                FreeCAD.ActiveDocument.removeObject("d934nut_m3")
                FreeCAD.ActiveDocument.removeObject("d912bolt_m3_l20")
                if nut_hole == 3:
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m3001")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_m3_l30")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_washer_m"  + str(int(nut_hole)) + "001")
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m" + str(int(nut_hole)) + "002")  
                elif nut_hole == 4:
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m3001")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_m4_l35")
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m4")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_washer_m4")
                elif nut_hole == 5:  
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m3001")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_m5_l40")
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m5")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_washer_m5")
                else: 
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m3001")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_m6_l40")
                    FreeCAD.ActiveDocument.removeObject("din125_washer_m6")
                    FreeCAD.ActiveDocument.removeObject("d912bolt_washer_m6")

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.SendMsgToActiveView("ViewFit")
            FreeCADGui.Control.closeDialog() #close the dialog
    
    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                           Belt Clamp                            |
# |_________________________________________________________________|

class _BeltClampCmd:
    def Activated(self):
        Widget_BeltClamp = QtWidgets.QWidget()
        Widget_BeltClamp.setWindowTitle("Belt Clamp options")
        Panel_BeltClamp = BeltClampTaskPanel(Widget_BeltClamp)
        FreeCADGui.Control.showDialog(Panel_BeltClamp)     
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Belt clamp')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a belt clamp')
        return {
            'Pixmap': __dir__ + '/icons/Double_Belt_Clamp_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class BeltClampTaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Type ----
        self.Type_Label = QtWidgets.QLabel("Type:")   

        self.Type_ComboBox = QtWidgets.QComboBox()
        self.TextType = ["Simple","Double"]
        self.Type_ComboBox.addItems(self.TextType)
        self.Type_ComboBox.setCurrentIndex(0)

        # ---- row 1: Length ----
        self.Length_Label = QtWidgets.QLabel("Length:")
        self.Length_Value = QtWidgets.QDoubleSpinBox()
        self.Length_Value.setValue(42)
        self.Length_Value.setSuffix(' mm')
        self.Length_Value.setMinimum(42)

        # ---- row 2: Width ----
        self.Width_Label = QtWidgets.QLabel("Width:")
        self.Width_Value = QtWidgets.QDoubleSpinBox()
        self.Width_Value.setValue(10.8)
        self.Width_Value.setSuffix(' mm')
        self.Width_Value.setMinimum(10.8)

        # ---- row 3: Nut Type ----
        self.nut_hole_Label = QtWidgets.QLabel("Nut Type:")   
        self.ComboBox_Nut_Hole = QtWidgets.QComboBox()
        self.TextNutType = ["M3","M4","M5","M6"]
        self.ComboBox_Nut_Hole.addItems(self.TextNutType)
        self.ComboBox_Nut_Hole.setCurrentIndex(self.TextNutType.index('M3'))

        # ---- row 4: placement ----
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

        # ---- row 7: axis ----
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

        # ---- row 10: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/BeltClamp.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Type_Label,0,0,1,2)
        layout.addWidget(self.Type_ComboBox,0,1,1,2)

        layout.addWidget(self.Length_Label,1,0,1,2)
        layout.addWidget(self.Length_Value,1,1,1,2)

        layout.addWidget(self.Width_Label,2,0,1,2)
        layout.addWidget(self.Width_Value,2,1,1,2)

        layout.addWidget(self.nut_hole_Label,3,0,1,2)
        layout.addWidget(self.ComboBox_Nut_Hole,3,1,1,2)

        layout.addWidget(self.Label_position,4,0,1,2)
        layout.addWidget(self.Label_pos_x,4,1,1,2)
        layout.addWidget(self.pos_x,4,2,1,2)
        layout.addWidget(self.Label_pos_y,5,1,1,2)
        layout.addWidget(self.pos_y,5,2,1,2)
        layout.addWidget(self.Label_pos_z,6,1,1,2)
        layout.addWidget(self.pos_z,6,2,1,2)

        layout.addWidget(self.Label_axis,7,0,1,4)
        layout.addWidget(self.Label_axis_d,7,1,1,4)
        layout.addWidget(self.axis_d_x,7,2,1,4)
        layout.addWidget(self.axis_d_y,7,3,1,4)
        layout.addWidget(self.axis_d_z,7,4,1,4)
        layout.addWidget(self.Label_axis_w,8,1,1,4)
        layout.addWidget(self.axis_w_x,8,2,1,4)
        layout.addWidget(self.axis_w_y,8,3,1,4)
        layout.addWidget(self.axis_w_z,8,4,1,4)
        layout.addWidget(self.Label_axis_h,9,1,1,4)
        layout.addWidget(self.axis_h_x,9,2,1,4)
        layout.addWidget(self.axis_h_y,9,3,1,4)
        layout.addWidget(self.axis_h_z,9,4,1,4)

        layout.addWidget(image,10,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        Type = self.Type_ComboBox.currentIndex()
        Length = self.Length_Value.value()
        Width = self.Width_Value.value()
        IndexNut = {0 : 3,
                    1 : 4,
                    2 : 5,
                    3 : 6}
        nut_hole = IndexNut[self.ComboBox_Nut_Hole.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if Type == 0:
                beltcl.BeltClamp(fc_fro_ax = axis_d,#VX,
                                fc_top_ax = axis_h,#VZ,
                                base_h = 2,
                                base_l = Length,
                                base_w = Width,
                                bolt_d = nut_hole,
                                bolt_csunk = 0,
                                ref = 1,
                                pos = pos,
                                extra=1,
                                wfco = 1,
                                intol = 0,
                                name = 'belt_clamp' )
            elif Type == 1:
                beltcl.DoubleBeltClamp(axis_h = axis_h,#VZ,
                                    axis_d = axis_d,#VX,
                                    axis_w = axis_w,#VY,
                                    base_h = 2,
                                    base_l = Length,
                                    base_w = Width,
                                    bolt_d = nut_hole,
                                    bolt_csunk = 0,
                                    ref = 1,
                                    pos = pos,
                                    extra=1,
                                    wfco = 1,
                                    intol = 0,
                                    name = 'double_belt_clamp' )
            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                           Belt Clamped                          |
# |_________________________________________________________________|

# This part dindt work properly. Need more test for the moment.
#   IS DISABLED IN InitGui.py file.
class _BeltClampedCmd:
    def Activated(self):
        Widget_BeltClamped = QtWidgets.QWidget()
        Widget_BeltClamped.setWindowTitle("Belt Clamped options")
        Panel_BeltClamped = BeltClampedTaskPanel(Widget_BeltClamped)
        FreeCADGui.Control.showDialog(Panel_BeltClamped)     
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Belt clamped')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a belt clamped')
        return {
            'Pixmap': __dir__ + '/icons/Belt_Clamped_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class BeltClampedTaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Diameters ----
        #Label :
        self.Label_Diameter = QtWidgets.QLabel("Diameter pulley")   
        # 1:
        self.Label_Diameter_1 = QtWidgets.QLabel("1:")   
        self.Pulley_D1 = QtWidgets.QDoubleSpinBox()
        self.Pulley_D1.setValue(5)
        self.Pulley_D1.setSuffix('')
        self.Pulley_D1.setMinimum(1)

        # 2:
        self.Label_Diameter_2 = QtWidgets.QLabel("2:")
        self.Pulley_D2 = QtWidgets.QDoubleSpinBox()
        self.Pulley_D2.setValue(6)
        self.Pulley_D2.setSuffix('')
        self.Pulley_D2.setMinimum(1)

        # ---- row 3: Separation ----
        # Label :
        self.Label_Sep = QtWidgets.QLabel("Separation between ")

        # Pulleys Axis d:
        self.Label_Sep_d = QtWidgets.QLabel("pulleys in axis d:")
        self.Sep_d = QtWidgets.QDoubleSpinBox()
        self.Sep_d.setValue(80)
        self.Sep_d.setSuffix(' mm')
        self.Sep_d.setMinimum(1)

        # Pulleys Axis w:
        self.Label_Sep_w = QtWidgets.QLabel("pulleys in axis w:")
        self.Sep_w = QtWidgets.QDoubleSpinBox()
        self.Sep_w.setValue(0)
        self.Sep_w.setSuffix(' mm')
        self.Sep_w.setMinimum(1)

        # Pulley 1 and Clamp 1 Axis d:
        self.Label_Sep_Clamp_1d = QtWidgets.QLabel("pulley 1 and clamp 1 in axis d")
        self.Sep_Clamp_1d = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp_1d.setValue(15)
        self.Sep_Clamp_1d.setSuffix(' mm')
        self.Sep_Clamp_1d.setMinimum(1)

        # Pulley 1 and Clamp 1 Axis w:
        self.Label_Sep_Clamp_1w = QtWidgets.QLabel("pulley 1 and clamp 1 in axis w")
        self.Sep_Clamp_1w = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp_1w.setValue(5)
        self.Sep_Clamp_1w.setSuffix(' mm')
        self.Sep_Clamp_1w.setMinimum(1)
        
        # Pulley 2 and Clamp 2 Axis d:
        self.Label_Sep_Clamp_2d = QtWidgets.QLabel("pulley 2 and clamp 2 in axis w")
        self.Sep_Clamp_2d = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp_2d.setValue(15)
        self.Sep_Clamp_2d.setSuffix(' mm')
        self.Sep_Clamp_2d.setMinimum(1)

        # ---- row 9: Clamp ----
        # Label :
        self.Label_Clamp = QtWidgets.QLabel("Clamp ")

        # Clamp d:
        self.Label_Clamp_d = QtWidgets.QLabel("Length:")
        self.Clamp_d = QtWidgets.QDoubleSpinBox()
        self.Clamp_d.setValue(5)
        self.Clamp_d.setSuffix('')
        self.Clamp_d.setMinimum(1)

        # Clamp w:
        self.Label_Clamp_w = QtWidgets.QLabel("Width:")
        self.Clamp_w = QtWidgets.QDoubleSpinBox()
        self.Clamp_w.setValue(4)
        self.Clamp_w.setSuffix('')
        self.Clamp_w.setMinimum(1)

        # Separation between clamps:
        self.Label_Sep_Clamp = QtWidgets.QLabel("Sepatarion:")
        self.Sep_Clamp = QtWidgets.QDoubleSpinBox()
        self.Sep_Clamp.setValue(8)
        self.Sep_Clamp.setSuffix('')
        self.Sep_Clamp.setMinimum(0.5)

        # ---- row 13: Belt ----
        self.label_Belt = QtWidgets.QLabel("Belt ")

        # Width:
        self.Label_belt_w = QtWidgets.QLabel("Width:")
        self.belt_w = QtWidgets.QDoubleSpinBox()
        self.belt_w.setValue(6)
        self.belt_w.setSuffix(' mm')
        self.belt_w.setMinimum(1)

        # Thick:
        self.Label_belt_t = QtWidgets.QLabel("Thick:")
        self.belt_t = QtWidgets.QDoubleSpinBox()
        self.belt_t.setValue(1.38)
        self.belt_t.setSuffix(' mm')
        self.belt_t.setMinimum(1)

        # Radius cyl:
        self.Label_R_cyl = QtWidgets.QLabel("Radius of the cylinder for the belt:")
        self.R_cyl = QtWidgets.QDoubleSpinBox()
        self.R_cyl.setValue(3)
        self.R_cyl.setSuffix(' mm')
        self.R_cyl.setMinimum(1)

        # ---- row 17: Position ----
        self.label_position = QtWidgets.QLabel("Position ")
        self.Label_pos_x = QtWidgets.QLabel("x:")
        self.Label_pos_y = QtWidgets.QLabel("y:")
        self.Label_pos_z = QtWidgets.QLabel("z:")
        self.pos_x = QtWidgets.QDoubleSpinBox()
        self.pos_y = QtWidgets.QDoubleSpinBox()
        self.pos_z = QtWidgets.QDoubleSpinBox()
        self.pos_x.setValue(0)
        self.pos_y.setValue(0)
        self.pos_z.setValue(0)

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3','4','5','6','7','8','9','10','11'])
        self.pos_d.setCurrentIndex(0)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3','4','5','6','7','8'])
        self.pos_w.setCurrentIndex(0)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1'])
        self.pos_h.setCurrentIndex(0)

        # ---- row 23: axis ----
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
        self.axis_d_x.setValue(0)
        self.axis_d_y.setValue(1)
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
        self.axis_w_x.setValue(1)
        self.axis_w_y.setValue(0)
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

        # ---- row 26: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/BeltClamped.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_Diameter,0,0,1,3)
        layout.addWidget(self.Label_Diameter_1,1,1,1,3)
        layout.addWidget(self.Pulley_D1,1,2,1,3)
        layout.addWidget(self.Label_Diameter_2,2,1,1,3)
        layout.addWidget(self.Pulley_D2,2,2,1,3)

        layout.addWidget(self.Label_Sep,3,0,1,3)
        layout.addWidget(self.Label_Sep_d,4,1,1,3)
        layout.addWidget(self.Sep_d,4,2,1,3)
        layout.addWidget(self.Label_Sep_w,5,1,1,3)
        layout.addWidget(self.Sep_w,5,2,1,3)

        layout.addWidget(self.Label_Sep_Clamp_1d,6,1,1,3)
        layout.addWidget(self.Sep_Clamp_1d,6,2,1,3)
        layout.addWidget(self.Label_Sep_Clamp_1w,7,1,1,3)
        layout.addWidget(self.Sep_Clamp_1w,7,2,1,3)
        layout.addWidget(self.Label_Sep_Clamp_2d,8,1,1,3)
        layout.addWidget(self.Sep_Clamp_2d,8,2,1,3)

        layout.addWidget(self.Label_Clamp,9,0,1,3)
        layout.addWidget(self.Label_Clamp_d,10,1,1,3)
        layout.addWidget(self.Clamp_d,10,2,1,3)
        layout.addWidget(self.Label_Clamp_w,11,1,1,3)
        layout.addWidget(self.Clamp_w,11,2,1,3)
        layout.addWidget(self.Label_Sep_Clamp,12,1,1,3)
        layout.addWidget(self.Sep_Clamp,12,2,1,3)

        layout.addWidget(self.label_Belt,13,0,1,3)
        layout.addWidget(self.Label_belt_w,14,1,1,3)
        layout.addWidget(self.belt_w,14,2,1,3)
        layout.addWidget(self.Label_belt_t,15,1,1,3)
        layout.addWidget(self.belt_t,15,2,1,3)
        layout.addWidget(self.Label_R_cyl,16,1,1,3)
        layout.addWidget(self.R_cyl,16,2,1,3)

        layout.addWidget(self.label_position,17,0,1,3)
        layout.addWidget(self.Label_pos_x,17,1,1,3)
        layout.addWidget(self.pos_x,187,2,1,3)
        layout.addWidget(self.Label_pos_y,18,1,1,3)
        layout.addWidget(self.pos_y,18,2,1,3)
        layout.addWidget(self.Label_pos_z,19,1,1,3)
        layout.addWidget(self.pos_z,19,2,1,3)

        layout.addWidget(self.Label_pos_d,20,1,1,3)
        layout.addWidget(self.pos_d,20,2,1,3)
        layout.addWidget(self.Label_pos_w,21,1,1,3)
        layout.addWidget(self.pos_w,21,2,1,3)
        layout.addWidget(self.Label_pos_h,22,1,1,3)
        layout.addWidget(self.pos_h,22,2,1,3)

        layout.addWidget(self.Label_axis,23,0,1,4)
        layout.addWidget(self.Label_axis_d,23,1,1,4)
        layout.addWidget(self.axis_d_x,23,2,1,4)
        layout.addWidget(self.axis_d_y,23,3,1,4)
        layout.addWidget(self.axis_d_z,23,4,1,4)
        layout.addWidget(self.Label_axis_w,24,1,1,4)
        layout.addWidget(self.axis_w_x,24,2,1,4)
        layout.addWidget(self.axis_w_y,24,3,1,4)
        layout.addWidget(self.axis_w_z,24,4,1,4)
        layout.addWidget(self.Label_axis_h,25,1,1,4)
        layout.addWidget(self.axis_h_x,25,2,1,4)
        layout.addWidget(self.axis_h_y,25,3,1,4)
        layout.addWidget(self.axis_h_z,25,4,1,4)

        layout.addWidget(image,26,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        pull1_dm = self.Pulley_D1.value()
        pull2_dm = self.Pulley_D2.value()
        pull_sep_d = self.Sep_d.value()
        pull_sep_w = self.Sep_w.value()
        clamp_pull1_d = self.Sep_Clamp_1d.value()
        clamp_pull1_w = self.Sep_Clamp_1w.value()
        clamp_pull2_d = self.Sep_Clamp_2d.value()
        clamp_d = self.Clamp_d.value()
        clamp_w = self.Clamp_w.value()
        clamp_cyl_sep = self.Sep_Clamp.value()
        cyl_r = self.R_cyl.value()
        belt_width = self.belt_w.value()
        belt_thick = self.belt_t.value()
        positions_d = [0,1,2,3,4,5,6,7,8,9,10,11]
        positions_w = [0,1,2,3,4,5,6,7,8]
        positions_h = [0,1]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            beltcl.PartBeltClamped(pull1_dm,
                                pull2_dm,
                                pull_sep_w,
                                pull_sep_d,
                                clamp_pull1_d,
                                clamp_pull1_w,
                                clamp_pull2_d,
                                clamp_d,
                                clamp_w,
                                clamp_cyl_sep,
                                cyl_r,
                                belt_width = belt_width,
                                belt_thick = belt_thick,
                                axis_d = axis_d ,#VY,
                                axis_w = axis_w ,#VX,
                                axis_h = axis_h ,#VZ,
                                pos_d = pos_d,
                                pos_w = pos_w,
                                pos_h = pos_h,
                                pos=pos,
                                name = 'belt')
            
            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                          Sensor Holder                          |
# |_________________________________________________________________|

class _SensorHolder_Cmd:
    def Activated(self):
        Widget_SensorHolder = QtWidgets.QWidget()
        Widget_SensorHolder.setWindowTitle("Sensor Holder options")
        Panel_SensorHolder = SensorHolderTaskPanel(Widget_SensorHolder)
        FreeCADGui.Control.showDialog(Panel_SensorHolder)     
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Sensor Holder')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Creates a sensor holder')
        return {
            'Pixmap': __dir__ + '/icons/Sensor_holder_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class SensorHolderTaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Sensor Pin Length ----
        self.Sensor_Pin_Length_Label = QtWidgets.QLabel("Sensor Pin Length:")  
        self.Sensor_Pin_Length_Value = QtWidgets.QDoubleSpinBox()
        self.Sensor_Pin_Length_Value.setValue(10)
        self.Sensor_Pin_Length_Value.setSuffix(' mm')
        self.Sensor_Pin_Length_Value.setMinimum(10) #Not sure

        # ---- row 1: Sensor Pin Width ----
        self.Sensor_Pin_Width_Label = QtWidgets.QLabel("Sensor Pin Width:")  
        self.Sensor_Pin_Width_Value = QtWidgets.QDoubleSpinBox()
        self.Sensor_Pin_Width_Value.setValue(2)
        self.Sensor_Pin_Width_Value.setSuffix(' mm')
        self.Sensor_Pin_Width_Value.setMinimum(2) #Not sure

        # ---- row 2: Sensor Pin High ----
        self.Sensor_Pin_High_Label = QtWidgets.QLabel("Sensor Pin High:")  
        self.Sensor_Pin_High_Value = QtWidgets.QDoubleSpinBox()
        self.Sensor_Pin_High_Value.setValue(3)
        self.Sensor_Pin_High_Value.setSuffix(' mm')
        self.Sensor_Pin_High_Value.setMinimum(3) #Not sure

        # ---- row 3: Depth ----
        self.Depth_CD_Label = QtWidgets.QLabel("Depth:")  
        self.Depth_CD_Value = QtWidgets.QDoubleSpinBox()
        self.Depth_CD_Value.setValue(8)
        self.Depth_CD_Value.setSuffix(' mm')
        self.Depth_CD_Value.setMinimum(8) #Not sure

        # ---- row 4: Width CD case----
        self.Width_CD_Label = QtWidgets.QLabel("Width CD case:")  
        self.Width_CD_Value = QtWidgets.QDoubleSpinBox()
        self.Width_CD_Value.setValue(20)
        self.Width_CD_Value.setSuffix(' mm')
        self.Width_CD_Value.setMinimum(20) #Not sure

        # ---- row 5: High CD case----
        self.High_CD_Label = QtWidgets.QLabel("High CD case:")  
        self.High_CD_Value = QtWidgets.QDoubleSpinBox()
        self.High_CD_Value.setValue(37)
        self.High_CD_Value.setSuffix(' mm')
        self.High_CD_Value.setMinimum(37) #Not sure

        # ---- row 6: placement ----
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

        # ---- row 9: axis ----
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

        # ---- row 12: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/SensorHolder.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Sensor_Pin_Length_Label,0,0,1,2)
        layout.addWidget(self.Sensor_Pin_Length_Value,0,1,1,2)
        layout.addWidget(self.Sensor_Pin_Width_Label,1,0,1,2)
        layout.addWidget(self.Sensor_Pin_Width_Value,1,1,1,2)
        layout.addWidget(self.Sensor_Pin_High_Label,2,0,1,2)
        layout.addWidget(self.Sensor_Pin_High_Value,2,1,1,2)

        layout.addWidget(self.Depth_CD_Label,3,0,1,2)
        layout.addWidget(self.Depth_CD_Value,3,1,1,2)

        layout.addWidget(self.Width_CD_Label,4,0,1,2)
        layout.addWidget(self.Width_CD_Value,4,1,1,2)

        layout.addWidget(self.High_CD_Label,5,0,1,2)
        layout.addWidget(self.High_CD_Value,5,1,1,2)

        layout.addWidget(self.Label_position,6,0,1,2)
        layout.addWidget(self.Label_pos_x,6,1,1,2)
        layout.addWidget(self.pos_x,6,2,1,2)
        layout.addWidget(self.Label_pos_y,7,1,1,2)
        layout.addWidget(self.pos_y,7,2,1,2)
        layout.addWidget(self.Label_pos_z,8,1,1,2)
        layout.addWidget(self.pos_z,8,2,1,2)

        layout.addWidget(self.Label_axis,9,0,1,4)
        layout.addWidget(self.Label_axis_d,9,1,1,4)
        layout.addWidget(self.axis_d_x,9,2,1,4)
        layout.addWidget(self.axis_d_y,9,3,1,4)
        layout.addWidget(self.axis_d_z,9,4,1,4)
        layout.addWidget(self.Label_axis_w,10,1,1,4)
        layout.addWidget(self.axis_w_x,10,2,1,4)
        layout.addWidget(self.axis_w_y,10,3,1,4)
        layout.addWidget(self.axis_w_z,10,4,1,4)
        layout.addWidget(self.Label_axis_h,11,1,1,4)
        layout.addWidget(self.axis_h_x,11,2,1,4)
        layout.addWidget(self.axis_h_y,11,3,1,4)
        layout.addWidget(self.axis_h_z,11,4,1,4)

        layout.addWidget(image,12,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        Sensor_Pin_Length = self.Sensor_Pin_Length_Value.value()
        Sensor_Pin_Width = self.Sensor_Pin_Width_Value.value()
        Sensor_Pin_High = self.Sensor_Pin_High_Value.value()
        Depth_CD = self.Depth_CD_Value.value()
        Width_CD = self.Width_CD_Value.value()
        High_CD = self.High_CD_Value.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            parts.sensor_holder(sensor_support_length = Sensor_Pin_Length,
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
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                             Aluprof                             |
# |_________________________________________________________________|

class _AluproftCmd:
    """
    This class create an aluminium profile with diferents sizes and any length
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Aluminium Profile options")
        panel_Aluproft = Aluproft_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_Aluproft) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Aluminium profile',
            'Aluminium profile')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/Aluproft_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class Aluproft_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Size ----
        self.Prof_Label = QtWidgets.QLabel("Size")  
        self.prof_size = ["5", "10", "15", "20", "30", "40"]
        self.profile = QtWidgets.QComboBox()
        self.profile.addItems(self.prof_size)
        self.profile.setCurrentIndex(3) #20


        # ---- row 1: Length ----
        self.length_Label = QtWidgets.QLabel("Length")  
        self.length_prof = QtWidgets.QDoubleSpinBox()
        self.length_prof.setValue(20)
        self.length_prof.setSuffix(' mm')
        self.length_prof.setMinimum(10) 
        self.length_prof.setMaximum(999)

        # ---- row 2: placement ----
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

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2'])
        self.pos_d.setCurrentIndex(0)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2'])
        self.pos_w.setCurrentIndex(0)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2'])
        self.pos_h.setCurrentIndex(0)

        # ---- row 8: axis ----
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

        # ---- row 11: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/Aluprof.png">hear</a>.')
        image.setOpenExternalLinks(True)
        # image.setPixmap(QtGui.QPixmap('/img_gui/Aluprof.png'))

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Prof_Label,0,0,1,2)
        layout.addWidget(self.profile,0,1,1,2)
        layout.addWidget(self.length_Label,1,0,1,2)
        layout.addWidget(self.length_prof,1,1,1,2)

        layout.addWidget(self.Label_position,2,0,1,2)
        layout.addWidget(self.Label_pos_x,2,1,1,2)
        layout.addWidget(self.pos_x,2,2,1,2)
        layout.addWidget(self.Label_pos_y,3,1,1,2)
        layout.addWidget(self.pos_y,3,2,1,2)
        layout.addWidget(self.Label_pos_z,4,1,1,2)
        layout.addWidget(self.pos_z,4,2,1,2)

        layout.addWidget(self.Label_pos_d,5,1,1,2)
        layout.addWidget(self.pos_d,5,2,1,2)
        layout.addWidget(self.Label_pos_w,6,1,1,2)
        layout.addWidget(self.pos_w,6,2,1,2)
        layout.addWidget(self.Label_pos_h,7,1,1,2)
        layout.addWidget(self.pos_h,7,2,1,2)

        layout.addWidget(self.Label_axis,8,0,1,4)
        layout.addWidget(self.Label_axis_d,8,1,1,4)
        layout.addWidget(self.axis_d_x,8,2,1,4)
        layout.addWidget(self.axis_d_y,8,3,1,4)
        layout.addWidget(self.axis_d_z,8,4,1,4)
        layout.addWidget(self.Label_axis_w,9,1,1,4)
        layout.addWidget(self.axis_w_x,9,2,1,4)
        layout.addWidget(self.axis_w_y,9,3,1,4)
        layout.addWidget(self.axis_w_z,9,4,1,4)
        layout.addWidget(self.Label_axis_h,10,1,1,4)
        layout.addWidget(self.axis_h_x,10,2,1,4)
        layout.addWidget(self.axis_h_y,10,3,1,4)
        layout.addWidget(self.axis_h_z,10,4,1,4)

        layout.addWidget(image,11,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        prof_type = {0:  5,
                     1: 10,
                     2: 15,
                     3: 20,
                     4: 30,
                     5: 40}
        prof = prof_type[self.profile.currentIndex()]
        length = self.length_prof.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        positions_d = [0,1,2]
        positions_w = [0,1,2]
        positions_h = [0,1,2]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            comps.PartAluProf(depth = length,
                            aluprof_dict = kcomp.ALU_PROF[prof],
                            xtr_d=0, xtr_nd=0,
                            axis_d = axis_d ,#VX, 
                            axis_w = axis_w ,#VY, 
                            axis_h = axis_h ,#V0,
                            pos_d = pos_d, pos_w = pos_w, pos_h = pos_h,
                            pos = pos,
                            model_type = 1, # dimensional model
                            name = 'aluprof_'+str(prof))

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                          Lin Guide Block                        |
# |_________________________________________________________________|
class _LinGuideBlockCmd:
    """
    This class create Linear Guide Block
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Linear Guide Block options")
        panel_LinGuideBlock = LinGuideBlock_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_LinGuideBlock) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Linear Guide Block',
            'Linear Guide Block')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/LinGuideBlock_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class LinGuideBlock_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Size ----
        self.Label_block = QtWidgets.QLabel("Type:")
        self.block_dict = QtWidgets.QComboBox()
        self.block_dict.addItems(["SEBW16","SEB15A","SEB8","SEB10"])
        self.block_dict.setCurrentIndex(0)

        # ---- row 1: Position ----
        self.label_position = QtWidgets.QLabel("Position ")

        # d :
        self.Label_pos_d = QtWidgets.QLabel("in d:")
        self.pos_d = QtWidgets.QComboBox()
        self.pos_d.addItems(['0','1','2','3'])
        self.pos_d.setCurrentIndex(0)

        # w :
        self.Label_pos_w = QtWidgets.QLabel("in w:")
        self.pos_w = QtWidgets.QComboBox()
        self.pos_w.addItems(['0','1','2','3','4'])
        self.pos_w.setCurrentIndex(0)

        # h :
        self.Label_pos_h = QtWidgets.QLabel("in h:")
        self.pos_h = QtWidgets.QComboBox()
        self.pos_h.addItems(['0','1','2','3','4'])
        self.pos_h.setCurrentIndex(1)

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
        self.pos_x.setAlignment(PySide2.QtCore.Qt.AlignCenter)
        self.pos_y.setAlignment(PySide2.QtCore.Qt.AlignCenter)
        self.pos_z.setAlignment(PySide2.QtCore.Qt.AlignCenter)

        # ---- row 7: axis ----
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

        # ---- row 10: image ----
        image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/LinearGuideBlock.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_block,0,0,1,2)
        layout.addWidget(self.block_dict,0,1,1,2)

        layout.addWidget(self.label_position,1,0,1,2)
        layout.addWidget(self.Label_pos_d,1,1,1,2)
        layout.addWidget(self.pos_d,1,2,1,2)
        layout.addWidget(self.Label_pos_w,2,1,1,2)
        layout.addWidget(self.pos_w,2,2,1,2)
        layout.addWidget(self.Label_pos_h,3,1,1,2)
        layout.addWidget(self.pos_h,3,2,1,2)
        layout.addWidget(self.Label_pos_x,4,1,1,2)
        layout.addWidget(self.pos_x,4,2,1,2)
        layout.addWidget(self.Label_pos_y,5,1,1,2)
        layout.addWidget(self.pos_y,5,2,1,2)
        layout.addWidget(self.Label_pos_z,6,1,1,2)
        layout.addWidget(self.pos_z,6,2,1,2)

        layout.addWidget(self.Label_axis,7,0,1,4)
        layout.addWidget(self.Label_axis_d,7,1,1,4)
        layout.addWidget(self.axis_d_x,7,2,1,4)
        layout.addWidget(self.axis_d_y,7,3,1,4)
        layout.addWidget(self.axis_d_z,7,4,1,4)
        layout.addWidget(self.Label_axis_w,8,1,1,4)
        layout.addWidget(self.axis_w_x,8,2,1,4)
        layout.addWidget(self.axis_w_y,8,3,1,4)
        layout.addWidget(self.axis_w_z,8,4,1,4)
        layout.addWidget(self.Label_axis_h,9,1,1,4)
        layout.addWidget(self.axis_h_x,9,2,1,4)
        layout.addWidget(self.axis_h_y,9,3,1,4)
        layout.addWidget(self.axis_h_z,9,4,1,4)

        layout.addWidget(image,10,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        dict_block = {0: kcomp.SEBWM16_B, 1: kcomp.SEB15A_B, 2: kcomp.SEB8_B, 3: kcomp.SEB10_B}
        dict_rail = {0: kcomp.SEBWM16_R, 1: kcomp.SEB15A_R, 2: kcomp.SEB8_R, 3: kcomp.SEB10_R}
        block_dict = dict_block[self.block_dict.currentIndex()]
        rail_dict = dict_rail[self.block_dict.currentIndex()]
        
        positions_d = [0,1,2,3]
        positions_w = [0,1,2,3,4]
        positions_h = [0,1,2,3,4]
        pos_d = positions_d[self.pos_d.currentIndex()]
        pos_w = positions_w[self.pos_w.currentIndex()]
        pos_h = positions_h[self.pos_h.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(),self.pos_y.value(),self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            comps.PartLinGuideBlock(block_dict, rail_dict,
                                    axis_d = axis_d ,#VX, 
                                    axis_w = axis_w ,#V0, 
                                    axis_h = axis_h ,#VZ,
                                    pos_d = pos_d, pos_w = pos_w, pos_h = pos_h,
                                    pos = pos,
                                    model_type = 1, # dimensional model
                                    name = '')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                        Bolt, Nut, Whaser                        |
# |_________________________________________________________________|
class _BoltCmd:
    """
    This class create Bolts, Nuts & Washers with diferents metrics
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Bolt, Nut and Whaser options")
        panel_Bolt = Bolt_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_Bolt) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Bolts, Nuts & Washers',
            'Bolts, Nuts & Washers')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/Bolt_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class Bolt_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Type ----
        self.Type_select_Label = QtWidgets.QLabel("Type")  
        self.Type_text = ["Bolt D912", "Nut D934", "Whasher DIN 125", "Whasher DIN 9021"]
        self.Type_select = QtWidgets.QComboBox()
        self.Type_select.addItems(self.Type_text)
        self.Type_select.setCurrentIndex(0)

        # ---- row 1: Metric ----
        self.Bolt_Metric_Label = QtWidgets.QLabel("Metric")  
        self.Bolt_metric = ["3","4","5","6"]
        self.metric = QtWidgets.QComboBox()
        self.metric.addItems(self.Bolt_metric)
        self.metric.setCurrentIndex(0)

        # ---- row 2: Length ----
        self.length_Label = QtWidgets.QLabel("Length for bolt")  
        self.length_bolt = QtWidgets.QDoubleSpinBox()
        self.length_bolt.setValue(20)
        self.length_bolt.setSuffix(' mm')
        self.length_bolt.setMinimum(4) 

        # ---- row 3: placement ----
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

        # # d :
        # self.Label_pos_d = QtWidgets.QLabel("in d:")
        # self.pos_d = QtWidgets.QComboBox()
        # self.pos_d.addItems(['0','1','2'])
        # self.pos_d.setCurrentIndex(0)

        # # w :
        # self.Label_pos_w = QtWidgets.QLabel("in w:")
        # self.pos_w = QtWidgets.QComboBox()
        # self.pos_w.addItems(['0','1','2'])
        # self.pos_w.setCurrentIndex(0)

        # # h :
        # self.Label_pos_h = QtWidgets.QLabel("in h:")
        # self.pos_h = QtWidgets.QComboBox()
        # self.pos_h.addItems(['0','1','2','3','4','5','6','7'])
        # self.pos_h.setCurrentIndex(0)

        # ---- row 9: image ----
        # image = QtWidgets.QLabel('Image of points and axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/Bolt_Nut_Washer.png">hear</a>.')
        # image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Type_select_Label,0,0,1,2)
        layout.addWidget(self.Type_select,0,1,1,2)
        layout.addWidget(self.Bolt_Metric_Label,1,0,1,2)
        layout.addWidget(self.metric,1,1,1,2)
        layout.addWidget(self.length_Label,2,0,1,2)
        layout.addWidget(self.length_bolt,2,1,1,2)

        layout.addWidget(self.Label_position,3,0,1,2)
        layout.addWidget(self.Label_pos_x,3,1,1,2)
        layout.addWidget(self.pos_x,3,2,1,2)
        layout.addWidget(self.Label_pos_y,4,1,1,2)
        layout.addWidget(self.pos_y,4,2,1,2)
        layout.addWidget(self.Label_pos_z,5,1,1,2)
        layout.addWidget(self.pos_z,5,2,1,2)

        # layout.addWidget(self.Label_pos_d,6,1,1,2)
        # layout.addWidget(self.pos_d,6,2,1,2)
        # layout.addWidget(self.Label_pos_w,7,1,1,2)
        # layout.addWidget(self.pos_w,7,2,1,2)
        # layout.addWidget(self.Label_pos_h,8,1,1,2)
        # layout.addWidget(self.pos_h,8,2,1,2)

        # layout.addWidget(image,9,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        metric = {0: 3,
                  1: 4,
                  2: 5,
                  3: 6}
        metric = metric[self.metric.currentIndex()]
        Type_sel = self.Type_text[self.Type_select.currentIndex()]
        length = self.length_bolt.value()
        # positions_d = [0,1,2]
        # positions_w = [0,1,2]
        # positions_h = [0,1,2,3,4,5,6,7]
        # pos_d = positions_d[self.pos_d.currentIndex()]
        # pos_w = positions_w[self.pos_w.currentIndex()]
        # pos_h = positions_h[self.pos_h.currentIndex()]

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())

        # Chose the data in function of the type selected
        if Type_sel == "Bolt D912":
            fc_clss.Din912Bolt(metric,
                               shank_l = length,
                               shank_l_adjust = 0,
                               shank_out = 0,
                               head_out = 0,
                               axis_h = VZ, axis_d = None, axis_w = None,
                               pos_h = 0, pos_d = 0, pos_w = 0,
                               pos = pos,
                               model_type = 0,
                               name = '')

        elif Type_sel == "Nut D934":
            fc_clss.Din934Nut(metric = metric,
                              axis_d_apo = 0, 
                              h_offset = 0,
                              axis_h = VZ,
                              axis_d = None,
                              axis_w = None,
                              pos_h = 0, pos_d = 0, pos_w = 0,
                              pos = pos)
        elif Type_sel == "Whasher DIN 125":
            fc_clss.Din125Washer(metric,
                                 axis_h = VZ, 
                                 pos_h = 1, 
                                 tol = 0,
                                 pos = pos,
                                 model_type = 0, # exact
                                 name = '')
        else : #Type_sel == "Whasher DIN 9021"
            fc_clss.Din9021Washer(metric,
                                  axis_h = VZ, 
                                  pos_h = 1, 
                                  tol = 0,
                                  pos = pos,
                                  model_type = 0, # exact
                                  name = '')
            # If there are other types of bolts it could be there

        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.Control.closeDialog() #close the dialog
        FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                            Tube Lense                           |
# |_________________________________________________________________|
class _TubeLense_Cmd:
    """
    This class create Tube Lense
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Tube Lense options")
        panel_TubeLense = TubeLense_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_TubeLense) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Tube Lense',
            'Tube Lense')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/TubeLense_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class TubeLense_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Length ----
        self.Label_Length = QtWidgets.QLabel("Length")
        self.Length = QtWidgets.QComboBox()
        self.Length.addItems(["3","5","10","15","20","30"])
        self.Length.setCurrentIndex(2) #10

        # ---- row 1: Placement ----
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

        # ---- row 8: axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
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
        self.axis_h_x.setValue(1)
        self.axis_h_y.setValue(0)
        self.axis_h_z.setValue(0)

        # ---- row 5: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/TubeLense.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_Length,0,0,1,2)
        layout.addWidget(self.Length,0,1,1,2)
        layout.addWidget(self.Label_position,1,0,1,2)
        layout.addWidget(self.Label_pos_x,1,1,1,2)
        layout.addWidget(self.pos_x,1,2,1,2)
        layout.addWidget(self.Label_pos_y,2,1,1,2)
        layout.addWidget(self.pos_y,2,2,1,2)
        layout.addWidget(self.Label_pos_z,3,1,1,2)
        layout.addWidget(self.pos_z,3,2,1,2)

        layout.addWidget(self.Label_position,4,0,1,4)
        layout.addWidget(self.Label_axis_h,4,1,1,4)
        layout.addWidget(self.axis_h_x,4,2,1,4)
        layout.addWidget(self.axis_h_y,4,3,1,4)
        layout.addWidget(self.axis_h_z,4,4,1,4)

        layout.addWidget(image,5,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        size = {0: 3, 1: 5, 2: 10, 3: 15, 4: 20, 5: 30}
        sm1l_size = size[self.Length.currentIndex()]
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        comp_optic.SM1TubelensSm2(sm1l_size,
                                   fc_axis = axis_h,#VX,
                                   ref_sm1 = 1,
                                   pos = pos,
                                   ring = 1,
                                   name = 'tubelens_sm1_sm2')

        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.Control.closeDialog() #close the dialog
        FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                           LCPB1M Base                           |
# |_________________________________________________________________|

class _Lcpb1mBase_Cmd:
    """
    This class create a Lcpb1mBase
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("LCPB1M Base options")
        panel_Lcpb1mBase = Lcpb1mBase_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_Lcpb1mBase) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Thorlabs LCPB1_M',
            'Thorlabs LCPB1_M')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/Lcpb1mBase_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class Lcpb1mBase_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Placement ----
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

        # ---- row 3: axis ----
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

        # ---- row 6: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/LCPB1MBase.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_position,0,0,1,2)
        layout.addWidget(self.Label_pos_x,0,1,1,2)
        layout.addWidget(self.pos_x,0,2,1,2)
        layout.addWidget(self.Label_pos_y,1,1,1,2)
        layout.addWidget(self.pos_y,1,2,1,2)
        layout.addWidget(self.Label_pos_z,2,1,1,2)
        layout.addWidget(self.pos_z,2,2,1,2)

        layout.addWidget(self.Label_axis,3,0,1,4)
        layout.addWidget(self.Label_axis_d,3,1,1,4)
        layout.addWidget(self.axis_d_x,3,2,1,4)
        layout.addWidget(self.axis_d_y,3,3,1,4)
        layout.addWidget(self.axis_d_z,3,4,1,4)
        layout.addWidget(self.Label_axis_w,4,1,1,4)
        layout.addWidget(self.axis_w_x,4,2,1,4)
        layout.addWidget(self.axis_w_y,4,3,1,4)
        layout.addWidget(self.axis_w_z,4,4,1,4)
        layout.addWidget(self.Label_axis_h,5,1,1,4)
        layout.addWidget(self.axis_h_x,5,2,1,4)
        layout.addWidget(self.axis_h_y,5,3,1,4)
        layout.addWidget(self.axis_h_z,5,4,1,4)

        layout.addWidget(image,6,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            comp_optic.lcpb1m_base(d_lcpb1m_base = kcomp_optic.LCPB1M_BASE,
                                    fc_axis_d = axis_d, #VX,
                                    fc_axis_w = axis_w, #V0,
                                    fc_axis_h = axis_h, #VZ,
                                    ref_d = 1, ref_w = 1, ref_h = 1,
                                    pos = pos, wfco = 1, toprint= 0, name = 'Lcpb1mBase')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                            Cage Cube                            |
# |_________________________________________________________________|

class _CageCube_Cmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("CageCube options")
        panel_CageCube = CageCube_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_CageCube) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'CageCube',
            'CageCube')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/CageCube_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class CageCube_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Type ----
        self.Label_Type = QtWidgets.QLabel("Type ")
        self.Type = QtWidgets.QComboBox()
        self.Type.addItems(["CAGE_CUBE_60","CAGE_CUBE_HALF_60"])
        self.Type.setCurrentIndex(0)

        # ---- row 1: Placement ----
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

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_Type,0,0,1,1)
        layout.addWidget(self.Type,0,1,1,1)
        layout.addWidget(self.Label_position,1,0,1,1)
        layout.addWidget(self.Label_pos_x,2,1,1,2)
        layout.addWidget(self.pos_x,2,2,1,2)
        layout.addWidget(self.Label_pos_y,3,1,1,2)
        layout.addWidget(self.pos_y,3,2,1,2)
        layout.addWidget(self.Label_pos_z,4,1,1,2)
        layout.addWidget(self.pos_z,4,2,1,2)
        
        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        # if fc_isperp(axis_d,axis_w) == 1:
        if self.Type.currentIndex() == 0:
            comp_optic.f_cagecube(kcomp_optic.CAGE_CUBE_60,
                                   axis_thru_rods = 'x',
                                   axis_thru_hole = 'y',
                                   name = 'cagecube',
                                   toprint_tol = 0)
        if self.Type.currentIndex() == 1:
            comp_optic.f_cagecubehalf(kcomp_optic.CAGE_CUBE_HALF_60,
                                       axis_1 = 'x',
                                       axis_2 = 'y',
                                       name = 'cagecubehalf')

        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.Control.closeDialog() #close the dialog
        FreeCADGui.SendMsgToActiveView("ViewFit")
        # else:
            # axis_message()

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                              Plate                              |
# |_________________________________________________________________|

class _Plate_Cmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Plate options")
        panel_Plate = Plate_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_Plate) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Plate',
            'Plate')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/Plate_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class Plate_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: plate ----
        self.Label_plate = QtWidgets.QLabel('Dictionary:')
        self.Plate = QtWidgets.QComboBox()
        self.Plate.addItems(["Lb1cm_Plate","Lb2c_Plate","Lcp01m_plate"])
        self.Plate.setCurrentIndex(0)

        # ---- row 1: placement ----
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

        # ---- row 8: axis ----
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

        # ---- row 7: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/Plate.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_plate,0,0,1,1)
        layout.addWidget(self.Plate,0,1,1,1)
        layout.addWidget(self.Label_position,1,0,1,2)
        layout.addWidget(self.Label_pos_x,1,1,1,2)
        layout.addWidget(self.pos_x,1,2,1,2)
        layout.addWidget(self.Label_pos_y,2,1,1,2)
        layout.addWidget(self.pos_y,2,2,1,2)
        layout.addWidget(self.Label_pos_z,3,1,1,2)
        layout.addWidget(self.pos_z,3,2,1,2)

        layout.addWidget(self.Label_axis,4,0,1,4)
        layout.addWidget(self.Label_axis_d,4,1,1,4)
        layout.addWidget(self.axis_d_x,4,2,1,4)
        layout.addWidget(self.axis_d_y,4,3,1,4)
        layout.addWidget(self.axis_d_z,4,4,1,4)
        layout.addWidget(self.Label_axis_w,5,1,1,4)
        layout.addWidget(self.axis_w_x,5,2,1,4)
        layout.addWidget(self.axis_w_y,5,3,1,4)
        layout.addWidget(self.axis_w_z,5,4,1,4)
        layout.addWidget(self.Label_axis_h,6,1,1,4)
        layout.addWidget(self.axis_h_x,6,2,1,4)
        layout.addWidget(self.axis_h_y,6,3,1,4)
        layout.addWidget(self.axis_h_z,6,4,1,4)

        layout.addWidget(image,7,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_d = FreeCAD.Vector(self.axis_d_x.value(),self.axis_d_y.value(),self.axis_d_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())

        if ortonormal_axis(axis_d,axis_w,axis_h) == True:
            if self.Plate.currentIndex() == 0:
                comp_optic.Lb1cPlate(kcomp_optic.LB1CM_PLATE,
                                    fc_axis_h = axis_h ,#VZ,
                                    fc_axis_l = axis_d ,#VX,
                                    ref_in = 1,
                                    pos = pos,
                                    name = 'lb1c_plate')

            if self.Plate.currentIndex() == 1:
                comp_optic.Lb2cPlate(fc_axis_h = axis_h ,#VZ,
                                    fc_axis_l = axis_d ,#VX,
                                    cl=1, cw=1, ch=0,
                                    pos = pos,
                                    name = 'lb2c_plate')

            if self.Plate.currentIndex() == 2:
                comp_optic.lcp01m_plate(d_lcp01m_plate = kcomp_optic.LCP01M_PLATE,
                                        fc_axis_h = axis_h ,#VZ,
                                        fc_axis_m = axis_d ,#VX,
                                        fc_axis_p = axis_w ,#V0,
                                        cm=1, cp=1, ch=1,
                                        pos = pos,
                                        wfco= 1,
                                        name = 'LCP01M_PLATE')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                             ThLed30                             |
# |_________________________________________________________________|

class _ThLed30_Cmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("ThLed 30 options")
        panel_ThLed30 = ThLed30_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_ThLed30) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ThLed30',
            'ThLed30')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/ThLed30_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class ThLed30_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: placement ----
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

        # ---- row 3: axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
        self.Label_axis_w = QtWidgets.QLabel(":")
        self.Label_axis_h = QtWidgets.QLabel("cable:")
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
        self.axis_h_z.setValue(-1)

        # ---- row 5: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/ThLed30.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_position,0,0,1,2)
        layout.addWidget(self.Label_pos_x,0,1,1,2)
        layout.addWidget(self.pos_x,0,2,1,2)
        layout.addWidget(self.Label_pos_y,1,1,1,2)
        layout.addWidget(self.pos_y,1,2,1,2)
        layout.addWidget(self.Label_pos_z,2,1,1,2)
        layout.addWidget(self.pos_z,2,2,1,2)

        layout.addWidget(self.Label_position,3,0,1,4)
        layout.addWidget(self.Label_axis_w,3,1,1,4)
        layout.addWidget(self.axis_w_x,3,2,1,4)
        layout.addWidget(self.axis_w_y,3,3,1,4)
        layout.addWidget(self.axis_w_z,3,4,1,4)
        layout.addWidget(self.Label_axis_h,4,1,1,4)
        layout.addWidget(self.axis_h_x,4,2,1,4)
        layout.addWidget(self.axis_h_y,4,3,1,4)
        layout.addWidget(self.axis_h_z,4,4,1,4)

        layout.addWidget(image,5,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())

        if fc_isperp(axis_w,axis_h) == 1:
            comp_optic.ThLed30(fc_axis = axis_w,#VY,
                                fc_axis_cable = axis_h,#VZN,
                                pos = pos,
                                name = 'thled30')

            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")
        else:
            axis_message()

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                             PrizLed                             |
# |_________________________________________________________________|

class _PrizLed_Cmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("PrizLed options")
        panel_PrizLed = PrizLed_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_PrizLed) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'PrizLed',
            'PrizLed')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/PrizLed_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class PrizLed_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: placement ----
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

        # ---- row 3: axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
        self.Label_axis_w = QtWidgets.QLabel("led:")
        self.Label_axis_h = QtWidgets.QLabel("clear:")
        self.axis_w_x = QtWidgets.QDoubleSpinBox()
        self.axis_w_y = QtWidgets.QDoubleSpinBox()
        self.axis_w_z = QtWidgets.QDoubleSpinBox()
        self.axis_w_x.setMinimum(-1)
        self.axis_w_x.setMaximum(1)
        self.axis_w_y.setMinimum(-1)
        self.axis_w_y.setMaximum(1)
        self.axis_w_z.setMinimum(-1)
        self.axis_w_z.setMaximum(1)
        self.axis_w_x.setValue(1)
        self.axis_w_y.setValue(0)
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
        self.axis_h_z.setValue(-1)

        # ---- row 5: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/PrizLed.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_position,0,0,1,2)
        layout.addWidget(self.Label_pos_x,0,1,1,2)
        layout.addWidget(self.pos_x,0,2,1,2)
        layout.addWidget(self.Label_pos_y,1,1,1,2)
        layout.addWidget(self.pos_y,1,2,1,2)
        layout.addWidget(self.Label_pos_z,2,1,1,2)
        layout.addWidget(self.pos_z,2,2,1,2)

        layout.addWidget(self.Label_position,3,0,1,4)
        layout.addWidget(self.Label_axis_w,3,1,1,4)
        layout.addWidget(self.axis_w_x,3,2,1,4)
        layout.addWidget(self.axis_w_y,3,3,1,4)
        layout.addWidget(self.axis_w_z,3,4,1,4)
        layout.addWidget(self.Label_axis_h,4,1,1,4)
        layout.addWidget(self.axis_h_x,4,2,1,4)
        layout.addWidget(self.axis_h_y,4,3,1,4)
        layout.addWidget(self.axis_h_z,4,4,1,4)

        layout.addWidget(image,5,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if fc_isperp(axis_w,axis_h) == 1:
            comp_optic.PrizLed(fc_axis_led = axis_w ,#VX, 
                                fc_axis_clear = axis_h ,#VZN,
                                pos = pos, 
                                name = 'prizmatix_led')
            
            FreeCADGui.activeDocument().activeView().viewAxonometric()
            FreeCADGui.Control.closeDialog() #close the dialog
            FreeCADGui.SendMsgToActiveView("ViewFit")
        else:
            axis_message()

    def reject(self):
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

#  _________________________________________________________________
# |                                                                 |
# |                            BreadBoard                           |
# |_________________________________________________________________|

class _BreadBoard_Cmd:
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Bread Board options")
        panel_BreadBoard = BreadBoard_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_BreadBoard) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'BreadBoard',
            'BreadBoard')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/BreadBoard_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class BreadBoard_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: length ----
        self.Label_len = QtWidgets.QLabel("Length:")
        self.len = QtWidgets.QDoubleSpinBox()
        self.len.setMinimum(1)
        self.len.setValue(200)
        self.len.setMaximum(9999)

        # ---- row 1: width ----
        self.Label_wid = QtWidgets.QLabel("Width:")
        self.wid = QtWidgets.QDoubleSpinBox()
        self.wid.setMinimum(1)
        self.wid.setValue(500)
        self.wid.setMaximum(9999)

        # ---- row 2: placement ----
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

        # ---- row 5: axis ----
        self.Label_axis = QtWidgets.QLabel("Axis ")
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

        # ---- row 7: image ----
        image = QtWidgets.QLabel('Image of axis <a href="https://raw.githubusercontent.com/davidmubernal/Mechatronic/master/img_gui/BreadBoard.png">hear</a>.')
        image.setOpenExternalLinks(True)

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Label_len,0,0,1,2)
        layout.addWidget(self.len,0,1,1,2)
        layout.addWidget(self.Label_wid,1,0,1,2)
        layout.addWidget(self.wid,1,1,1,2)
        layout.addWidget(self.Label_position,2,0,1,2)
        layout.addWidget(self.Label_pos_x,2,1,1,2)
        layout.addWidget(self.pos_x,2,2,1,2)
        layout.addWidget(self.Label_pos_y,3,1,1,2)
        layout.addWidget(self.pos_y,3,2,1,2)
        layout.addWidget(self.Label_pos_z,4,1,1,2)
        layout.addWidget(self.pos_z,4,2,1,2)

        layout.addWidget(self.Label_position,5,0,1,4)
        layout.addWidget(self.Label_axis_w,5,1,1,4)
        layout.addWidget(self.axis_w_x,5,2,1,4)
        layout.addWidget(self.axis_w_y,5,3,1,4)
        layout.addWidget(self.axis_w_z,5,4,1,4)
        layout.addWidget(self.Label_axis_h,6,1,1,4)
        layout.addWidget(self.axis_h_x,6,2,1,4)
        layout.addWidget(self.axis_h_y,6,3,1,4)
        layout.addWidget(self.axis_h_z,6,4,1,4)

        layout.addWidget(image,7,0,1,0)

        self.track = v.addEventCallback("SoEvent",self.position)

    def accept(self):
        v.removeEventCallback("SoEvent",self.track)

        length = self.len.value()
        width = self.wid.value()
        pos = FreeCAD.Vector(self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        axis_w = FreeCAD.Vector(self.axis_w_x.value(),self.axis_w_y.value(),self.axis_w_z.value())
        axis_h = FreeCAD.Vector(self.axis_h_x.value(),self.axis_h_y.value(),self.axis_h_z.value())
        
        if fc_isperp(axis_w,axis_h) == 1:
            comp_optic.f_breadboard(kcomp_optic.BREAD_BOARD_M,
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
        v.removeEventCallback("SoEvent",self.track)
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
            self.pos_x.setValue(round(v.getPoint(pos)[0],3))
            self.pos_y.setValue(round(v.getPoint(pos)[1],3))
            self.pos_z.setValue(round(v.getPoint(pos)[2],3))
        else: pass

        if FreeCAD.Gui.Selection.hasSelection():
            self.placement = False
            try:
                obj = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
                if hasattr(obj,"Point"): # Is a Vertex
                    pos = obj.Point
                else: # Is an Edge or Face
                    pos = obj.CenterOfMass
                print(pos)
                print("track" + str(self.placement))
                self.pos_x.setValue(pos.x)
                self.pos_y.setValue(pos.y)
                self.pos_z.setValue(pos.z)
            except Exception: None

###############################################################################
#*************************************TEST*************************************
class _testCmD:
    """
    Test class
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("TEST")
        panel_test = test_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_test) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Test',
            'Test')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class test_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        # layout = QtWidgets.QGridLayout(self.form)
    
    def accept(self):
        import comps_new
        # TODO check Tensioner in NuevaClase. Mirar posiciones para ver que pasa.

        comps_new.AluProf(depth = 50.,
                          aluprof_dict = kcomp.ALU_PROF[20],
                          xtr_d=0, xtr_nd=0,
                          axis_d = VX, 
                          axis_w = VY, 
                          axis_h = V0,
                          pos_d = 0, pos_w = 0, pos_h = 0,
                          pos = V0,
                          model_type = 1, # dimensional model
                          name = 'aluprof_'+str(20))
        # tensioner_clss_new.TensionerHolder(aluprof_w = 20., belt_pos_h = 20., tens_h=10, tens_w=10, tens_d_inside=25)
        # tensioner_clss.IdlerTensionerSet()
        # tensioner_clss_new.IdlerTensionerSet()
        # print("_____________________________")
        # print("Old")
        # tensioner_clss.TensionerSet()
        # print("_____________________________")
        # print("New")
        # tensioner_clss_new.TensionerSet()

        # NuevaClase.placa_perforada( 10, 10, 5, 2, name = 'placa perforada')

        # NuevaClase.placa_tornillos( 10, 10, 5, 1, name = 'placa tornillos')

        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.Control.closeDialog() #close the dialog
        FreeCADGui.SendMsgToActiveView("ViewFit")

#  _________________________________________________________________
# |                                                                 |
# |                        Print and export                         |
# |_________________________________________________________________|

class _ChangePosExportCmd:
    def Activated(self):
        objSelect = FreeCADGui.Selection.getSelection()[0]#.Name
        print_export(objSelect)
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Change Pos and Export',
            'Change Pos and Export')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            'Object selected changes to print position and it is exported in .stl')
        return {
            'Pixmap': __dir__ + '/icons/Print_Export_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

#  _________________________________________________________________
# |                                                                 |
# |                             Assembly                            |
# |_________________________________________________________________|

class _AssemlyCmd:
    """
    This utility change the position of the component that has been selected and set up in the second component you have selected.
    Shape has:
        - Vertexes
        - Edges
        - Faces
        - Solids
    
    """
    def Activated(self):
        baseWidget = QtWidgets.QWidget()
        baseWidget.setWindowTitle("Assembly")
        panel_Assembly = Assembly_TaskPanel(baseWidget)
        FreeCADGui.Control.showDialog(panel_Assembly) 
        """
        message = QtWidgets.QMessageBox()
        message.setText('Select:\n  - First: Think to move.\n   - Second: New placement.\n')
        message.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message.setDefaultButton(QtWidgets.QMessageBox.Ok)
        message.exec_()"""
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Assembly',
            'Assembly')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/icons/Assembly_cmd.svg',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 
    
class Assembly_TaskPanel:
    def __init__(self, widget):
        self.form = widget
        layout = QtWidgets.QGridLayout(self.form)

        self.placement = True

        # ---- row 0: Text ----
        self.Text_1_Label = QtWidgets.QLabel("Select object to move")  
        self.ComboBox_ObjSelection1 = QtWidgets.QComboBox()
        self.TextObj = []
        for i in range (len (FreeCAD.ActiveDocument.Objects)):
            self.TextObj.append(FreeCAD.ActiveDocument.Objects[i].Name)
        self.ComboBox_ObjSelection1.addItems(self.TextObj)
        self.ComboBox_ObjSelection1.setCurrentIndex(0)


        # ---- row 1: Sel obj1 ----
        self.Text_Selection1 = QtWidgets.QLabel("Select")
        self.ComboBox_Selection1 = QtWidgets.QComboBox()
        self.TextSelection1 = ["Vertexes","Edges","Faces"]
        self.ComboBox_Selection1.addItems(self.TextSelection1)
        self.ComboBox_Selection1.setCurrentIndex(0)

        # ---- row 2: Text ----
        self.Text_2_Label = QtWidgets.QLabel("After select the place")  
        self.ComboBox_ObjSelection2 = QtWidgets.QComboBox()
        self.TextObj = []
        for i in range (len (FreeCAD.ActiveDocument.Objects)):
            self.TextObj.append(FreeCAD.ActiveDocument.Objects[i].Name)
        self.ComboBox_ObjSelection2.addItems(self.TextObj)
        self.ComboBox_ObjSelection2.setCurrentIndex(0)

        # ---- row 3: Sel obj2 ----
        self.Text_Selection2 = QtWidgets.QLabel("Select")
        self.ComboBox_Selection2 = QtWidgets.QComboBox()
        self.TextSelection1 = ["Vertexes","Edges","Faces"]
        self.ComboBox_Selection2.addItems(self.TextSelection1)
        self.ComboBox_Selection2.setCurrentIndex(0)

        # ---- row 4: Note ----
        self.Text_Note = QtWidgets.QLabel("With Vertexes don't work properly")

        # row X, column X, rowspan X, colspan X
        layout.addWidget(self.Text_1_Label,0,0,1,1)
        layout.addWidget(self.ComboBox_ObjSelection1,0,1,1,1)
        layout.addWidget(self.Text_Selection1,1,0,1,1)
        layout.addWidget(self.ComboBox_Selection1,1,1,1,1)
        layout.addWidget(self.Text_2_Label,2,0,1,1)
        layout.addWidget(self.ComboBox_ObjSelection2,2,1,1,1)
        layout.addWidget(self.Text_Selection2,3,0,1,1)
        layout.addWidget(self.ComboBox_Selection2,3,1,1,1)
        layout.addWidget(self.Text_Note,4,0,1,1)

    def accept(self):
        self.ObjSelection1 = FreeCAD.ActiveDocument.Objects[self.ComboBox_ObjSelection1.currentIndex()]
        self.ObjSelection2 = FreeCAD.ActiveDocument.Objects[self.ComboBox_ObjSelection2.currentIndex()]
        self.Selection1 = self.ComboBox_Selection1.currentIndex()
        self.Selection2 = self.ComboBox_Selection2.currentIndex()
        if len(FreeCADGui.Selection.getSelection()) == 0:
            Assembly_TaskPanel.change_color(self, color = (0.0, 1.0, 0.0), size = 5)

        if len(FreeCADGui.Selection.getSelection()) == 2 :
            grafic.grafic()
            Assembly_TaskPanel.change_color(self, color = (0.0, 0.0, 0.0), size = 2)
            FreeCADGui.Control.closeDialog() #close the dialog
        else:
            message = QtWidgets.QMessageBox()
            message.setText('Select object to move and placement')
            message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            message.setDefaultButton(QtWidgets.QMessageBox.Ok)
            message.exec_()
    
    def reject(self):
        FreeCADGui.Control.closeDialog()
        Assembly_TaskPanel.change_color(self, color = (0.0, 0.0, 0.0), size = 2)

    def change_color(self, color = (1.0, 1.0, 1.0), size = 2):
        doc = FreeCADGui.ActiveDocument
        if self.Selection1 == 0: #Vertexes 1 - Cambiamos su color para verlo mejor
            doc.getObject(self.ObjSelection1.Name).PointColor = color
            doc.getObject(self.ObjSelection1.Name).PointSize = size
        if self.Selection2 == 0: #Vertexes 2
            doc.getObject(self.ObjSelection2.Name).PointColor = color
            doc.getObject(self.ObjSelection2.Name).PointSize = size

        if self.Selection1 == 1: #Edges
            doc.getObject(self.ObjSelection1.Name).LineColor = color
            doc.getObject(self.ObjSelection1.Name).LineWidth = size
        if self.Selection2 == 1: #Edges
            doc.getObject(self.ObjSelection2.Name).LineColor = color
            doc.getObject(self.ObjSelection2.Name).LineWidth = size
            
        if self.Selection1 == 2: #Faces
            if color == (0.0, 0.0, 0.0):
                color = (0.8, 0.8, 0.8)
            doc.getObject(self.ObjSelection1.Name).ShapeColor = color
        if self.Selection2 == 2: #Faces
            if color == (0.0, 0.0, 0.0):
                color = (0.8, 0.8, 0.8)
            doc.getObject(self.ObjSelection2.Name).ShapeColor = color

#  _________________________________________________________________
# |                                                                 |
# |                         Ortonormal Axis                         |
# |_________________________________________________________________|
def ortonormal_axis(axis_1, axis_2, axis_3):
    if ((fc_isperp(axis_1,axis_2)==0) or (fc_isperp(axis_2,axis_3)==0) or (fc_isperp(axis_1,axis_3)==0)):
        axis_message()
        return False
    else:
        return True
    
def axis_message():
    axis_message = QtWidgets.QMessageBox()
    axis_message.setText("Please, check the input axes")
    axis_message.setInformativeText("The axes must be perpendicular to each other")
    axis_message.setStandardButtons(QtWidgets.QMessageBox.Ok)
    axis_message.setDefaultButton(QtWidgets.QMessageBox.Ok)
    axis_message.exec_()

#  _________________________________________________________________
# |                                                                 |
# |                             Commands                            |
# |_________________________________________________________________|

FreeCADGui.addCommand('Sk',_SkDirCmd())
FreeCADGui.addCommand('Idle_Pulley_Holder',_IdlePulleyHolderCmd())
FreeCADGui.addCommand('Aluprof_Bracket',_AluprofBracketCmd())
FreeCADGui.addCommand('Motor_Holder',_MotorHolderCmd())
FreeCADGui.addCommand('Motor',_NemaMotorCmd())
FreeCADGui.addCommand('Simple_End_Stop_Holder',_SimpleEndStopHolderCmd())
FreeCADGui.addCommand('LinBearHouse',_LinBearHouseCmd())
FreeCADGui.addCommand('Stop_Holder',_stop_holderCmd())
FreeCADGui.addCommand('Sensor_Holder',_SensorHolder_Cmd())
FreeCADGui.addCommand('Belt_Clamp',_BeltClampCmd())
FreeCADGui.addCommand('Belt_Clamped',_BeltClampedCmd())
FreeCADGui.addCommand('Aluproft',_AluproftCmd()) 
FreeCADGui.addCommand('Bolts, Nuts & Washers',_BoltCmd())  
FreeCADGui.addCommand('Linear_Guide_Block',_LinGuideBlockCmd())

## Opctic
FreeCADGui.addCommand('TubeLense',_TubeLense_Cmd())
FreeCADGui.addCommand('LCB1M_Base',_Lcpb1mBase_Cmd())
FreeCADGui.addCommand('CageCube',_CageCube_Cmd())
FreeCADGui.addCommand('Plate',_Plate_Cmd())
FreeCADGui.addCommand('BreadBoard',_BreadBoard_Cmd())
FreeCADGui.addCommand('PrizLed',_PrizLed_Cmd())
FreeCADGui.addCommand('ThLed30',_ThLed30_Cmd())


## Filter Stage
FreeCADGui.addCommand('Filter_Stage', _FilterStageCmd())
FreeCADGui.addCommand('Filter_Holder',_FilterHolderCmd())
FreeCADGui.addCommand('Tensioner',_TensionerCmd())

## Print
FreeCADGui.addCommand('ChangePosExport',_ChangePosExportCmd())

## Assembly
FreeCADGui.addCommand('Assembly',_AssemlyCmd())

## Test
FreeCADGui.addCommand('test', _testCmD())