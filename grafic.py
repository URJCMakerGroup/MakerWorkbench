# -*- coding: utf-8 -*-
# FreeCAD script to do assembly of mechatronic systems
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

import FreeCAD
import FreeCADGui

def grafic():
    objSelect = FreeCADGui.Selection.getSelection()[0]
    Sel = FreeCADGui.Selection.getSelectionEx()[0].SubObjects[0]
    pos1 = objSelect.getGlobalPlacement().Base
    try:
        p_1 = Sel.CenterOfMass
    except:
        p_1 = Sel.Placement.Base
    #o_1 = Sel.Orientation ------------------------------- DIDN'T KNOW HOW TO CHANGE
    #Relative position of the center respect the point select
    p_ret_1 = FreeCAD.Vector(0,0,0)
    #------------------------------
    if p_1.x >= pos1.x:
        p_ret_1.x = pos1.x - p_1.x
    else:# p_1.x < pos1.x:
        p_ret_1.x = p_1.x - pos1.x
    #------------------------------
    if p_1.y >= pos1.y:
        p_ret_1.y = pos1.y - p_1.y
    else:# p_1.y < pos1.y:
        p_ret_1.y = p_1.y - pos1.y
    #------------------------------
    if p_1.z >= pos1.z:
        p_ret_1.z = pos1.z - p_1.z
    else:# p_1.z < pos1.z:
        p_ret_1.z = p_1.z - pos1.z
    #------------------------------

    objSelect2= FreeCADGui.Selection.getSelection()[1]
    Sel2 = FreeCADGui.Selection.getSelectionEx()[1].SubObjects[0]
    pos2 = objSelect2.getGlobalPlacement().Base
    
    try:
        p_2 = Sel2.CenterOfMass
    except:
        p_2 = Sel2.Placement.Base # don't WORK 
    #o_2 = Sel2.Orientation ------------------------------- DIDN'T KNOW HOW TO CHANGE
    #Relative position of the center respect the edge select
    p_ret_2 = FreeCAD.Vector(0,0,0)
    #------------------------------
    if p_2.x >= pos2.x:
        p_ret_2.x = pos2.x - p_2.x
    else:# p_2.x < pos2.x:
        p_ret_2.x = p_2.x - pos2.x
    #------------------------------
    if p_2.y >= pos2.y:
        p_ret_2.y = pos2.y - p_2.y
    else:# p_2.y < pos2.y:
        p_ret_2.y = p_2.y - pos2.y
    #------------------------------
    if p_2.z >= pos2.z:
        p_ret_2.z = pos2.z - p_2.z
    else:# p_2.z < pos2.z:
        p_ret_2.z = p_2.z - pos2.z
    #------------------------------

    p_final = FreeCAD.Vector(0,0,0)
    #-------------------------------------
    p_final.x = pos1.x + ( p_2.x - p_1.x)
    p_final.y = pos1.y + ( p_2.y - p_1.y)
    p_final.z = pos1.z + ( p_2.z - p_1.z)
    #-------------------------------------

    objSelect.Placement.Base = (p_final)