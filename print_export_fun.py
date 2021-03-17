# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# -- Function Print and Export Object
# ----------------------------------------------------------------------------
# -- (c) David Muñoz Bernal
# ----------------------------------------------------------------------------
# -- This function set the object to the print position and export the object.
import os
import sys
import FreeCAD
import FreeCADGui
import Mesh
import MeshPart
import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
import kparts


def print_export(obj_select):
    show_message = True
    place_old = obj_select.Placement

    # _________Motor_Holder_________
    if 'motorholder' in obj_select.Name or 'nema_holder' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 180) 
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Idler_Tensioner_________
    elif 'idler_tensioner' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Tensioner_Holder_________
    elif 'tensioner_holder' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Filter_Holder_________
    elif 'filter_holder' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Nema_Holder_________
    # elif 'nema_holder' in obj_select.Name:
    #    pos = obj_select.Placement.Base
    #    rot = FreeCAD.Rotation(FreeCAD.Vector(0,1,0),180) 
    #    centre = FreeCAD.Vector(0,0,0)

    # _________Linbearhouse_________
    elif 'linbear' in obj_select.Name:
        if 'top' in obj_select.Name:
            pos = obj_select.Placement.Base
            rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 180)
            centre = FreeCAD.Vector(0, 0, 0)

        elif 'bot' in obj_select.Name:
            pos = obj_select.Placement.Base
            rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
            centre = FreeCAD.Vector(0, 0, 0)

        else:
            message = QtWidgets.QMessageBox()
            message.Critical()
            message.setWindowTitle('Critial error')
            message.setText('Not position set for this model')
            message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            message.setDefaultButton(QtWidgets.QMessageBox.Ok)
            message.exec_()

    # _________Bracket_________
    elif 'bracket' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)
    
    # _________Bracket_3_________
    # elif bracket3 in obj_select.Name:
    #    pos = obj_select.Placement.Base
    #    rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,0),0)
    #    centre = FreeCAD.Vector(0,0,0)

    # _________Bracket_Twin_________
    # elif bracket_twin in obj_select.Name:
    #    pos = obj_select.Placement.Base
    #    rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,0),0)
    #    centre = FreeCAD.Vector(0,0,0)

    # _________Shaft_________
    elif 'shaft' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________IdlepulleyHold_________
    elif 'idlepulleyhold' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Simple_End_Stop_Holder_________
    elif 'simple_endstop_holder' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Stop_Holder_________
    elif 'stop_holder' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Belt_Clamp_________
    elif 'belt_clamp' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Sensor_Holder_________
    elif 'sensorholder' in obj_select.Name:
        pos = obj_select.Placement.Base
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
        centre = FreeCAD.Vector(0, 0, 0)

    # _________Not_Name_________
    else:
        message = QtWidgets.QMessageBox()
        message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message.setWindowTitle('Sorry')
        message.setText('This object is not a workbench object.\n')
        message.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message.setDefaultButton(QtWidgets.QMessageBox.Ok)
        message.exec_()
        show_message = False

    #######################################################
    # _________Message_And_Change_________
    if show_message is True:
        obj_select.Placement = FreeCAD.Placement(pos, rot, centre)
        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        # _________EXPORT_________
        # Open the file explorer to set the folder
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(QtWidgets.QFileDialog(), "Select directory", "c:/",
                                                                 QtWidgets.QFileDialog.ShowDirsOnly)
        if folder_name is not "":
            # take the path and export the object
            stl_file_name = str(folder_name) + "/" + obj_select.Name + ".stl"
            mesh_shp = MeshPart.meshFromShape(obj_select.Shape,
                                              LinearDeflection=kparts.LIN_DEFL,
                                              AngularDeflection=kparts.ANG_DEFL)
            mesh_shp.write(stl_file_name)
            del mesh_shp

            obj_select.Placement = place_old
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Icon.Information)
            message.setWindowTitle('Congratulations')
            message.setText("You export " + obj_select.Name + " in " + folder_name)
            message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            message.setDefaultButton(QtWidgets.QMessageBox.Ok)
            message.exec_()
        else:
            obj_select.Placement = place_old
            message = QtWidgets.QMessageBox()
            message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            message.setWindowTitle('Error')
            message.setText("Please, select a correct folder to export " + obj_select.Name)
            message.setStandardButtons(QtWidgets.QMessageBox.Ok)
            message.setDefaultButton(QtWidgets.QMessageBox.Ok)
            message.exec_()
