# -*- coding: utf-8 -*-
# FreeCAD init script of the Filter Stage module,

# ***************************************************************************
# *   (c) David Muñoz Bernal                                                *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************/

class MakerWorkbench (Workbench):
    """Maker Wokbench to create objects"""
    #  Icon in XPM 16x16
    Icon = "./Resources/icons/Maker_workbench_icon.svg"
    
    # """
    # /* XPM */
    # static char * Filter_Stage_xpm[] = {
    # "16 16 5 1",
    # " 	c None",
    # ".	c #FFFFFF",
    # "+	c #000000",
    # "@	c #7F4F00",
    # "#	c #FFBF00",
    # "................",
    # "...++++++++++++.",
    # "..+@#########++.",
    # ".+@#########+@+.",
    # ".+++++++++++@#+.",
    # ".+#########+##+.",
    # ".+#++###++#+##+.",
    # ".+#+#+#+#+#+##+.",
    # ".+#+##+##+#+##+.",
    # ".+#+#####+#+##+.",
    # ".+#+#####+#+##+.",
    # ".+#+#####+#+##+.",
    # ".+#+#####+#+#@+.",
    # ".+#########+@+..",
    # ".++++++++++++...",
    # "................"};
    # """
    MenuText = "Maker Workbench"
    ToolTip = "Maker Workbench"

    def Initialize(self):
        from PySide2 import QtCore, QtGui
        # import MechatronicGui
        import Gui.Sk_Gui
        import Gui.IdlePulleyHolder_Gui
        import Gui.AluprofBracket_Gui
        import Gui.MotorHolder_Gui
        import Gui.NemaMotor_Gui
        import Gui.SimpleEndStopHolder_Gui
        import Gui.LinBearHouse_Gui
        import Gui.StopHolder_Gui
        import Gui.FilterHolder_Gui
        import Gui.BeltClamp_Gui
        import Gui.SensorHolder_Gui
        import Gui.Aluprof_Gui
        import Gui.LinGuideBlock_Gui
        import Gui.Bolt_Nut_Washer_Gui

        import Gui.TubeLense_Gui
        import Gui.LCPB1M_Gui
        import Gui.Plate_Gui
        import Gui.CageCube_Gui
        import Gui.ThLed30_Gui
        import Gui.PrizLed_Gui
        import Gui.BreadBoard_Gui

        import Gui.FilterStage_Gui
        import Gui.Tensioner_Gui

        import Gui.ChangePos_Gui
        import Gui.Assembly_Gui
        import Gui.test_Gui

        import Gui.New_Point_Gui

        # +-------------------------------+
        # |                               |
        # |   List of mechanical models   |
        # |                               |
        # +-------------------------------+

        partsList = ["Sk",
                     "Idle_Pulley_Holder",
                     "Aluprof_Bracket",
                     "Motor_Holder",
                     "Motor",
                     "Simple_Endstop_Holder",
                     "LinBearHouse",
                     "Stop_Holder",
                     "Filter_Holder",
                     "Belt_Clamp",
                     #  "Belt_Clamped", # Not working properly
                     "Sensor_Holder",
                     "Aluproft",
                     "Linear_Guide_Block",
                     "Bolts, Nuts & Washers"]

        # +-------------------------------+
        # |                               |
        # |   List of optic models        |
        # |                               |
        # +-------------------------------+    

        opticList = ["TubeLense",
                     "LCB1M_Base",
                     "Plate",
                     "CageCube",
                     "ThLed30",
                     "PrizLed",
                     "BreadBoard"]

        # +-------------------------------+
        # |                               |
        # |   List of systems             |
        # |                               |
        # +-------------------------------+

        sysList = ["Filter_Stage",
                   "Tensioner"]

        # +-------------------------------+
        # |                               |
        # |   List of functions           |
        # |                               |
        # +-------------------------------+

        modList = ["ChangePosExport",
                   "Assembly",
                   "New_Internal_Point"]  # ,
        #          "test"]

        # +-------------------------------+
        # |                               |
        # |   Add ToolBars                |
        # |                               |
        # +-------------------------------+

        self.appendToolbar(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Parts")), partsList)
        self.appendToolbar(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Optic")), opticList)
        self.appendToolbar(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Systems")), sysList)
        self.appendToolbar(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Functions")), modList)

        # +-------------------------------+
        # |                               |
        # |   Add Menus                   |
        # |                               |
        # +-------------------------------+

        self.appendMenu(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Parts")), partsList)
        self.appendMenu(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Optic")), opticList)
        self.appendMenu(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Systems")), sysList)
        self.appendMenu(
            str(QtCore.QT_TRANSLATE_NOOP("Maker", "Functions")), modList)
        
        Log('Loalding Maker Workbench... done! \n')
    
    def GetClassName(self):
        return "Gui::PythonWorkbench"


# Add workbench
Gui.addWorkbench(MakerWorkbench())
