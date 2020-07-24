import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg
import os
import FreeCAD
import FreeCADGui

from grafic import grafic

__dir__ = os.path.dirname(__file__)

class _Assembly_Cmd:
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
        
    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Assembly',
            'Assembly')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            '',
            '')
        return {
            'Pixmap': __dir__ + '/../icons/Assembly_cmd.svg',
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
            grafic()
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

# Command
FreeCADGui.addCommand('Assembly',_Assembly_Cmd())