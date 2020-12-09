# ----------------------------------------------------------------------------
# -- Belt Clamp Tensioner
# -- comps library
# -- Python classes and functions to make belt tensioner in FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD
import Part
import Draft
import DraftVecUtils
import logging
import inspect
import Mesh
import MeshPart


import os
# can be taken away after debugging
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)

import kcomp  # import material constants and other constants
import fcfun      # import my functions for freecad
import kparts 
import shp_clss
import fc_clss

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl
from kcomp import TOL

stl_dir = "/stl/"

logger = logging.getLogger(__name__)

# Belt dimensions:

# space for the 2 belts to clamp them
# the GT2 belt is 1.38mm width. 2 together facing teeth will be about 2mm
# I make it 2.8mm
# Internal Width of the Clamp Block
CB_IW = 2.8
# Width of the exterior clamp blocks (Y axis)
CB_W = 4.0
# Length of the clamp blocks (X axis)
CB_L = 12.0
# GT2 height is 6 mm, making the height 8mm
C_H = 8.0
# GT2 Clamp Cylinder radius
CCYL_R = 4.0
# separation between the clamp blocks and the clamp cylinder
CS = 3.0

# separation of the nut hole from the edge
NUT_HOLE_EDGSEP = 3 


# --------------------------- belt clamp and tensioner
# radius of the cylinder
#""                           
#          TOPVIEW                    
#                CLAMPBLOCK          
#                    CB             
#                    ____     
#           CB_W  {  XXXX       ___
#           CB_IW {  ____      /   \
# 0,1 or 2: CB_MW {  XXXX      |   |   CCYL: CLAMPCYL 
#           CB_IW {  ____      \___/
#           CB_W  {  XXXX     
#        
#                    CB_L  CS
#
#
#    Y A  (width)
#      |
#      |---> X (length)
#
#
# Arguments:
#  midblock: 0 or 1. It will add a none/single width middle block
#                   In the future I may consider a double middle block (2)
#  base_h:  height of the base


# Attributes:
# fco : the FreeCAD Object of the belt clamp
# fco_cont : the FreeCAD object of the belt clamp offset. To make a cut
#              on the FreeCAD object where the belt tensioner will be.


class Gt2BeltClamp (object):

    # space for the 2 belts to clamp them
    # the GT2 belt is 1.38mm width. 2 together facing teeth will be about 2mm
    # I make it 2.8mm
    # Internal Width of the Clamp Block
    CB_IW = 2.8
    # Width of the exterior clamp blocks (Y axis)
    CB_W = 4.0
    # Length of the clamp blocks (X axis)
    CB_L = 12.0
    # GT2 height is 6 mm, making the height 8mm
    C_H = 8.0
    # GT2 Clamp Cylinder radius
    CCYL_R = 4.0
    # separation between the clamp blocks and the clamp cylinder
    CS = 3.0

    # separation of the nut hole from the edge
    NUT_HOLE_EDGSEP = 3 


    """
    how much the rail is inside

     ________________________________________________    
    |        
    |   __________________________
     \                        ____ CBASERAILIND 
      |       
     /  _____ CBASE_RAIL ___
    |
    |_________________________ CBASE_WALL _________ CBASE_H

    |-|
      CBASERAILIND_SIG (it is 45 degrees). SIG: can be + or -

    if midblock > 0 this will be the indentation, 
    if midblock == 0 it will be outward, like this:
        _________
       |         |
      /           \ 
     |             |
      \           /
       |_________|
      
    """
  
    CBASE_L = CB_L + CS + 2*CCYL_R

    def __init__(self, base_h, midblock, name):
        doc = FreeCAD.ActiveDocument
        self.base_place = (0,0,0)
        # Clamp base
        self.CBASE_H = base_h
        # divides how much is rail and how much is wall
        # It has to be greater than 1. If it is 1, there is no wall.
        # if it is 2. Half is wall, half is indent
        self.CBASE_RAIL_DIV = 1.6 #2.0
        self.CBASE_RAIL = self.CBASE_H / self.CBASE_RAIL_DIV # rail for the base
        # the part that is wall, divided by 2, because one goes at the bottom
        # and the other on top
        # rail for the base
        self.CBASE_WALL = (self.CBASE_H - self.CBASE_RAIL)/2.0 
        # Indentation, if midblock == 0, the Indentation is negative, which
        # means it will be outward, otherwise, inward
        self.CBASERAILIND = self.CBASE_RAIL/3.0

        self.midblock = midblock
        # Width of the interior/middle clamp blocks
        self.CB_MW = midblock * self.CB_W
        if midblock == 0:
            self.CBASE_W =     self.CB_IW + 2 * self.CB_W 
            self.CBASERAILIND_SIG = - self.CBASERAILIND 
            # Since the indentation is outwards, we have to add it
            self.TotW = self.CBASE_W + 2 *  self.CBASERAILIND
            # external indent, so all the internal elements have to have this
            # nternal offset. In Y axis
            self.extind = self.CBASERAILIND 
        else:
            self.CBASE_W = 2 * self.CB_IW + 2 * self.CB_W + self.CB_MW
            self.CBASERAILIND_SIG = self.CBASERAILIND 
            # Since the indentation is inward, it is just the base
            self.TotW = self.CBASE_W 
            # no external indent, so the internal elements don't have to have 
            # this internal offset
            self.extind = 0
  
        gt2_clamp_list = []
        # we make it using points-plane and extrusions
        #gt2_base =addBox (self.CBASE_L, self.CBASE_W, self.CBASE_H, "gt2_base")
        gt2_cb_1 = addBox (self.CB_L, self.CB_W, self.C_H+1, name + "_cb1")
        gt2_cb_1.Placement.Base = FreeCAD.Vector (self.CBASE_L-self.CB_L,
                                                  self.extind,
                                                  self.CBASE_H-1)
        gt2_clamp_list.append (gt2_cb_1)
        if midblock > 0:
          gt2_cb_2 = addBox (self.CB_L, self.CB_MW, self.C_H+1, name + "_cb2")
          gt2_cb_2.Placement.Base = FreeCAD.Vector (self.CBASE_L-self.CB_L,
		                                   self.CB_W + self.CB_IW + self.extind,
		                                   self.CBASE_H-1)
          gt2_clamp_list.append (gt2_cb_2)

        gt2_cb_3 = addBox (self.CB_L, self.CB_W, self.C_H + 1, name + "_cb3")
        gt2_cb_3.Placement.Base = FreeCAD.Vector (self.CBASE_L-self.CB_L,
                                        self.CBASE_W - self.CB_W + self.extind,
		                                self.CBASE_H-1)
        gt2_clamp_list.append (gt2_cb_3)
 
        gt2_cyl = fcfun.addCyl (self.CCYL_R,  self.C_H + 1, name + "_cyl")
        gt2_cyl.Placement.Base = FreeCAD.Vector (self.CCYL_R, 
                                             self.CBASE_W/2 + self.extind,
                                             self.CBASE_H-1)
        gt2_clamp_list.append (gt2_cyl)

        # base
        # calling to the method that gets a list of the points to make 
        # the polygon of the base
        #gt2_base_list = self.get_base_list_v()
        # doing this because the carriage is already printed, so I am going
        # to make the base smaller to fit. CHANGE to the upper sentence
        gt2_base_list = self.get_base_list_v(offs_y = -TOL/2, offs_z = - TOL)
        """
        gt2_base_plane_yz = Part.makePolygon(gt2_base_list)
        gt2_base = gt2_base_plane_xy.extrude(FreeCAD.Vector(self.CBASE_L,0,0))
        """
        gt2_base_plane_yz = doc.addObject("Part::Polygon",
                                           name + "base_plane_yz")
        gt2_base_plane_yz.Nodes = gt2_base_list
        gt2_base_plane_yz.Close = True
        gt2_base = doc.addObject("Part::Extrusion",
                                           name + "extr_base")
        gt2_base.Base = gt2_base_plane_yz
        gt2_base.Dir = (self.CBASE_L,0,0)
        gt2_base.Solid = True

        gt2_clamp_list.append(gt2_base)

        gt2_clamp_basic = doc.addObject("Part::MultiFuse", name + "clamp_base")
        gt2_clamp_basic.Shapes = gt2_clamp_list

        # creation of the same base, but with a little offset to be able to 
        # cut the piece where it will be inserted
        #gt2_baseof_list = self.get_base_list_v(offs_y = TOL, offs_z = TOL/2.0)
        # CHANGE TO THE UPPER SENTENCE
        gt2_baseof_list = self.get_base_list_v(offs_y = TOL, offs_z = 0)
        gt2_baseof_plane_yz = doc.addObject("Part::Polygon",
                                           name + "_baseof_plane_yz")
        gt2_baseof_plane_yz.Nodes = gt2_baseof_list
        gt2_baseof_plane_yz.Close = True
        gt2_baseof = doc.addObject("Part::Extrusion",
                                   name + "_baseof")
        gt2_baseof.Base = gt2_baseof_plane_yz
        gt2_baseof.Dir = (self.CBASE_L,0,0)
        gt2_baseof.Solid = True

        self.fco_cont = gt2_baseof

        # hole for the leadscrew bolt
        # the head is longer because it can be inserted deeper into the piece
        # so a shorter bolt will be needed
        gt2_base_lscrew = fcfun.addBolt (kcomp.M3_SHANK_R_TOL, self.CBASE_L,
                                   kcomp.M3_HEAD_R_TOL, 2.5*kcomp.M3_HEAD_L,
                                   extra = 1, support = 0,
                                   name= name + "_base_lscrew")
    
        gt2_base_lscrew.Placement.Base = FreeCAD.Vector (self.CBASE_L,
                                                self.CBASE_W/2.0 + self.extind,
                                                self.CBASE_H/2.0)
        gt2_base_lscrew.Placement.Rotation = FreeCAD.Rotation (VY, -90)

        # ------------ hole for a nut, also M3, for the leadscrew 
        gt2_base_lscrew_nut = doc.addObject("Part::Prism", 
                                            name + "_base_lscrew_nut")
        gt2_base_lscrew_nut.Polygon = 6
        gt2_base_lscrew_nut.Circumradius = kcomp.M3_NUT_R_TOL
        gt2_base_lscrew_nut.Height = kcomp.M3NUT_HOLE_H 
        gt2_base_lscrew_nut.Placement.Rotation = \
                                      gt2_base_lscrew.Placement.Rotation 
                  # + TOL so it will be a little bit higher, so more room
        gt2_base_lscrew_nut.Placement.Base = FreeCAD.Vector (
                  #(self.CBASE_L-kcomp.M3_HEAD_L)/2.0 - kcomp.M3NUT_HOLE_H/2.0,
                               self.NUT_HOLE_EDGSEP,
                               self.CBASE_W/2.0 + self.extind,
                               self.CBASE_H/2.0 + TOL) 
        gt2_base_lscrew_nut.Placement.Rotation = FreeCAD.Rotation (VY, 90)
        # ------------ hole to reach out the nut hole
 
        # X is the length: M3NUT_HOLE_H. Y is the width. M3_2APOT_TOL
        gt2_base_lscrew_nut2 = addBox (kcomp.M3NUT_HOLE_H,
                                       kcomp.M3_2APOT_TOL,
                                       self.CBASE_H/2.0 + TOL,
                                       name + "_base_lscrew_nut2")
        gt2_base_lscrew_nut2.Placement.Base = (
                    #((self.CBASE_L-kcomp.M3_HEAD_L) - kcomp.M3NUT_HOLE_H)/2.0,
                       self.NUT_HOLE_EDGSEP,
                       (self.CBASE_W - kcomp.M3_2APOT_TOL)/2.0 + self.extind,
                       0)

        gt2_base_holes_l = [ gt2_base_lscrew,
                             gt2_base_lscrew_nut,
                             gt2_base_lscrew_nut2]

        # fuse the holes
        gt2_clamp_holes = doc.addObject("Part::MultiFuse", name + "_clamp_hole")
        gt2_clamp_holes.Shapes = gt2_base_holes_l
        # Substract the holes 
        gt2_clamp = doc.addObject("Part::Cut", name)
        gt2_clamp.Base = gt2_clamp_basic
        gt2_clamp.Tool = gt2_clamp_holes

        self.fco = gt2_clamp   # the FreeCad Object

    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.fco.Placement.Base = FreeCAD.Vector(position)
        self.fco_cont.Placement.Base = FreeCAD.Vector(position)

    # --------------------------------------------------------------------
    # obtains the list of vectors for the base of the clamp
    # offs_y: if zero it takes normal points
    # offs_z added because it didn't fit
    # offs_z: if zero it takes normal points
    #  CBASERAILIND_SIG <0:              CBASERAILIND_SIG > 0
    #  lv5         _________               ___________
    #  lv4        |         |             |
    #  lv3       /           \             \ 
    #  lv2      |             |             |
    #  lv1       \           /             / 
    #  lv0        |_________|             |_
    #         
    #
    #
    def get_base_list_v(self, offs_y = 0, offs_z = 0):

        if self.CBASERAILIND_SIG < 0:
            offs_zsig = - offs_z
        else:
            offs_zsig =  offs_z

        # Points that make the shape of the base
        # left side (offs is negative
        gt2_base_lv00 = FreeCAD.Vector (0,
                                        0 - offs_y,
                                        0)
        # offs_z higher when CBASERAILIND_SIG > 0
        gt2_base_lv01 = FreeCAD.Vector (0,
                                        0 - offs_y,
                                        self.CBASE_WALL + offs_zsig)
        gt2_base_lv02 = FreeCAD.Vector (
                                0,
                                self.CBASERAILIND_SIG - offs_y,
                                self.CBASE_WALL + self.CBASERAILIND + offs_zsig)
        # offs_z negative (lower)
        gt2_base_lv03 = FreeCAD.Vector (0,
                            self.CBASERAILIND_SIG - offs_y,
                            self.CBASE_WALL + 2*self.CBASERAILIND - offs_zsig)
        gt2_base_lv04 = FreeCAD.Vector (0,0 - offs_y,
                                self.CBASE_WALL + self.CBASE_RAIL - offs_zsig)
        gt2_base_lv05 = FreeCAD.Vector (0,0 - offs_y,
                                        self.CBASE_H)
        # right side (offs_y is positive
        gt2_base_rv00 = FreeCAD.Vector (0,
                                        self.CBASE_W + offs_y,
                                        0)
        gt2_base_rv01 = FreeCAD.Vector (0,
                                        self.CBASE_W + offs_y,
                                        self.CBASE_WALL + offs_zsig)
        gt2_base_rv02 = FreeCAD.Vector (0,
                               self.CBASE_W - self.CBASERAILIND_SIG + offs_y,
                               self.CBASE_WALL + self.CBASERAILIND + offs_zsig)
        gt2_base_rv03 = FreeCAD.Vector (0,
                             self.CBASE_W - self.CBASERAILIND_SIG + offs_y,
                             self.CBASE_WALL + 2*self.CBASERAILIND - offs_zsig)
        gt2_base_rv04 = FreeCAD.Vector (0,
                             self.CBASE_W + offs_y,
                             self.CBASE_WALL + self.CBASE_RAIL - offs_zsig)
        gt2_base_rv05 = FreeCAD.Vector (0,
                                        self.CBASE_W + offs_y,
                                        self.CBASE_H)
    
        gt2_base_list = [
                         gt2_base_lv00,
                         gt2_base_lv01,
                         gt2_base_lv02,
                         gt2_base_lv03,
                         gt2_base_lv04,
                         gt2_base_lv05,
                         gt2_base_rv05,
                         gt2_base_rv04,
                         gt2_base_rv03,
                         gt2_base_rv02,
                         gt2_base_rv01,
                         gt2_base_rv00
                        ]

        # if it is negative, the indentation will be outwards, so we will
        # make the Y=0 on the most outward point, except for the offs_y
        # that will be negative when Y=0
        if self.CBASERAILIND_SIG < 0:
            addofs = FreeCAD.Vector (0, - self.CBASERAILIND_SIG,0)
            gt2_base_list = [x + addofs for x in gt2_base_list]

        return gt2_base_list
    
# end class Gt2BeltClamp:

# ----------- shp_topbeltclamp
# Creates a shape of a belt clamp. Just the rail and the cylinder
# just one way: 2 clamp blocks
# It is references at the end of the rail

#""                           
#          TOPVIEW                    
#                CLAMPBLOCK          
#                    CB             
#                    ____       ___ 
#           CB_W  {  XXXX      /   \
#           CB_IW {  ____      |   |   CCYL: CLAMPCYL  
#           CB_W  {  XXXX      \___/
#        
#                    CB_L  CS
#

def shp_topbeltclamp (railaxis = 'x', bot_norm = '-z', pos = V0, extra=1):

    cyl_posx = Gt2BeltClamp.CB_L + Gt2BeltClamp.CS + Gt2BeltClamp.CCYL_R
    height =  Gt2BeltClamp.C_H + extra

    shpcyl = fcfun.shp_cyl(r= Gt2BeltClamp.CCYL_R,
                           h= height,
                           normal = VZ,
                           pos = FreeCAD.Vector(cyl_posx,0,-extra) )

    bl_posy0 = Gt2BeltClamp.CB_IW/2.
    bl_posy1 = Gt2BeltClamp.CB_IW/2. + Gt2BeltClamp.CB_W

    # block on top
    blt_p0 = FreeCAD.Vector(0, bl_posy0, -extra)
    blt_p1 = FreeCAD.Vector(Gt2BeltClamp.CB_L , bl_posy0, -extra)
    blt_p2 = FreeCAD.Vector(Gt2BeltClamp.CB_L , bl_posy1, -extra)
    blt_p3 = FreeCAD.Vector(0 , bl_posy1, -extra)
    shp_wire_blt = Part.makePolygon([blt_p0,blt_p1,blt_p2,blt_p3, blt_p0])
    shp_face_blt = Part.Face(shp_wire_blt)
    shpblt = shp_face_blt.extrude(FreeCAD.Vector(0,0,height))
    
    # block on bottom
    blb_p0 = FreeCAD.Vector(0 , -bl_posy1, -extra)
    blb_p1 = FreeCAD.Vector(Gt2BeltClamp.CB_L , -bl_posy1, -extra)
    blb_p2 = FreeCAD.Vector(Gt2BeltClamp.CB_L , -bl_posy0, -extra)
    blb_p3 = FreeCAD.Vector(0, -bl_posy0, -extra)
    shp_wire_blb = Part.makePolygon([blb_p0,blb_p1,blb_p2,blb_p3, blb_p0])
    shp_face_blb = Part.Face(shp_wire_blb)
    shpblb = shp_face_blb.extrude(FreeCAD.Vector(0,0,height))

    shp_clamp = shpcyl.multiFuse([shpblt, shpblb])

    vec_railaxis = fcfun.getvecofname(railaxis)
    vec_botnorm = fcfun.getvecofname(bot_norm)

    vrot = fcfun.calc_rot(vec_railaxis, vec_botnorm)

    shp_clamp.Placement.Rotation = vrot
    shp_clamp.Placement.Base = pos

    return shp_clamp

    #Part.show (shp_clamp)


def fco_topbeltclamp (railaxis = 'x', bot_norm = '-z', pos = V0, extra=1,
                      name = "bclamp"):

    doc = FreeCAD.ActiveDocument
    shptopbeltclamp = shp_topbeltclamp (railaxis = railaxis,
                                        bot_norm = bot_norm,
                                        pos = pos, extra= extra)
    fcotopbeltclamp = doc.addObject("Part::Feature", name)
    fcotopbeltclamp.Shape = shptopbeltclamp


#doc = FreeCAD.newDocument()
#shp = shp_topbeltclamp (railaxis = 'x', bot_norm= '-z', pos=FreeCAD.Vector(2,0,4))



# ----------- shp_topbeltclamp_dir

class BeltClamp (object):

    """ 
    Similar to shp_topbeltclamp, but with any direction, and 
    can have a base
    Creates a shape of a belt clamp. Just the rail and the cylinder
    and may have a rectangular base
    just one way: 2 clamp blocks
    It is referenced on the base of the clamp, but it may have 5 different
    positions

    Parameters
    ----------
    fc_fro_ax : FreeCAD.Vector
        FreeCAD.Vector pointing to the front, see pricture
    fc_top_ax : FreeCAD.Vector
        FreeCAD.Vector pointing to the top, see pricture
    base_h : float
        Height of the base,

                * if 0 and bolt_d=0: no base
                * if 0 and bolt_d!= 0: minimum base to have the bolt head and
                  not touching with the belt (countersunk) if bolt_csunk > 0

    base_l : float
        Length of the base, if base_h not 0.
            
            * if 0 and bolt_d=0: will have the minimum length, defined by the
              clamp
            * if 0 and bolt_d!=0: will have the minimum length, defined by
              the clamp plus the minimum separation due to the bolt holes

    base_w : float
        Width of the base, if base_h not 0.
    bolt_d : float
        Diameter of the bolts, if zero, no bolts
    bolt_csunk : float
        If the bolt is countersunk

            * if >0: there is a whole to countersink the head of the bolt
              there will be an extra height if not enough
              bolt_d has to be > 0
            * if 0: no whole for the height, and no extra height
            * if >0, the size will determine the minimum height of the 
              base, below the countersink hole

    ref : int
        Reference of the position (see picture below)
    extra : float
        If extra, it will have an extra height below the zero height,
        this is to be joined to some other piece
    wfco : int 
        * if 1: With FreeCad Object: a freecad object is created
        * if 0: only the shape
    intol : float
        Internal extra tolerance to the dimension CB_IW, substracting
        to CB_W. If negative, makes CB_IW smaller.
    name : str
        Name of the freecad object, if created


    ::

                                 fc_top_ax
                                    :
                       _____       _:_ ..........
                      |     |     | : |         + C_H
                  ____|_____|_____|_:_|____.....:
                 | ::               :   :: |    + base_h
     fc_fro_ax...|_::_______________*___::_|....:
                            
                  CLAMPBLOCK          
                      CB            * ref
 
                  clamp2end             clamp2end
                 ..+...               ...+...
                 :     :              :     :
                 :   bolt2end         :    bolt2end 
                 :+..+.               :.+..+.
                 :  :  :              :  :  :
                 :__:__:______________:__:__:...................
                 |  :   ____       ___      |                  :
        CB_W  {  |  :  |____|     /   \     |                  :
        CB_IW {  |  O   ____      | * |  O  | CCYL: CLAMPCYL   + base_w
        CB_W  {  |     |____|     \___/     |                  :
                 |__________________________|..................:
                 :     :    :     : :       :
                 :     :CB_L:.CS..:.:       :
                 :                 +        :
                 :                 CCYL_R   :
                 :......... base_l .........:
 
                  __________________________
                 |      ____       ___      |
        CB_W  {  |     |____|     /   \     |
        CB_IW {  4  3  2____      | 1 |  5  6 CCYL: CLAMPCYL  
        CB_W  {  |     |____|     \___/     |
                 |__________________________|
                       :    :
                       :CB_L:.CS.:
 
        References:
        1: cencyl: center of cylinder
        2: frontclamp: front of the clamps
        3: frontbolt
        4: frontbase
        5: backbolt
        6: backbase


                                 fc_top_ax
                                    :
                       _____       _:_
                      |     |     | : |
                  ____|_____|_____|_:_|____
                 |:..:              :  :..:|..... 
     fc_fro_ax...|_::_______________*___::_|....+ bolt_csunk (if not 0)

    """
    # minimum base 
    MIN_BASE_H = 2.

    def __init__(self,
                 fc_fro_ax,
                 fc_top_ax,
                 base_h = 2,
                 base_l = 0,
                 base_w = 0,
                 bolt_d = 3,
                 bolt_csunk = 0,
                 ref = 1,
                 pos = V0,
                 extra=1,
                 wfco = 1,
                 intol = 0,
                 name = 'belt_clamp' ):

        doc = FreeCAD.ActiveDocument
        self.name = name

        # if more tolerance is needed in the center
        cb_in_w = CB_IW + intol
        self.cb_in_w = cb_in_w
        cb_wall_w = CB_W - intol/2
        self.cb_wall_w = cb_wall_w

        # normalize and get the other base vector
        nfro_ax = DraftVecUtils.scaleTo(fc_fro_ax,1)
        nfro_ax_n = nfro_ax.negative()
        ntop_ax = DraftVecUtils.scaleTo(fc_top_ax,1)
        ntop_ax_n = ntop_ax.negative()
        nsid_ax = nfro_ax.cross(ntop_ax)

        clamponly_l = CB_L + CS + 2 * CCYL_R
        clamponly_w = max((cb_in_w+2*cb_wall_w), (2*CCYL_R))

        bolt2end = 0 # they will change in case they are used
        clamp2end = 0
        if base_h == 0 and bolt_d == 0:
            # No base
            base = 0
            base_l = 0
        else:
            base = 1
            if bolt_d > 0 :
                d_bolt = kcomp.D912[bolt_d]
                bolt_shank_r = d_bolt['shank_r_tol']
                bolt_head_r = d_bolt['head_r_tol']
                bolt_head_l = d_bolt['head_l']
                # there are bolt holes, calculate the extra length needed
                # from the end to the clamp / cylinder
                bolt2end = fcfun.get_bolt_end_sep(bolt_d,hasnut=0)
                # bolt space on one side
                clamp2end = 2 * bolt2end
                base_min_len = clamponly_l + 2 * clamp2end
                if base_l < base_min_len:
                    logger.debug("base_l too short, taking min len %s",
                                  base_min_len)
                    base_l = base_min_len
                else:
                    clamp2end = (base_l - clamponly_l) /2.
                    bolt2end = clamp2end / 2.
                if bolt_csunk > 0:
                    # there are countersunk holes for the bolts
                    if base_h == 0:
                        # minimum height:
                        base_h = bolt_csunk + bolt_head_l
                    else:
                        # check if there is enough base height
                        if base_h < bolt_csunk + bolt_head_l:
                            base_h = bolt_csunk + bolt_head_l
                            logger.debug("base_h too short,taking height %s",
                                  base_h)
                else:
                    if base_h < self.MIN_BASE_H:
                        base_h = self.MIN_BASE_H
                        logger.debug("taking base height %s",
                                  base_h)
            else: # No bolt
                bolt2end = 0
                if base_l < clamponly_l:
                    if base_l > 0:
                        logger.debug("base_l too short, Taking min len %s",
                                      clamponly_l) 
                    base_l = clamponly_l
                    clamp2end = 0
                else: #base larger than clamp
                    clamp2end = (base_l - clamponly_l) /2.
            if base_w == 0:
                base_w = clamponly_w
            elif base_w < clamponly_w:
                logger.debug("base_w too short, Taking min width %s",
                              clamponly_w)
                base_w = clamponly_w

        ###
        cencyl2froclamp = CB_L+CS+CCYL_R
        #vectors to references:
        # from the center of the cylinder to the front clamp
        vec_1to2 = DraftVecUtils.scale(nfro_ax,cencyl2froclamp)
        vec_2to1 = vec_1to2.negative()
        # from the front clamp to the front bolt
        vec_2to3 = DraftVecUtils.scale(nfro_ax, bolt2end)
        vec_3to2 = vec_2to3.negative()
        # Since not always there is a bolt, from the clamp
        vec_2to4 = DraftVecUtils.scale(nfro_ax, clamp2end)
        vec_4to2 = vec_2to4.negative()
        # from the center of the cylinder to the back bolt
        vec_5to1 = DraftVecUtils.scale(nfro_ax,CCYL_R) + vec_2to3
        vec_1to5 = vec_5to1.negative()
        # from the back bolt to the back end
        vec_6to1 = DraftVecUtils.scale(nfro_ax,CCYL_R) + vec_2to4
        vec_1to6 = vec_6to1.negative()

        # default values
        vec_tocencyl = V0
        vec_tofrontclamp = V0
        vec_tofrontbolt = V0
        vec_tofrontbase = V0
        vec_tobackbolt = V0
        vec_tobackbase = V0
        if ref==1: #ref on the center of the cylinder
            vec_tocencyl = V0
            vec_tofrontclamp = vec_1to2 
            vec_tofrontbolt = vec_1to2 + vec_2to3
            vec_tofrontbase = vec_1to2 + vec_2to4
            vec_tobackbolt = vec_1to5
            vec_tobackbase = vec_1to6
        elif ref==2: #ref on the front of the clamps
            vec_tocencyl = vec_2to1
            vec_tofrontclamp = V0
            vec_tofrontbolt = vec_2to3
            vec_tofrontbase = vec_2to4
            vec_tobackbolt = vec_2to1 + vec_1to5
            vec_tobackbase = vec_2to1 + vec_1to6
        elif ref == 3:
            if clamp2end == 0 or bolt2end == 0:
                logger.error('reference on the bolts, there are no bolts')
            else:
                vec_tocencyl = vec_3to2 + vec_2to1
                vec_tofrontclamp = vec_3to2
                vec_tofrontbolt = V0
                vec_tofrontbase = vec_2to3 #same as 3 to 4
                vec_tobackbolt = vec_3to2 + vec_2to1 + vec_1to5
                vec_tobackbase = vec_3to2 + vec_2to1 + vec_1to6
        elif ref == 4:
            if clamp2end == 0:
                logger.debug('reference at the end, same as the clamps')
            vec_tocencyl = vec_4to2 + vec_2to1
            vec_tofrontclamp = vec_4to2
            vec_tofrontbolt = vec_3to2 # same as 4 to 3
            vec_tofrontbase = V0
            vec_tobackbolt = vec_4to2 + vec_2to1 + vec_1to5
            vec_tobackbase = vec_4to2 + vec_2to1 + vec_1to6
        elif ref == 5:
            if clamp2end == 0 or bolt2end == 0:
                logger.error('reference on the bolts, there are no bolts')
            else:
                vec_tocencyl = vec_5to1
                vec_tofrontclamp = vec_5to1 + vec_1to2
                vec_tofrontbolt = vec_5to1 + vec_1to2 + vec_2to3
                vec_tofrontbase = vec_5to1 + vec_1to2 + vec_2to4
                vec_tobackbolt = V0
                vec_tobackbase = vec_3to2 #5to6: same as 3to2
        elif ref == 6:
            if clamp2end == 0:
                logger.debug('reference at the end, same as the clamps')
            vec_tocencyl = vec_6to1
            vec_tofrontclamp = vec_6to1 + vec_1to2
            vec_tofrontbolt = vec_6to1 + vec_1to2 + vec_2to3
            vec_tofrontbase = vec_6to1 + vec_1to2 + vec_2to4
            vec_tobackbolt = vec_2to3 # same as 6 to 5
            vec_tobackbase = V0
        else:
            logger.error('reference out of range')
          


        if extra == 0:
            extra_pos = V0
        else:
            extra_pos = DraftVecUtils.scale(ntop_ax, -extra)
        pos_extra = pos + extra_pos
        base_top_add = DraftVecUtils.scale(ntop_ax, base_h + extra)
        
        
        # total height of the clamp, including the base
        clamp_tot_h = C_H + base_h + extra
        # position of the clamp cylinder:
        clampcyl_pos = pos_extra + vec_tocencyl
        shp_cyl = fcfun.shp_cyl(CCYL_R, clamp_tot_h, ntop_ax, clampcyl_pos)
        # position of the clamp blocks, without going to the side axis
        clampblock_pos = pos_extra + vec_tofrontclamp
        clampblock_side_add = DraftVecUtils.scale(nsid_ax, 
                                                  (cb_in_w + cb_wall_w)/2.)
        clampblock_1_pos = clampblock_pos + clampblock_side_add
        clampblock_2_pos = clampblock_pos - clampblock_side_add
        shp_clampblock_1 = fcfun.shp_box_dir(box_w = cb_wall_w,
                                             box_d = CB_L,
                                             box_h = clamp_tot_h,
                                             fc_axis_h = ntop_ax,
                                             fc_axis_d = nfro_ax_n,
                                             cw=1, cd=0, ch=0,
                                             pos = clampblock_1_pos)
        shp_clampblock_2 = fcfun.shp_box_dir(box_w = cb_wall_w,
                                             box_d = CB_L,
                                             box_h = clamp_tot_h,
                                             fc_axis_h = ntop_ax,
                                             fc_axis_d = nfro_ax_n,
                                             cw=1, cd=0, ch=0,
                                             pos = clampblock_2_pos)

        shp_clamp = shp_cyl.multiFuse([shp_clampblock_1, shp_clampblock_2])


        #position of the base, we will take it on the point 4 and make it not 
        # centered
        if base == 1:
            base_pos = pos_extra + vec_tofrontbase 
            shp_base = fcfun.shp_box_dir(box_w = base_w,
                                         box_d = base_l,
                                         box_h = base_h + extra,
                                         fc_axis_h = ntop_ax,
                                         fc_axis_d = nfro_ax_n,
                                         cw=1, cd=0, ch=0,
                                         pos = base_pos)
            if base_l > clamponly_l: # chamfer
                shp_base = fcfun.shp_filletchamfer_dir (shp_base,
                                              fc_axis=ntop_ax,
                                              fillet=1, radius= 2)

            # shape of the bolt holes, if there are
            if bolt_d > 0:
                pos_bolt_front = pos_extra + vec_tofrontbolt + base_top_add
                pos_bolt_back = pos_extra + vec_tobackbolt + base_top_add
                if bolt_csunk > 0 :
                    shp_bolt_front = fcfun.shp_bolt_dir(
                                              r_shank = bolt_shank_r,
                                              l_bolt = base_h + extra,
                                              r_head = bolt_head_r,
                                              l_head = bolt_head_l,
                                              support=0,
                                              fc_normal = ntop_ax_n,
                                              pos=pos_bolt_front)
                    shp_bolt_back = fcfun.shp_bolt_dir(
                                              r_shank = bolt_shank_r,
                                              l_bolt = base_h + extra,
                                              r_head = bolt_head_r,
                                              l_head = bolt_head_l,
                                              support=0,
                                              fc_normal = ntop_ax_n,
                                              pos=pos_bolt_back)
                else: # no head, just a cylinder:
                    shp_bolt_front = fcfun.shp_cylcenxtr (
                                              r = bolt_shank_r,
                                              h = base_h + extra,
                                              normal = ntop_ax_n,
                                              ch = 0,
                                              xtr_top=1, xtr_bot=1,
                                              pos = pos_bolt_front)
                    shp_bolt_back = fcfun.shp_cylcenxtr (
                                              r = bolt_shank_r,
                                              h = base_h + extra,
                                              normal = ntop_ax_n,
                                              ch = 0,
                                              xtr_top=1, xtr_bot=1,
                                              pos = pos_bolt_back)


                # fuse the bolts:
                shp_bolts = shp_bolt_front.fuse(shp_bolt_back)
                shp_base = shp_base.cut(shp_bolts)
            shp_clamp = shp_base.fuse(shp_clamp)

              
 

        doc.recompute()
        shp_clamp = shp_clamp.removeSplitter()
        self.shp = shp_clamp

        self.wfco = wfco
        if wfco == 1:
            # a freeCAD object is created
            fco_clamp = doc.addObject("Part::Feature", name )
            fco_clamp.Shape = shp_clamp
            self.fco = fco_clamp

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Clamp object with no fco")
        
    # exports the shape into stl format
    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        #stlPath = filepath + "/freecad/stl/"
        stlPath = filepath + stl_dir
        stlFileName = stlPath + name + ".stl"
        # exportStl is not working well with FreeCAD 0.17
        #self.shp.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.shp,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp


# Revisar el caso con agujeros de bolt
#BeltClamp (VX, VY, base_h = 0, bolt_d=3, bolt_csunk = 2)



class ShpBeltClamped (shp_clss.WireBeltClamped):
    """ Creates a belt from a wire of the trajectory of the belt and its
    section. The shape is not toothed, it is just a rough shape

    ::

      axis_w
        :
        :
     pulley1                   pulley2
          
        -----------------------------------
      (   )                             (   )--------> axis_d
        ---------===  ( )  ( )  ===--------
               clamp1          clamp2

      1 0        2 3   45  67   8 9      10 11   pos_d
        :          :            :         :
        :          :            :         :
        :          :............:         :
        :                +                :
        :             clamp_sep           :
        :                                 :
        :.................................:
                       +
                     pull_sep_d

      pos_w points:

      axis_w
        :                                    pull2
        :      clamp1                 clamp2
       2_                                     3-
                                             ( 1 )   - - pull_sep_w (positive)
     (  0  )   - - - - - - - - - - - - - - -  5-     - -
              6 ___ ...................___.............:+ clamp_pull1_w (neg)
       4-     7       < )        ( >                   :+ clamp_w
              8 ___ ...................___.............:



      axis_w
        :                                      pull2
        :      clamp1                 clamp2
        _                                         -
                                                (   )   - - pull_sep_w(positive)
     (     )   - - - - - - - - - - - - - - - - -  -     - -
                ___ ...................___.............:+ clamp_pull1_w (neg)
        -       x     < )        ( >                   :+ clamp_w
                ___ ...................___.............:
        :      :   :   ::         :   :   :       :
        :      :   :   :cyl_r     :   :   :       :
        :      :   :...:          :...:   :.......:
        :      :   :  +            +  :   :   +
        :      :   :  clamp_cyl_sep   :   :   +
        :      :   :                  :   :  clamp_pull2_d
        :      :   :                  :...:
        :      :   :                  :  +
        :      :   :..................: clamp_d
        :      :   :        +
        :      :   :       clamp_sep
        :      :...:   
        :      : +
        :      : clamp_d
        :      :
        :......:
           +
         clamp_pull1_d
         

     Section of the belt. The belt starts at point x (see upper drawing)

                    axis_h
                       :
                       :
         _____         :    _____
              |    1 __:__ |....................
         clamp|     |  :  ||clamp               :
              |     |  :  ||                    :
              |     |  :  ||                    :+belt_width (can be confusing)
              |     |  :  ||                    :   is the width of the belt
              |    0|  :..||........ axis_w     :   but in the drawing is the
              |     |     ||                    :   height
              |     |     ||         axis_d is pointing out of the screen
              |     |     ||                (to you)
              |     |belt ||                    :
              |     |_____||....................:
              |        0 12|   for now, the belt will be at this pos_w 2
                               because, there is already a pos_w for the wire
                    :     :
                    :.....:
                       +
                      belt_thick
                   
    Parameters:
    -----------
    pull1_dm: float
        Diameter of pulley 1
    pull2_dm: float
        Diameter of pulley 2
    pull_sep_d : float
        Separation between the 2 pulleys centers along axis_d
    pull_sep_w : float
        Separation between the 2 pulleys centers along axis_w

        * if positive, pulley 2 is further away in the direction of axis_w
        * if negative, pulley 2 is further away opposite to the direction of
          axis_w

    clamp_pull1_d : float
        Separation between the clamp (side closer to the center) and the center
        of the pulley1 along axis d
    clamp_pull1_w : float
        Separation between the center of the clamp and the center of the
        pulley1 along axis w
    clamp_pull2_d : float
        Separation between the clamp (side closer to the center) and the center
        of the pulley1 along axis d
        clamp_pull2_w can be calculated because the clamps are aligned along
        axis_d, so it will be clamp_pull1_d + pull_sep_w
    clamp_d : float
        Length of the clamp (same for each clamp)
    clamp_w : float
        Width of inner space (same for each clamp)
    clamp_cyl_sep : float
        Separation between clamp and the center of the cylinder (or the center)
        of the larger cylinder (when is a belt shape)
    cyl_r : float
        Radius of the cylinder for the belt, if it is not a cylinder but a
        shape of 2 cylinders: < ) , then the raidius of the larger one
    belt_width : float
        Width of the belt, can be consfusing because the width is along axis_h
    belt_thick : float
        Thickness of the belt, it doesn't take into account the teeth, or the
        detailed shape (contour)
    axis_d :  FreeCAD.Vector
        Coordinate System Vector along the depth
    axis_w :  FreeCAD.Vector
        Coordinate System Vector along the width
    axis_h :  FreeCAD.Vector
        Coordinate System Vector along the height
    pos_d : int
        Location of pos along the axis_d, see drawing

        * 0: center of the pulley 1
        * 1: end of pulley 1
        * 2: end of clamp 1, closest end to pulley 1
        * 3: other end of clamp 1, closest to cylinder
        * 4: center of cylinder (or shape < ) 1
        * 5: external radius of cylinder 1
        * 6: external radius of cylinder 2
        * 7: center of cylinder (or shape ( > 2
        * 8: end of clamp 2, closest to cylinder
        * 9: other end of clamp 2, closest end to pulley 2
        * 10: center of pulley 2
        * 11: end of pulley 2

    pos_w : int
        Location of pos along the axis_w, see drawing

        * 0: center of pulley 1
        * 1: center of pulley 2
        * 2: end (radius) of pulley 1 along axis_w
        * 3: end (radius) of pulley 2 along axis_w
        * 4: other end (radius) of pulley 1 opposite to axis_w
        * 5: other end (radius) of pulley 2 opposite to axis_w
        * 6: clamp space, closest to the pulley
        * 7: center of clamp space
        * 8: clamp space, far away from the pulley

    pos_h : int
        Location of pos along the axis_h, see drawing

        * 0: center of symmetry
        * 1: top of the belt
          since it is symmetric -1 will be at the bottom of the belt

    pos: FreeCAD vector of the position of the reference

    Attributes:
    -----------
    clamp_sep : float
        Separation between clamps, the closest ends

    """

    
    def __init__(self,
                 pull1_dm,
                 pull2_dm,
                 pull_sep_d,
                 pull_sep_w,
                 clamp_pull1_d,
                 clamp_pull1_w,
                 clamp_pull2_d,
                 clamp_d,
                 clamp_w,
                 clamp_cyl_sep,
                 cyl_r,
                 belt_width = 6.,
                 belt_thick = 1.38,
                 axis_d = VY,
                 axis_w = VX,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos=V0):

        shp_clss.WireBeltClamped.__init__( self,
                             pull1_dm      = pull1_dm,
                             pull2_dm      = pull2_dm,
                             pull_sep_d    = pull_sep_d,
                             pull_sep_w    = pull_sep_w,
                             clamp_pull1_d = clamp_pull1_d,
                             clamp_pull1_w = clamp_pull1_w,
                             clamp_pull2_d = clamp_pull2_d,
                             clamp_d       = clamp_d,
                             clamp_w       = clamp_w,
                             clamp_cyl_sep = clamp_cyl_sep,
                             cyl_r         = cyl_r,
                             axis_d        = axis_d,
                             axis_w        = axis_w,
                             pos_d         = pos_d,
                             pos_w         = pos_w,
                             pos           = pos)

        self.belt_thick = belt_thick
        self.belt_width = belt_width

        # vectors from the origin to the points along axis_h:
        self.h0_cen = 1 # symmetric
        self.axis_h = DraftVecUtils.scaleTo(axis_h,1)
        self.h_o[0] = V0 # origin (center symmetric)
        self.h_o[1] = self.vec_h(-self.belt_width/2.)
        print(str(self.h_o[1]))

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # Four corners of the belt section
        #
        #    axis_h
        #      :
        #      :   ___
        #    4_:_1|
        #    |   ||
        #    |   |.....> axis_w
        #    |   ||
        #    3___2| clamp
        #         |
        #

        belt_sec_pt1 = self.get_pos_dwh(2,6,1)
        belt_sec_pt2 = self.get_pos_dwh(2,6,-1)
        belt_sec_pt3 = belt_sec_pt2 + self.vec_w(-belt_thick)
        belt_sec_pt4 = belt_sec_pt1 + self.vec_w(-belt_thick)

        wire_belt_sec = Part.makePolygon([belt_sec_pt1, belt_sec_pt2,
                                          belt_sec_pt3, belt_sec_pt4,
                                          belt_sec_pt1])
        shp_belt = self.belt_wire.makePipeShell([wire_belt_sec],True, False,2)
        shp_belt = shp_belt.removeSplitter()

        self.shp = shp_belt
        


    # not using this yet
    #def get_o_to_wb (self, pos_wb):
    #    """ returns the vector from origin of the belt section to pos_wb
    #    wb is related to the belt
    #    If it is symmetrical, pos_wb == 0 will be at the middle
    #    Then, pos_wb > 0 will be the points on the positive side of axis_w
    #    Then, pos_wb < 0 will be the points on the negative side of axis_w
    #    """
    #    abs_pos_wb = abs(pos_wb)
    #    if self.wb0_cen == 1:
    #        if pos_wb <= 0:
    #            try:
    #                vec = self.wb_o[abs_pos_wb]
    #            except KeyError:
    #                logger.error('pos_wb key not defined ' + str(pos_wb))
    #            else:
    #                return vec
    #        else:
    #            try:
    #                vec_0_to_wb = (self.wb_o[0]).sub(self.wb_o[pos_wb]) #D= B-C
    #            except KeyError:
    #                logger.error('pos_wb key not defined ' + str(pos_wb))
    #            else:
    #                vec_orig_to_wb = self.wb_o[0] + vec_0_to_wb # A = B + D
    #                return vec_orig_to_wb
    #    else: #pos_d == 0 is at the end, distances are calculated directly
    #        try:
    #            vec = self.wb_o[pos_wb]
    #        except KeyError:
    #            logger.error('pos_wb key not defined' + str(pos_wb))
    #        else:
    #            return vec

       

#belt = ShpBeltClamped (
#                 pull1_dm = 5,
#                 pull2_dm = 6,
#                 pull_sep_d = 80,
#                 pull_sep_w = 0,
#                 clamp_pull1_d = 15,
#                 clamp_pull1_w = 5,
#                 clamp_pull2_d = 15,
#                 clamp_d = 5,
#                 clamp_w = 4,
#                 clamp_cyl_sep = 8,
#                 cyl_r = 3,
#                 belt_width = 6.,
#                 belt_thick = 1.38,
#                 axis_d = VY,
#                 axis_w = VX,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos=V0)

class PartBeltClamped (fc_clss.SinglePart, ShpBeltClamped):
    """ Integration of a ShpBeltClamped object into a PartBeltClamped object

    Same parameters as ShpBeltClamped plus

    model_type
    name
    """

    def __init__(self,
                 pull1_dm,
                 pull2_dm,
                 pull_sep_d,
                 pull_sep_w,
                 clamp_pull1_d,
                 clamp_pull1_w,
                 clamp_pull2_d,
                 clamp_d,
                 clamp_w,
                 clamp_cyl_sep,
                 cyl_r,
                 belt_width = 6.,
                 belt_thick = 1.38,
                 axis_d = VY,
                 axis_w = VX,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos=V0,
                 model_type = 1, # dimensional model
                 name = ''):

        default_name = 'gt2_belt'
        self.set_name (name, default_name, change=0)

        ShpBeltClamped.__init__(self,
                 pull1_dm = pull1_dm,
                 pull2_dm = pull2_dm,
                 pull_sep_d = pull_sep_d,
                 pull_sep_w = pull_sep_w,
                 clamp_pull1_d = clamp_pull1_d,
                 clamp_pull1_w = clamp_pull1_w,
                 clamp_pull2_d = clamp_pull2_d,
                 clamp_d  = clamp_d,
                 clamp_w  = clamp_w,
                 clamp_cyl_sep = clamp_cyl_sep,
                 cyl_r = cyl_r,
                 belt_width = belt_width,
                 belt_thick = belt_thick,
                 axis_d = axis_d,
                 axis_w = axis_w,
                 axis_h = axis_h,
                 pos_d = pos_d,
                 pos_w = pos_w,
                 pos_h = pos_h,
                 pos = pos)

        # creation of the part
        fc_clss.SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])
                 

#belt = PartBeltClamped (
#                 pull1_dm = 5,
#                 pull2_dm = 6,
#                 pull_sep_d = 80,
#                 pull_sep_w = 0,
#                 clamp_pull1_d = 15,
#                 clamp_pull1_w = 5,
#                 clamp_pull2_d = 15,
#                 clamp_d = 5,
#                 clamp_w = 4,
#                 clamp_cyl_sep = 8,
#                 cyl_r = 3,
#                 belt_width = 6.,
#                 belt_thick = 1.38,
#                 axis_d = VY,
#                 axis_w = VX,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 1,
#                 pos=V0)

class DoubleBeltClamp (shp_clss.Obj3D):
    """
    Similar to BeltClamp, but in two ways
    Creates a shape of a double belt clamp.
    positions

    Parameters
    ----------
    fc_fro_ax : FreeCAD.Vector
        FreeCAD.Vector pointing to the front, see pricture
    fc_top_ax : FreeCAD.Vector
        FreeCAD.Vector pointing to the top, see pricture
    base_h : float
        Height of the base,

                * if 0 and bolt_d=0: no base
                * if 0 and bolt_d!= 0: minimum base to have the bolt head and
                  not touching with the belt (countersunk) if bolt_csunk > 0

    base_l : float
        Length of the base, if base_h not 0.
            
            * if 0 and bolt_d=0: will have the minimum length, defined by the
              clamp
            * if 0 and bolt_d!=0: will have the minimum length, defined by
              the clamp plus the minimum separation due to the bolt holes

    base_w : float
        Width of the base, if base_h not 0.
    bolt_d : float
        Diameter of the bolts, if zero, no bolts
    bolt_csunk : float
        If the bolt is countersunk

            * if >0: there is a whole to countersink the head of the bolt
              there will be an extra height if not enough
              bolt_d has to be > 0
            * if 0: no whole for the height, and no extra height
            * if >0, the size will determine the minimum height of the 
              base, below the countersink hole

    ref : int
        Reference of the position (see picture below)
    extra : float
        If extra, it will have an extra height below the zero height,
        this is to be joined to some other piece
    wfco : int 
        * if 1: With FreeCad Object: a freecad object is created
        * if 0: only the shape
    intol : float
        Internal extra tolerance to the dimension CB_IW, substracting
        to CB_W. If negative, makes CB_IW smaller.
    name : str
        Name of the freecad object, if created


    ::

                                    axis_h
                                   :
                      _____       _:_           _:_       _____ ..........
                     |     |     | : |         | : |     |     |         + C_H
                 ____|_____|_____|_:_|_________|_:_|_____|_____|____.....:
                | ::               :  |       |  :               :: | + base_h
       axis_d...|_::_______________*__|_______|__*_______________::_|.:


                  clamp2end                                     clamp2end
                ...+...                                       ...+...
                :     :                                       :     :
                :   bolt2end           _______                :   bolt2end
                :+..+.:               |       |               :+..+.: 
                :  :  :               |   O   |               :  :  :
                :__:__:_______________|_______|_______________:__:__:...................
                |  :   ____       ___           ___       ____      |                  :
       CB_W  {  |  :  |____|     /   \         /   \     |____|     |                  :
       CB_IW {  |  O   ____      | * |         | * |      ____   O  | CCYL: CLAMPCYL   + base_w
       CB_W  {  |     |____|     \___/         \___/     |____|     |                  :
                |___________________________________________________|..................:
                :     :    :     : :  |       |                     :
                :     :    :     : :  |   O   |                     :
                :     :CB_L:.CS..:.:  |_______|                     :
                :                 +                                 :
                :                 CCYL_R                            :
                :...................... base_l .....................:

                                       _______                
                                      |       |               
                                      |   O   |               
                 _____________________|_______|______________________
                |      ____       ___           ___       ____      |
       CB_W  {  |     |____|     /   \         /   \     |____|     |
       CB_IW { -4 -3 -2____      |-1 |    0    | 1 |      ____2  3  4
       CB_W  {  |     |____|     \___/         \___/     |____|     |
                |___________________________________________________|
                                      |       |                     
                                      |   O   |                     
                                      |_______|
                1: center 
                2: center of left cylinder
                3: center of right cylinder
                4: front of the left clamps
                5: front of the right clamps
                6: left bolt
                7: right bolt
                8: left base
                9: right base

                                       ___3___                
                                      |       |               
                                      |   2   |               
                 _____________________|_______|______________________
                |      ____       ___           ___       ____      |
       CB_W  {  |     |____| . . /   \ .  1 .  /   \ . . |____|     |
       CB_IW {  |      ____      |   |    0    |   |      ____      |
       CB_W  {  |     |____| . . \___/ . -1 .  \___/ . . |____|     |
                |___________________________________________________|
                                      |       |                     
                                      |  -2   |                     
                                      |__-3___|
                1: center
                2: bolt up
                3: bolt down
                4: up base
                5: down base

    """
    def __init__(self, 
                axis_h = VZ,
                axis_d = VX,
                axis_w = VY,
                base_h = 2,
                base_l = 0,
                base_w = 0,
                bolt_d = 3,
                bolt_csunk = 0,
                ref = 1,
                pos = V0,
                extra=1,
                wfco = 1,
                intol = 0,
                name = 'double_belt_clamp' ):
        doc = FreeCAD.ActiveDocument
        self.name = name
        
        self.axis_d = axis_d
        self.axis_h = axis_h
        self.axis_w = axis_w
        if axis_w is None or axis_w == V0:
            axis_w = axis_h.cross(axis_d)

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)
        
        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i]) 

        d_bolt = kcomp.D912[bolt_d]
        bolt_shank_r = d_bolt['shank_r_tol']
        bolt_head_r = d_bolt['head_r_tol']
        bolt_head_l = d_bolt['head_l']

        # if more tolerance is needed in the center
        cb_in_w = CB_IW + intol
        self.cb_in_w = cb_in_w
        cb_wall_w = CB_W - intol/2
        self.cb_wall_w = cb_wall_w

        clamponly_l = 2 * (CB_L + CS + 2 * CCYL_R)
        clamponly_w = max((cb_in_w+2*cb_wall_w), (2*CCYL_R))
        # there are bolt holes, calculate the extra length needed
        # from the end to the clamp / cylinder
        bolt2end = fcfun.get_bolt_end_sep(bolt_d,hasnut=0)
        # bolt space on one side
        clamp2end = 2 * bolt2end
        base_min_len = clamponly_l + 3 * clamp2end
        if base_l < base_min_len:
            logger.debug("base_l too short, taking min len %s",
                            base_min_len)
            base_l = base_min_len
        else:
            clamp2end = (base_l - clamponly_l) /2.
            bolt2end = clamp2end / 2.

        if base_w == 0:
                base_w = clamponly_w
                logger.debug("base_w too short, Taking min width %s",
                              clamponly_w)
        elif base_w < clamponly_w:
                logger.debug("base_w too short, Taking min width %s",
                              clamponly_w)
                base_w = clamponly_w

        self.base_h = base_h
        self.base_w = base_w
        self.base_l = base_l
        self.pos_o = pos
        self.pos_d = 0
        self.pos_w = 0
        self.pos_h = 0
        chmf_r = 1.

        if extra == 0:
            extra_pos = V0
        else:
            extra_pos = DraftVecUtils.scale(self.axis_h, -extra)

        pos_extra = pos + extra_pos
        base_top_add = DraftVecUtils.scale(self.axis_h, base_h + extra)

        # position centered
        self.d0_cen = 1
        self.w0_cen = 1
        self.h0_cen = 0
        # position along axis_d
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(clamp2end/2 + CCYL_R)
        self.d_o[2] = self.vec_d(clamp2end/2 + CCYL_R + CS + CB_L)
        self.d_o[3] = self.vec_d(self.base_l/2 - bolt_head_r)
        self.d_o[4] = self.vec_d(clamp2end/2 + CCYL_R + CS + CB_L + clamp2end)
        # position along axis_w
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w((cb_in_w + cb_wall_w)/2.)
        self.w_o[2] = self.vec_w((self.base_w + clamp2end)/2)
        self.w_o[3] = self.vec_w(self.base_w/2 + 2*bolt2end)

        # position along axis_h
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(self.base_h)

        # Make the base
            # principal
        shp_base_1 = fcfun.shp_box_dir(box_w = self.base_w,
                                     box_d = self.base_l,
                                     box_h = self.base_h,
                                     fc_axis_w = self.axis_w,
                                     fc_axis_h = self.axis_h,
                                     fc_axis_d = self.axis_d,
                                     cw=1, cd=1, ch=0, # 1 centrado, 0 descentrado
                                     pos = self.pos_o)
        shp_base_1 = fcfun.shp_filletchamfer_dir (shp_base_1, self.axis_h,
                                                fillet = 1, radius = chmf_r)

            # perp
        shp_base_2 = fcfun.shp_box_dir(box_w = self.base_w + clamp2end + 2*bolt_head_r,
                                     box_d = 2 * bolt_head_r,
                                     box_h = self.base_h,
                                     fc_axis_w = self.axis_w,
                                     fc_axis_h = self.axis_h,
                                     fc_axis_d = self.axis_d,
                                     cw=1, cd=1, ch=0, # 1 centrado, 0 descentrado
                                     pos = self.pos_o)
        shp_base_2 = fcfun.shp_filletchamfer_dir (shp_base_2, self.axis_h,
                                                fillet = 1, radius = chmf_r)
        
        shp_base = fcfun.fuseshplist([shp_base_1, shp_base_2])

        # make the clampblock
        clamp_tot_h = C_H + base_h + extra
        clampcyl_pos_1 = self.d_o [1] + pos_extra
        #clampcyl_pos_2 = self.d_o[-1] - pos_extra
        clampblock_side_add = DraftVecUtils.scale(self.axis_w, 
                                                  (cb_in_w + cb_wall_w)/2.)
        clampblock_1_pos = self.d_o[2]
        #clampblock_2_pos = self.d_o[-2]

        shp_cyl_1 = fcfun.shp_cyl(CCYL_R, clamp_tot_h, self.axis_h, self.get_pos_dwh(1,0,1))#self.pos + clampcyl_pos_1 + FreeCAD.Vector(0,0,self.base_h/2))
        shp_clampblock_1_a = fcfun.shp_box_dir(box_w = cb_wall_w,
                                             box_d = CB_L,
                                             box_h = clamp_tot_h,
                                             fc_axis_h = self.axis_h,
                                             fc_axis_d = self.axis_d,
                                             cw=1, cd=1, ch=0,
                                             pos = self.get_pos_dwh(2,1,0))#self.pos + clampblock_1_pos + clampblock_side_add)
        shp_clampblock_1_b = fcfun.shp_box_dir(box_w = cb_wall_w,
                                             box_d = CB_L,
                                             box_h = clamp_tot_h,
                                             fc_axis_h = self.axis_h,
                                             fc_axis_d = self.axis_d,
                                             cw=1, cd=1, ch=0,
                                             pos = self.get_pos_dwh(2,-1,0))#self.pos + clampblock_1_pos - clampblock_side_add)
        
        shp_cyl_2 = fcfun.shp_cyl(CCYL_R, clamp_tot_h, self.axis_h, self.get_pos_dwh(-1,0,1))#self.pos + clampcyl_pos_2 - FreeCAD.Vector(0,0,self.base_h/2))
        shp_clampblock_2_a = fcfun.shp_box_dir(box_w = cb_wall_w,
                                             box_d = CB_L,
                                             box_h = clamp_tot_h,
                                             fc_axis_h = self.axis_h,
                                             fc_axis_d = self.axis_d,
                                             cw=1, cd=1, ch=0,
                                             pos = self.get_pos_dwh(-2,1,0))#self.pos + clampblock_2_pos + clampblock_side_add)
        shp_clampblock_2_b = fcfun.shp_box_dir(box_w = cb_wall_w,
                                             box_d = CB_L,
                                             box_h = clamp_tot_h,
                                             fc_axis_h = self.axis_h,
                                             fc_axis_d = self.axis_d,
                                             cw=1, cd=1, ch=0,
                                             pos = self.get_pos_dwh(-2,-1,0))#self.pos + clampblock_2_pos - clampblock_side_add)
        
        shp_clamp = fcfun.fuseshplist([shp_cyl_1, shp_clampblock_1_a, shp_clampblock_1_b,
                                       shp_cyl_2, shp_clampblock_2_a, shp_clampblock_2_b])
        
        # Make holes
        if bolt_d > 0:
            
            # pos_bolt_1 = self.pos + self.d_o[6] 
            # pos_bolt_2 = self.pos + self.d_o[5]
            # pos_bolt_3 = self.pos + self.w_o[1] + pos_extra + base_top_add + FreeCAD.Vector(0,0,-self.base_h)
            # pos_bolt_4 = self.pos + self.w_o[2] - pos_extra - base_top_add 
            if bolt_csunk > 0 :
                shp_bolt_1 = fcfun.shp_bolt_dir(
                                            r_shank = bolt_shank_r,
                                            l_bolt = base_h + extra,
                                            r_head = bolt_head_r,
                                            l_head = bolt_head_l,
                                            support=0,
                                            fc_normal = self.axis_h,
                                            pos= self.get_pos_dwh(3,0,0))#pos_bolt_1)
                shp_bolt_2 = fcfun.shp_bolt_dir(
                                            r_shank = bolt_shank_r,
                                            l_bolt = base_h + extra,
                                            r_head = bolt_head_r,
                                            l_head = bolt_head_l,
                                            support=0,
                                            fc_normal = self.axis_h,
                                            pos= self.get_pos_dwh(-3,0,0))#pos_bolt_2)
                shp_bolt_3 = fcfun.shp_bolt_dir(
                                            r_shank = bolt_shank_r,
                                            l_bolt = base_h + extra,
                                            r_head = bolt_head_r,
                                            l_head = bolt_head_l,
                                            support=0,
                                            fc_normal = self.axis_h,
                                            pos= self.get_pos_dwh(0,2,0))#pos_bolt_3)
                shp_bolt_4 = fcfun.shp_bolt_dir(
                                            r_shank = bolt_shank_r,
                                            l_bolt = base_h + extra,
                                            r_head = bolt_head_r,
                                            l_head = bolt_head_l,
                                            support=0,
                                            fc_normal = self.axis_h,
                                            pos= self.get_pos_dwh(0,-2,0))#pos_bolt_4)
            else: # no head, just a cylinder:
                shp_bolt_1 = fcfun.shp_cylcenxtr (
                                            r = bolt_shank_r,
                                            h = base_h + extra,
                                            normal = self.axis_h,
                                            ch = 0,
                                            xtr_top=1, xtr_bot=1,
                                            pos = self.get_pos_dwh(3,0,0))#pos_bolt_1)
                shp_bolt_2 = fcfun.shp_cylcenxtr (
                                            r = bolt_shank_r,
                                            h = base_h + extra,
                                            normal = self.axis_h,
                                            ch = 0,
                                            xtr_top=1, xtr_bot=1,
                                            pos = self.get_pos_dwh(-3,0,0))#pos_bolt_2)
                shp_bolt_3 = fcfun.shp_cylcenxtr (
                                            r = bolt_shank_r,
                                            h = base_h + extra,
                                            normal = self.axis_h,
                                            ch = 0,
                                            xtr_top=1, xtr_bot=1,
                                            pos = self.get_pos_dwh(0,2,0))#pos_bolt_3)
                shp_bolt_4 = fcfun.shp_cylcenxtr (
                                            r = bolt_shank_r,
                                            h = base_h + extra,
                                            normal = self.axis_h,
                                            ch = 0,
                                            xtr_top=1, xtr_bot=1,
                                            pos = self.get_pos_dwh(0,-2,0))#pos_bolt_4)
                

            # fuse the bolts:
            shp_bolts = fcfun.fuseshplist([shp_bolt_1,
                                           shp_bolt_2,
                                           shp_bolt_3,
                                           shp_bolt_4])
            shp_base = shp_base.cut(shp_bolts)
        shp = fcfun.fuseshplist([shp_base, shp_clamp])

        #doc.recompute()
        shp = shp.removeSplitter()
        self.shp = shp

        self.wfco = wfco
        if wfco == 1:
            # a freeCAD object is created
            fco_clamp = doc.addObject("Part::Feature", name )
            fco_clamp.Shape = shp
            self.fco = fco_clamp