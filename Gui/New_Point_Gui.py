import PySide2
from PySide2 import QtCore, QtGui, QtWidgets

import os
import FreeCAD
import FreeCADGui
import logging

__dir__ = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class _New_Point_Cmd:
    """
    Gui to create new points 
    """
    def Activated(self):
        FreeCADGui.Control.showDialog(New_Point_Dialog()) 

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Add new internal point',
            'Add new internal point')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '',
            'MenuText': MenuText,
            'ToolTip': ToolTip}
    def IsActive(self):
        return not FreeCAD.ActiveDocument is None 

class New_Point_Dialog:
    def __init__(self):
        self.Object = Set_object_TaskPanel()
        self.Axis = Set_axis_TaskPanel(self.Object)
        self.Points = Set_points_TaskPanel(self.Object, self.Axis)
        self.form = [self.Object.widget, self.Axis.widget, self.Points.widget]

    def accept(self): 
        pass

class Set_object_TaskPanel:
    def __init__(self):
        self.obj_list = []
        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Select Object")
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget.setLayout(main_layout)

        obj_layout = QtWidgets.QHBoxLayout()
        obj_label = QtWidgets.QLabel()
        obj_label.setText("Select Object")
        self.obj_combo = QtWidgets.QComboBox()
        # self.obj_combo.addItem('') #add initial null value

        obj_layout.addWidget(obj_label)
        obj_layout.addWidget(self.obj_combo)

        for obj in FreeCAD.ActiveDocument.Objects: # Save the objects name
            self.obj_list.append(obj)
            self.obj_combo.addItem(obj.Name)
        if len(self.obj_list) == 0:
            self.obj_list = [""]
            self.obj_combo.addItem('')

        main_layout.addLayout(obj_layout)

class Set_axis_TaskPanel:
    def __init__(self, Object):
        self.Object = Object

        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Set internal axis")
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget.setLayout(main_layout)

        main2_layout = QtWidgets.QHBoxLayout()
        axis_layout = QtWidgets.QVBoxLayout()
        values_layout = QtWidgets.QVBoxLayout()

        main_layout.addLayout(main2_layout)
        main2_layout.addLayout(axis_layout)
        main2_layout.addLayout(values_layout)

        # axis_layout
        ## none
        axis_n_layout = QtWidgets.QHBoxLayout()
        axis_n_label = QtWidgets.QLabel()
        axis_n_label.setText(" ")

        axis_n_layout.addWidget(axis_n_label)

        ## axis d
        axis_d_layout = QtWidgets.QHBoxLayout()
        axis_d_label = QtWidgets.QLabel()
        axis_d_label.setText("axis d")

        axis_d_layout.addWidget(axis_d_label)
        
        ## axis w
        axis_w_layout = QtWidgets.QHBoxLayout()
        axis_w_label = QtWidgets.QLabel()
        axis_w_label.setText("axis w")

        axis_w_layout.addWidget(axis_w_label)
        
        ## axis h
        axis_h_layout = QtWidgets.QHBoxLayout()
        axis_h_label = QtWidgets.QLabel()
        axis_h_label.setText("axis h")

        axis_h_layout.addWidget(axis_h_label)

        axis_layout.addLayout(axis_n_layout)
        axis_layout.addLayout(axis_d_layout)
        axis_layout.addLayout(axis_w_layout)
        axis_layout.addLayout(axis_h_layout)

        # values_layout
        points_layout = QtWidgets.QHBoxLayout()
        values_layout.addLayout(points_layout)
        ## x
        points_x_layout = QtWidgets.QVBoxLayout()
        point_x_label = QtWidgets.QLabel()
        point_x_label.setText("x")
        point_x_label.setAlignment(QtCore.Qt.AlignCenter)

        self.d_x = QtWidgets.QDoubleSpinBox()
        self.d_x.setMinimum(-999999) 
        self.d_x.setMaximum(999999)

        self.w_x = QtWidgets.QDoubleSpinBox()
        self.w_x.setMinimum(-999999) 
        self.w_x.setMaximum(999999)

        self.h_x = QtWidgets.QDoubleSpinBox()
        self.h_x.setMinimum(-999999) 
        self.h_x.setMaximum(999999)

        points_x_layout.addWidget(point_x_label)
        points_x_layout.addWidget(self.d_x)
        points_x_layout.addWidget(self.w_x)
        points_x_layout.addWidget(self.h_x)

        ## y
        points_y_layout = QtWidgets.QVBoxLayout()
        point_y_label = QtWidgets.QLabel()
        point_y_label.setText("y")
        point_y_label.setAlignment(QtCore.Qt.AlignCenter)

        self.d_y = QtWidgets.QDoubleSpinBox()
        self.d_y.setMinimum(-999999) 
        self.d_y.setMaximum(999999)

        self.w_y = QtWidgets.QDoubleSpinBox()
        self.w_y.setMinimum(-999999) 
        self.w_y.setMaximum(999999)

        self.h_y = QtWidgets.QDoubleSpinBox()
        self.h_y.setMinimum(-999999) 
        self.h_y.setMaximum(999999)

        points_y_layout.addWidget(point_y_label)
        points_y_layout.addWidget(self.d_y)
        points_y_layout.addWidget(self.w_y)
        points_y_layout.addWidget(self.h_y)

        ## z
        points_z_layout = QtWidgets.QVBoxLayout()
        point_z_label = QtWidgets.QLabel()
        point_z_label.setText("z")
        point_z_label.setAlignment(QtCore.Qt.AlignCenter)

        self.d_z = QtWidgets.QDoubleSpinBox()
        self.d_z.setMinimum(-999999) 
        self.d_z.setMaximum(999999)

        self.w_z = QtWidgets.QDoubleSpinBox()
        self.w_z.setMinimum(-999999) 
        self.w_z.setMaximum(999999)

        self.h_z = QtWidgets.QDoubleSpinBox()
        self.h_z.setMinimum(-999999) 
        self.h_z.setMaximum(999999)

        points_z_layout.addWidget(point_z_label)
        points_z_layout.addWidget(self.d_z)
        points_z_layout.addWidget(self.w_z)
        points_z_layout.addWidget(self.h_z)

        # add layouts to the values
        points_layout.addLayout(points_x_layout)
        points_layout.addLayout(points_y_layout)
        points_layout.addLayout(points_z_layout)

        button_layout = QtWidgets.QHBoxLayout()
        btn_new_axes = QtWidgets.QPushButton("Add internal axes to the model")
        button_layout.addWidget(btn_new_axes)

        main_layout.addLayout(button_layout)
        # Conect the button 
        btn_new_axes.clicked.connect(self.new_axes) 

        obj = self.Object.obj_list[self.Object.obj_combo.currentIndex()]
        if hasattr(obj,'axis_d'):
            self.d_x.setValue(obj.axis_d.x)
            self.d_y.setValue(obj.axis_d.y)
            self.d_z.setValue(obj.axis_d.z)
        else:
            self.d_x.setValue(0)
            self.d_y.setValue(0)
            self.d_z.setValue(0)
        if hasattr(obj,'axis_w'):
            self.w_x.setValue(obj.axis_w.x)
            self.w_y.setValue(obj.axis_w.y)
            self.w_z.setValue(obj.axis_w.z)
        else:
            self.w_x.setValue(0)
            self.w_y.setValue(0)
            self.w_z.setValue(0)
        if hasattr(obj,'axis_h'):
            self.h_x.setValue(obj.axis_h.x)
            self.h_y.setValue(obj.axis_h.y)
            self.h_z.setValue(obj.axis_h.z)
        else:
            self.h_x.setValue(0)
            self.h_y.setValue(0)
            self.h_z.setValue(0)

        self.Object.obj_combo.currentTextChanged.connect(self.change_axis)
        
    def change_axis(self):
        obj = self.Object.obj_list[self.Object.obj_combo.currentIndex()]
        if hasattr(obj,'axis_d'):
            self.d_x.setValue(obj.axis_d.x)
            self.d_y.setValue(obj.axis_d.y)
            self.d_z.setValue(obj.axis_d.z)
        else:
            self.d_x.setValue(0)
            self.d_y.setValue(0)
            self.d_z.setValue(0)
        if hasattr(obj,'axis_w'):
            self.w_x.setValue(obj.axis_w.x)
            self.w_y.setValue(obj.axis_w.y)
            self.w_z.setValue(obj.axis_w.z)
        else:
            self.w_x.setValue(0)
            self.w_y.setValue(0)
            self.w_z.setValue(0)
        if hasattr(obj,'axis_h'):
            self.h_x.setValue(obj.axis_h.x)
            self.h_y.setValue(obj.axis_h.y)
            self.h_z.setValue(obj.axis_h.z)
        else:
            self.h_x.setValue(0)
            self.h_y.setValue(0)
            self.h_z.setValue(0)

    def new_axes(self):
        if int(FreeCAD.Version()[1])>=19.:  
            # logger.warning('FreeCAD 19 or newer')
            obj = self.Object.obj_list[self.Object.obj_combo.currentIndex()]

            axis_d = FreeCAD.Vector(self.d_x.value(),self.d_y.value(),self.d_z.value())
            axis_w = FreeCAD.Vector(self.w_x.value(),self.w_y.value(),self.w_z.value())
            axis_h = FreeCAD.Vector(self.h_x.value(),self.h_y.value(),self.h_z.value())
            if 'axis_d' in obj.PropertiesList:
                obj.axis_d = axis_d
            else:
                obj.addProperty("App::PropertyVector","axis_d",obj.Name,"Internal axis d",4).axis_d = axis_d
            
            if 'axis_w' in obj.PropertiesList:
                obj.axis_w = axis_w
            else:
                obj.addProperty("App::PropertyVector","axis_w",obj.Name,"Internal axis w",4).axis_w = axis_w
            
            if 'axis_h' in obj.PropertiesList:
                obj.axis_h = axis_h
            else:
                obj.addProperty("App::PropertyVector","axis_h",obj.Name,"Internal axis h",4).axis_h = axis_h
        else:
            logger.warning('FreeCAD version need to be 19 or newer to use this utility')

class Set_points_TaskPanel:
    def __init__(self, Object, Axis):
        self.Object = Object
        self.Axis = Axis

        self.widget = QtWidgets.QWidget()
        self.widget.setWindowTitle("Set internal points")
        main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.widget.setLayout(main_layout)

        axis_layout = QtWidgets.QHBoxLayout()
        axis_label = QtWidgets.QLabel()
        axis_label.setText("Select axis")
        self.axis_combo = QtWidgets.QComboBox()
        self.axis_combo.addItems(["d","w","h"]) #add the axis (d,w,h)

        axis_layout.addWidget(axis_label)
        axis_layout.addWidget(self.axis_combo)

        main_layout.addLayout(axis_layout)

        values_layout = QtWidgets.QHBoxLayout()
        value_label = QtWidgets.QLabel()
        value_label.setText("Value")
        self.value_data = QtWidgets.QDoubleSpinBox()
        self.value_data.setValue(0)

        values_layout.addWidget(value_label)
        values_layout.addWidget(self.value_data)

        main_layout.addLayout(values_layout)

        button_layout = QtWidgets.QHBoxLayout()
        btn_new_point = QtWidgets.QPushButton("Add internal point to the model")
        button_layout.addWidget(btn_new_point)

        main_layout.addLayout(button_layout)
        # Conect the button 
        btn_new_point.clicked.connect(self.new_point) 

    def new_point(self):
        if int(FreeCAD.Version()[1])>=19.:  
            # logger.warning('FreeCAD 19 or newer')
            obj = self.Object.obj_list[self.Object.obj_combo.currentIndex()]
            axis = self.axis_combo.currentText()
            value = self.value_data.value()
            if axis == 'd':
                if 'axis_d' in obj.PropertiesList:
                    vec = obj.axis_d * value
                    if 'd_o' in obj.PropertiesList:
                        base = obj.d_o
                        base.append(vec)
                        obj.d_o = base
                    else:
                        obj.addProperty("App::PropertyVectorList","d_o",obj.Name,"Points o to d",4).d_o = [vec]
                else:
                    # mensaje de error para que el usuario fije unos ejes
                    self.message()
            elif axis == 'w':
                if 'axis_w' in obj.PropertiesList:
                    vec = obj.axis_w * value
                    if 'w_o' in obj.PropertiesList:
                        base = obj.w_o
                        base.append(vec)
                        obj.w_o = base
                    else:
                        obj.addProperty("App::PropertyVectorList","w_o",obj.Name,"Points o to w",4).w_o = [vec]
                else:
                    # mensaje de error para que el usuario fije unos ejes
                    self.message()
            elif axis == 'h':
                if 'axis_h' in obj.PropertiesList:
                    vec = obj.axis_h * value
                    if 'h_o' in obj.PropertiesList:
                        base = obj.h_o
                        base.append(vec)
                        obj.h_o = base
                    else:
                        obj.addProperty("App::PropertyVectorList","h_o",obj.Name,"Points o to h",4).h_o = [vec]
                else:
                    # mensaje de error para que el usuario fije unos ejes
                    self.message()
            else:
                # logger.error('Not working!!')
                pass
        else:
            logger.warning('FreeCAD version need to be 19 or newer to use this utility')

    def message(self):
        message = QtWidgets.QMessageBox()
        message.setText('The axes are not defined yet. Please set the axes first')
        message.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message.setDefaultButton(QtWidgets.QMessageBox.Ok)
        message.exec_()
# Command
FreeCADGui.addCommand('New_Internal_Point', _New_Point_Cmd())