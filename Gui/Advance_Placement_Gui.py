import PySide2
from PySide2 import QtWidgets

import FreeCAD
import Draft

from Gui.function_Gui import set_place, ortonormal_axis
from NuevaClase import Obj3D

class Advance_Placement_TaskPanel:
    def __init__(self,obj_task):
        self.obj_task = obj_task
        self.obj_list = []

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
            if hasattr(obj, 'd_o'):
                self.obj_list.append(obj)
                self.obj_combo.addItem(obj.Name)
            else: pass
        self.obj_combo.currentTextChanged.connect(self.set_points)

        main_layout.addLayout(obj_layout)
        main_layout.addLayout(points_layout)
        main_layout.addLayout(button_layout)
    
    def set_points(self):
        self.obj_d.clear()
        self.obj_w.clear()
        self.obj_h.clear()
        obj = self.obj_list[self.obj_combo.currentIndex()-1]
        
        if hasattr(obj, "d_o"):
            if obj.d0_cen == 0:
                for p in range(0,len(obj.d_o)):
                    self.obj_d.addItem(str(p))
            elif obj.d0_cen == 1:
                for p in range(-len(obj.d_o)+1,len(obj.d_o)): # +1 is necessary to eliminate the 0 value duplicate
                    self.obj_d.addItem(str(p)) 
        else: pass
        if hasattr(obj, "w_o"):
            if obj.w0_cen == 0:
                for p in range(0,len(obj.w_o)):
                    self.obj_w.addItem(str(p))
            elif obj.w0_cen == 1:
                for p in range(-len(obj.w_o)+1,len(obj.w_o)):
                    self.obj_w.addItem(str(p))
        else: pass
        if hasattr(obj, "h_o"):
            if obj.h0_cen == 0:
                for p in range(0,len(obj.h_o)):
                    self.obj_h.addItem(str(p))
            elif obj.h0_cen == 1:
                for p in range(-len(obj.h_o)+1,len(obj.h_o)):
                    self.obj_h.addItem(str(p))
        else: pass

    def button_clicked(self):
        obj_selected = self.obj_list[self.obj_combo.currentIndex()-1]
        d = self.obj_d.currentText()
        w = self.obj_w.currentText()
        h = self.obj_h.currentText()        
        point = obj_selected.Placement.Base + self.get_point(obj_selected, int(d), int(w), int(h))
        set_place(self.obj_task, point.x, point.y, point.z)

    def show_point(self):
        obj_selected = self.obj_list[self.obj_combo.currentIndex()-1]
        d = self.obj_d.currentText()
        w = self.obj_w.currentText()
        h = self.obj_h.currentText()

        point = obj_selected.Placement.Base + self.get_point(obj_selected, int(d), int(w), int(h))

        for obj in FreeCAD.ActiveDocument.Objects:
            if 'Point_d_w_h' == obj.Name:
                FreeCAD.ActiveDocument.removeObject('Point_d_w_h')

        Draft.makePoint(X=point.x, Y=point.y, Z=point.z, name='Point_d_w_h', point_size=10, color=(0,1,0))
        FreeCAD.ActiveDocument.recompute()

    def get_point(self, obj, d, w, h):
        if obj.d0_cen == 1:
            if d <= 0: # pos_d is negative 
                point_d = -obj.d_o[abs(d)]
            else:
                point_d = obj.d_o[d]
        else:
            point_d = obj.d_o[d]

        if obj.w0_cen == 1:
            if w <= 0:
                point_w = -obj.w_o[abs(w)]
            else:
                point_w = obj.w_o[w]
        else:
            point_w = obj.w_o[w]

        
        if obj.h0_cen == 1:
            if h <= 0:
                point_h = -obj.h_o[abs(h)]
            else:
                point_h = obj.h_o[h]
        else:
            point_h = obj.h_o[h]
        
        point = point_d + point_w + point_h
        return point

